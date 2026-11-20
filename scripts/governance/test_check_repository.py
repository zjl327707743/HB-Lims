"""Regression tests for governance safeguards, not LIMS business tests."""
import copy
import unittest
from check_repository import ROOT, read_requirements, safe_csv, validate


class GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read_requirements(ROOT / 'docs/六车间QC实验室信息管理系统用户需求说明.docx')

    def setUp(self):
        self.index = [{k: r[k] for k in ('urs_id', 'source_table', 'source_row', 'source_category')} for r in self.source]
        self.tracking = {'defaults': {'implementation': 'NOT_IMPLEMENTED', 'test_status': 'NOT_RUN'}, 'overrides': {}}

    def check(self):
        return validate(self.index, self.source, self.tracking)

    def test_complete_baseline_is_valid(self):
        self.assertEqual([], self.check())

    def test_missing_requirement_rejected(self):
        self.index.pop()
        self.assertTrue(self.check())

    def test_duplicate_requirement_rejected(self):
        self.index[-1] = copy.deepcopy(self.index[0])
        self.assertTrue(self.check())

    def test_source_locator_change_rejected(self):
        self.index[0]['source_row'] = '999'
        self.assertTrue(self.check())

    def test_blank_category_cannot_be_silently_filled(self):
        next(r for r in self.index if r['urs_id'] == 'URS-1605')['source_category'] = 'Q'
        self.assertTrue(self.check())

    def test_unknown_override_rejected(self):
        self.tracking['overrides']['URS-9999'] = {'implementation': 'IN_PROGRESS'}
        self.assertTrue(self.check())

    def test_pass_without_evidence_rejected(self):
        self.tracking['overrides']['URS-100'] = {'implementation': 'IMPLEMENTED', 'test_status': 'PASS'}
        self.assertTrue(self.check())

    def test_global_pass_default_rejected(self):
        self.tracking['defaults']['test_status'] = 'PASS'
        self.assertTrue(self.check())

    def test_deferred_without_decision_rejected(self):
        self.tracking['overrides']['URS-100'] = {'implementation': 'DEFERRED'}
        self.assertTrue(self.check())

    def test_explicit_in_progress_allowed(self):
        self.tracking['overrides']['URS-100'] = {'implementation': 'IN_PROGRESS'}
        self.assertEqual([], self.check())

    def test_original_numbering_preserved(self):
        ids = {r['urs_id'] for r in self.source}
        self.assertIn('URS-1306', ids)
        self.assertNotIn('URS-1206', ids)

    def test_csv_formula_prefix_escaped(self):
        self.assertEqual("'=1+1", safe_csv('=1+1'))
        self.assertEqual('URS-100', safe_csv('URS-100'))


if __name__ == '__main__':
    unittest.main()
