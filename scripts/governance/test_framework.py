"""Regression tests for accepted planning; never evidence of application validation."""
import copy
import unittest
from check_framework import (ROOT, load, inspect, validate_framework, validate_controls,
                             validate_functions, validate_backlog)
from check_repository import read_requirements
from estimate_delivery import estimate


class FrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_framework = load(ROOT, 'docs/standards/framework.json')
        cls.raw_controls = load(ROOT, 'docs/standards/controls.json')
        cls.raw_functions = load(ROOT, 'docs/requirements/function-scope.json')
        cls.raw_backlog = load(ROOT, 'docs/delivery/backlog.json')
        cls.raw_model = load(ROOT, 'docs/delivery/capacity-model.json')
        cls.urs = {r['urs_id'] for r in read_requirements(ROOT / 'docs/六车间QC实验室信息管理系统用户需求说明.docx')}

    def setUp(self):
        self.fw = copy.deepcopy(self.raw_framework)
        self.controls = copy.deepcopy(self.raw_controls)
        self.functions = copy.deepcopy(self.raw_functions)
        self.backlog = copy.deepcopy(self.raw_backlog)
        self.model = copy.deepcopy(self.raw_model)

    def test_complete_framework(self):
        self.assertEqual([], inspect()['errors'])

    def test_fake_application_pass(self):
        self.fw['application_validation'] = 'PASS'
        self.assertTrue(validate_framework(self.fw))

    def test_fake_qa_approval(self):
        self.fw['qa_approval'] = 'APPROVED'
        self.assertTrue(validate_framework(self.fw))

    def test_fake_production_authorization(self):
        self.fw['production_release'] = 'AUTHORIZED'
        self.assertTrue(validate_framework(self.fw))

    def test_missing_required_document(self):
        self.fw['required_documents'].pop()
        self.assertTrue(validate_framework(self.fw))

    def test_missing_control(self):
        self.controls['controls'].pop()
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_duplicate_control(self):
        self.controls['controls'][-1] = copy.deepcopy(self.controls['controls'][0])
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_fake_control_implementation(self):
        self.controls['implementation'] = 'IMPLEMENTED'
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_control_source_row_changed(self):
        self.controls['controls'][0]['source_row'] = 99
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_technology_not_automatically_qualified(self):
        self.controls['technology_extensions'][2]['adoption'] = 'PRODUCTION_QUALIFIED'
        self.assertTrue(validate_controls(self.controls, ROOT))

    def test_missing_function(self):
        self.functions['rows'].pop()
        self.assertTrue(validate_functions(self.functions))

    def test_duplicate_function(self):
        self.functions['rows'][-1] = copy.deepcopy(self.functions['rows'][0])
        self.assertTrue(validate_functions(self.functions))

    def test_quantity_10_cannot_be_normalized_to_one(self):
        self.functions['rows'][25]['selected_raw'] = 1
        self.assertTrue(validate_functions(self.functions))

    def test_quantity_15_cannot_be_normalized_to_one(self):
        self.functions['rows'][26]['selected_raw'] = 1
        self.assertTrue(validate_functions(self.functions))

    def test_oos_mode_cannot_be_silently_changed(self):
        self.functions['rows'][4]['selected_raw'] = 0
        self.functions['rows'][5]['selected_raw'] = 1
        self.assertTrue(validate_functions(self.functions))

    def test_original_blank_title_preserved(self):
        self.functions['rows'][5]['source_title'] = 'invented original title'
        self.assertTrue(validate_functions(self.functions))

    def test_les_dependencies_preserved(self):
        self.functions['les_required_function_ids'].pop()
        self.assertTrue(validate_functions(self.functions))

    def test_unknown_effort_units_not_used(self):
        self.functions['effort_values']['used_for_delivery_estimate'] = True
        self.assertTrue(validate_functions(self.functions))

    def test_task_cycle_rejected(self):
        self.backlog['tasks'][0]['depends_on'] = ['B13']
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_unknown_task_dependency(self):
        self.backlog['tasks'][0]['depends_on'] = ['B99']
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_unknown_urs_reference(self):
        self.backlog['tasks'][0]['urs_ids'] = ['URS-9999']
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_unknown_control_reference(self):
        self.backlog['tasks'][0]['control_ids'] = ['C99']
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_planning_task_not_executed(self):
        self.backlog['tasks'][0]['status'] = 'PASS'
        self.assertTrue(validate_backlog(self.backlog, self.urs))

    def test_capacity_reproduces_accepted_ranges(self):
        result = estimate(self.model)
        self.assertEqual([750.0, 1100.0], result['full_effort_days'])
        self.assertEqual([9, 13], result['scenarios'][0]['pilot_months'])
        self.assertEqual([7, 9], result['scenarios'][1]['pilot_months'])
        self.assertEqual([27, 40], result['scenarios'][0]['full_scope_months_including_pilot'])
        self.assertEqual([19, 28], result['scenarios'][1]['full_scope_months_including_pilot'])

    def test_zero_capacity_rejected(self):
        self.model['effective_fraction'] = 0
        with self.assertRaises(ValueError):
            estimate(self.model)

    def test_pilot_cannot_be_added_twice(self):
        self.model['full_includes_pilot'] = False
        with self.assertRaises(ValueError):
            estimate(self.model)

    def test_bool_is_not_a_team_size(self):
        self.model['team_sizes'] = [True]
        with self.assertRaises(ValueError):
            estimate(self.model)

    def test_reversed_effort_range_rejected(self):
        self.model['pilot_effort_days'] = [320, 240]
        with self.assertRaises(ValueError):
            estimate(self.model)


if __name__ == '__main__':
    unittest.main()
