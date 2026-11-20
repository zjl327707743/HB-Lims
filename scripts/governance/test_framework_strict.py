"""Reject forged state and missing links in frozen planning snapshots."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
import check_framework as cf
from check_framework import ROOT, load, validate_controls, validate_backlog, validate_framework, validate_functions
from check_repository import read_requirements


class StrictPlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.urs = {r['urs_id'] for r in read_requirements(ROOT / 'docs/六车间QC实验室信息管理系统用户需求说明.docx')}

    def setUp(self):
        self.controls = load(ROOT, 'docs/standards/controls.json')
        self.backlog = load(ROOT, 'docs/delivery/backlog.json')
        self.framework = load(ROOT, 'docs/standards/framework.json')
        self.functions = load(ROOT, 'docs/requirements/function-scope.json')

    def test_row_level_forged_approval_rejected(self):
        self.controls['controls'][0].update(implementation='IMPLEMENTED', test_status='PASS', qa_approval='APPROVED')
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_unknown_control_root_field_rejected(self):
        self.controls['quality_release'] = 'APPROVED'
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_unknown_technology_field_rejected(self):
        self.controls['technology_extensions'][0]['validated'] = True
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_boolean_source_row_rejected(self):
        self.controls['controls'][0]['source_row'] = True
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_control_array_not_string(self):
        self.controls['controls'] = 'C01'
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_nonobject_control_rejected(self):
        self.controls['controls'][0] = None
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_all_mappings_cannot_be_emptied(self):
        for row in self.backlog['tasks']:
            for field in ('urs_ids', 'control_ids', 'function_ids', 'depends_on'):
                row[field] = []
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_each_original_mapping_protected(self):
        for field in ('urs_ids', 'control_ids', 'function_ids', 'depends_on'):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.backlog)
                row = next(x for x in candidate['tasks'] if x[field])
                row[field].pop()
                self.assertTrue(validate_backlog(candidate, self.urs))

    def test_original_empty_root_dependencies_remain_allowed(self):
        self.assertEqual([], self.backlog['tasks'][0]['depends_on'])
        self.assertEqual([], validate_backlog(self.backlog, self.urs))

    def test_unknown_task_field_rejected(self):
        self.backlog['tasks'][0]['qa_approval'] = 'APPROVED'
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_wrong_mapping_type_rejected(self):
        self.backlog['tasks'][0]['urs_ids'] = 'URS-105'
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_boolean_function_id_rejected(self):
        self.backlog['tasks'][0]['function_ids'][0] = True
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_duplicate_links_rejected(self):
        self.backlog['tasks'][0]['urs_ids'].append(self.backlog['tasks'][0]['urs_ids'][0])
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_future_qa_field_not_allowed_in_planning_framework(self):
        self.framework['qa_release'] = 'APPROVED'
        self.assertTrue(validate_framework(self.framework))

    def test_unknown_function_row_field_rejected(self):
        self.functions['rows'][0]['test_status'] = 'PASS'
        self.assertTrue(validate_functions(self.functions))

    def test_boolean_schema_rejected(self):
        self.framework['schema_version'] = True
        self.assertTrue(validate_framework(self.framework))

    def test_malformed_effort_rejected(self):
        self.functions['effort_values']['unit_confirmed'] = 'false'
        self.assertTrue(validate_functions(self.functions))

    def test_unknown_effort_field_rejected(self):
        self.functions['effort_values']['delivery_guaranteed'] = True
        self.assertTrue(validate_functions(self.functions))

    def test_wrong_template_root_overwrites_stale_green_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT, root, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git', '__pycache__', 'artifacts'))
            (root / 'docs/templates/VALIDATION_EVIDENCE.json').write_text('[]')
            out = root / 'artifacts/governance'; out.mkdir(parents=True, exist_ok=True)
            (out / 'framework-result.json').write_text('{"errors":[]}')
            with mock.patch.object(cf, 'ROOT', root), mock.patch('builtins.print'):
                self.assertEqual(1, cf.main())
            self.assertTrue(json.loads((out / 'framework-result.json').read_text())['errors'])

    def test_framework_input_symlink_loop_overwrites_stale_green_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / 'docs/standards'; src.mkdir(parents=True)
            path = src / 'framework.json'; path.symlink_to(path)
            out = root / 'artifacts/governance'; out.mkdir(parents=True)
            (out / 'framework-result.json').write_text('{"errors":[]}')
            with mock.patch.object(cf, 'ROOT', root), mock.patch('builtins.print'):
                self.assertEqual(1, cf.main())
            self.assertTrue(json.loads((out / 'framework-result.json').read_text())['errors'])


if __name__ == '__main__':
    unittest.main()
