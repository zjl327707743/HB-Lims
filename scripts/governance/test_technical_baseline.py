"""Negative and positive tests for specification integrity, not LIMS behavior."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from check_technical_baseline import (
    ROOT, ACTIVE, ARCHIVE, validate_archive, validate_preserved,
    validate_selection, check_relative_links, inspect,
)


class TechnicalBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / 'docs/standards/baseline.json').read_text(encoding='utf-8'))
        cls.original_bytes = (ROOT / ARCHIVE).read_bytes()
        cls.old = cls.original_bytes.decode('utf-8')
        cls.new = (ROOT / ACTIVE).read_text(encoding='utf-8')

    def setUp(self):
        self.baseline = copy.deepcopy(self.config)

    def test_selected_stack_valid(self):
        self.assertEqual([], validate_selection(self.baseline))

    def test_backend_drift_rejected(self):
        self.baseline['selected']['backend'] = 'Django'
        self.assertTrue(validate_selection(self.baseline))

    def test_queue_drift_rejected(self):
        self.baseline['selected']['queue'] = 'ARQ'
        self.assertTrue(validate_selection(self.baseline))

    def test_unqualified_storage_rejected(self):
        self.baseline['production_storage_product'] = 'MinIO Community'
        self.assertTrue(validate_selection(self.baseline))

    def test_fake_application_pass_rejected(self):
        self.baseline['application_validation'] = 'PASS'
        self.assertTrue(validate_selection(self.baseline))

    def test_fake_visual_pass_rejected(self):
        self.baseline['visual_validation'] = 'PASS'
        self.assertTrue(validate_selection(self.baseline))

    def test_fake_qa_approval_rejected(self):
        self.baseline['qa_approval'] = 'APPROVED'
        self.assertTrue(validate_selection(self.baseline))

    def test_required_document_omission_rejected(self):
        self.baseline['required_documents'].pop()
        self.assertTrue(validate_selection(self.baseline))

    def test_frozen_archive_valid(self):
        self.assertEqual([], validate_archive(self.original_bytes))

    def test_archive_tampering_rejected(self):
        self.assertTrue(validate_archive(self.original_bytes + b'changed'))

    def test_all_three_sections_preserved(self):
        self.assertEqual([], validate_preserved(self.old, self.new))

    def test_visual_clause_change_rejected(self):
        changed = self.new.replace('紫色主操作', '蓝色主操作')
        self.assertNotEqual(self.new, changed)
        self.assertTrue(validate_preserved(self.old, changed))

    def test_business_clause_change_rejected(self):
        changed = self.new.replace('两名不同人员确认', '一名人员确认')
        self.assertNotEqual(self.new, changed)
        self.assertTrue(validate_preserved(self.old, changed))

    def test_acceptance_omission_rejected(self):
        self.assertTrue(validate_preserved(self.old, self.new.split('## 验收')[0]))

    def test_engineering_addition_allowed(self):
        self.assertEqual([], validate_preserved(self.old, self.new + '\n## 工程补充测试\n仅技术文本。\n'))

    def test_missing_relative_link_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'README.md'
            page.write_text('[missing](missing.md)', encoding='utf-8')
            self.assertTrue(check_relative_links(root, [page]))

    def test_existing_relative_link_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'README.md'
            page.write_text('[existing](target.md)', encoding='utf-8')
            (root / 'target.md').write_text('ok', encoding='utf-8')
            self.assertEqual([], check_relative_links(root, [page]))

    def test_whole_repository_structure(self):
        self.assertEqual([], inspect()['errors'])


if __name__ == '__main__':
    unittest.main()
