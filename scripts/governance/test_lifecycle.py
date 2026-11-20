"""Target draft forgery, broken references and unsafe/stale lifecycle outputs."""
import copy
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import check_lifecycle as lc


class LifecyclePlanningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'checkout'
        self.plan = json.loads((lc.ROOT / lc.PLAN).read_text())
        paths = [lc.PLAN, lc.URS_INDEX, lc.DEV_REGISTER, self.plan['standard_ref'],
                 self.plan['source_register_ref'], 'scripts/governance/check_lifecycle.py',
                 'scripts/governance/check_evidence.py']
        paths += [row['path'] for row in self.plan['documents']]
        for relative in paths:
            dest = self.root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(lc.ROOT / relative, dest)

    def save(self, data=None, path=lc.PLAN):
        (self.root / path).write_text(json.dumps(self.plan if data is None else data,
                                               ensure_ascii=False), encoding='utf-8')

    def rejected(self, data):
        self.save(data)
        with self.assertRaises(lc.ERROR_TYPES):
            lc.validate(self.root)

    def cli(self):
        return subprocess.run([sys.executable, 'scripts/governance/check_lifecycle.py'],
                              cwd=self.root, capture_output=True, text=True, timeout=15)

    def test_initial_plan_exports_only_draft_facts(self):
        result = self.cli()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        out = self.root / 'artifacts/governance'
        report = json.loads((out / lc.RESULT).read_text())
        self.assertEqual([], report['errors'])
        self.assertEqual('NOT_RUN', report['application_validation'])
        self.assertEqual('NOT_GRANTED', report['qa_approval'])
        self.assertEqual('NOT_AUTHENTICATED_BY_THIS_CHECK', report['source_authenticity'])
        with (out / lc.EXPORT).open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(self.plan['risks']), len(rows))
        self.assertTrue(all(row['status'] == 'OPEN' and
                            row['residual_assessment'] == 'NOT_EVALUATED' for row in rows))

    def test_forged_execution_approval_and_risk_acceptance_rejected(self):
        cases = [([], 'implementation', 'IMPLEMENTED'),
                 ([], 'validation_execution', 'PASS'), ([], 'qa_approval', 'GRANTED'),
                 (['documents', 0], 'approval_ref', 'someone-approved'),
                 (['risks', 0], 'status', 'CLOSED'),
                 (['risks', 0], 'residual_assessment', 'LOW'),
                 (['risks', 0], 'residual_acceptance_ref', 'QA-123'),
                 (['verification_scenarios', 0], 'status', 'PASS'),
                 (['verification_scenarios', 0], 'evidence_ref', 'invented-run')]
        for path, field, value in cases:
            with self.subTest(path=path, field=field):
                data = copy.deepcopy(self.plan)
                row = data
                for key in path:
                    row = row[key]
                row[field] = value
                self.rejected(data)

    def test_unknown_fields_cannot_add_row_level_pseudo_approval(self):
        for path in ([], ['documents', 0], ['risks', 0], ['verification_scenarios', 0]):
            with self.subTest(path=path):
                data = copy.deepcopy(self.plan)
                row = data
                for key in path:
                    row = row[key]
                row['quality_release'] = 'APPROVED'
                self.rejected(data)

    def test_wrong_shapes_and_empty_required_collections_rejected(self):
        for key, value in [('schema_version', True), ('documents', []), ('risks', []),
                           ('verification_scenarios', []), ('lc_ids', 'LC-001')]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.plan); data[key] = value
                self.rejected(data)
        data = copy.deepcopy(self.plan); data['risks'][0] = []
        self.rejected(data)
        data = copy.deepcopy(self.plan); data['risks'][0]['planned_controls'] = ['']
        self.rejected(data)

    def test_unknown_urs_dev_lc_and_duplicate_links_rejected(self):
        for field, value in [('urs_ids', ['URS-99999']), ('dev_ids', ['DEV-999']),
                             ('lc_ids', ['LC-099']), ('urs_ids', ['URS-100', 'URS-100'])]:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(self.plan); data['risks'][0][field] = value
                self.rejected(data)
        for collection in ('documents', 'risks', 'verification_scenarios'):
            data = copy.deepcopy(self.plan)
            data[collection][1]['id'] = data[collection][0]['id']
            self.rejected(data)

    def test_dangling_or_one_way_risk_scenario_links_rejected(self):
        for collection, field, links in [('risks', 'scenario_ids', ['VS-999']),
                                          ('risks', 'scenario_ids', []),
                                          ('verification_scenarios', 'risk_ids', []),
                                          ('verification_scenarios', 'risk_ids', ['RISK-002'])]:
            with self.subTest(collection=collection, field=field, links=links):
                data = copy.deepcopy(self.plan); data[collection][0][field] = links
                self.rejected(data)

    def test_legitimate_many_to_many_extension_is_not_frozen_to_18_rows(self):
        data = copy.deepcopy(self.plan)
        extra_risk = copy.deepcopy(data['risks'][0]); extra_risk['id'] = 'RISK-019'
        extra_scene = copy.deepcopy(data['verification_scenarios'][0]); extra_scene['id'] = 'VS-019'
        extra_risk['scenario_ids'] = ['VS-001', 'VS-019']
        extra_scene['risk_ids'] = ['RISK-001', 'RISK-019']
        data['risks'][0]['scenario_ids'].append('VS-019')
        data['verification_scenarios'][0]['risk_ids'].append('RISK-019')
        data['risks'].append(extra_risk); data['verification_scenarios'].append(extra_scene)
        self.save(data)
        self.assertEqual(19, len(lc.validate(self.root)['risks']))

    def test_source_register_is_strict_but_does_not_need_private_pdfs(self):
        path = self.plan['source_register_ref']
        source = json.loads((self.root / path).read_text())
        for field, value in [('sha256', 'not-a-digest'), ('official_urls', ['file:///etc/passwd']),
                             ('coverage_summary', ''), ('id', 'S99'), ('qa_approval', 'APPROVED')]:
            with self.subTest(field=field):
                data = copy.deepcopy(source); data['sources'][0][field] = value
                self.save(data, path)
                with self.assertRaises(lc.ERROR_TYPES):
                    lc.validate(self.root)
        self.save(source, path)
        self.assertEqual(self.plan, lc.validate(self.root))
        self.assertFalse(any(self.root.rglob('*.pdf')))

    def test_missing_actual_lc_heading_cannot_be_replaced_by_fenced_example(self):
        path = self.root / self.plan['standard_ref']
        text = path.read_text()
        heading = next(h for h in text.splitlines() if h.startswith('## LC-012 '))
        path.write_text(text.replace(heading, '## Removed lifecycle section')
                        + '\n```markdown\n' + heading + '\n```\n')
        with self.assertRaises(lc.ERROR_TYPES):
            lc.validate(self.root)

    def test_specification_outline_and_draft_marker_are_required(self):
        row = next(d for d in self.plan['documents'] if d['id'] == 'DOC-SPEC')
        path = self.root / row['path']; original = path.read_text()
        for value in (original.replace('## 3. DS：', '## 3. Design：'),
                      original.replace('TEMPLATE_NOT_EXECUTED / NOT_APPROVED', 'APPROVED')):
            with self.subTest(value=value[:90]):
                path.write_text(value)
                with self.assertRaises(lc.ERROR_TYPES):
                    lc.validate(self.root)

    def test_core_document_missing_and_aliases_cannot_hide_gaps(self):
        data = copy.deepcopy(self.plan)
        data['documents'] = [d for d in data['documents'] if d['id'] != 'DOC-SIA']
        self.rejected(data)
        data = copy.deepcopy(self.plan); data['documents'][1]['path'] = data['documents'][0]['path']
        self.rejected(data)

    def test_hidden_or_example_draft_marker_cannot_mask_visible_approval(self):
        path = self.root / self.plan['documents'][0]['path']
        original = path.read_text()
        for extra in ('<!-- PLANNING_DRAFT_NOT_APPROVED -->',
                      '<!-- 状态：PLANNING_DRAFT_NOT_APPROVED -->',
                      '```markdown\n状态：PLANNING_DRAFT_NOT_APPROVED\n```'):
            with self.subTest(extra=extra):
                body = original.replace('**PLANNING_DRAFT_NOT_APPROVED**', '**APPROVED**')
                body = body.replace('\n## 1.', '\n' + extra + '\n## 1.', 1)
                path.write_text(body)
                self.assertNotEqual(0, self.cli().returncode)

    def test_csv_directory_does_not_preserve_old_success_json(self):
        out = self.root / 'artifacts/governance'; out.mkdir(parents=True)
        (out / lc.EXPORT).mkdir()
        sentinel = out / lc.EXPORT / 'do-not-recursively-delete'
        sentinel.write_text('keep')
        (out / lc.RESULT).write_text('{"errors":[],"old_success_marker":"OLD_SUCCESS"}')
        result = self.cli()
        self.assertNotEqual(0, result.returncode)
        report = json.loads((out / lc.RESULT).read_text())
        self.assertTrue(report['errors'])
        self.assertNotIn('old_success_marker', report)
        self.assertEqual('keep', sentinel.read_text())

    def test_malformed_inputs_and_path_attacks_remove_stale_success(self):
        # Each mutation exercises the real CLI, including cleanup on parse/path failure.
        for attack in ('invalid_json', 'duplicate_key', 'wrong_root', 'external_plan',
                       'external_register', 'external_document', 'symlink_loop'):
            with self.subTest(attack=attack):
                self.save()
                plan_path = self.root / lc.PLAN
                target = plan_path
                original = target.read_bytes()
                if attack == 'invalid_json': target.write_text('{')
                elif attack == 'duplicate_key':
                    target.write_text(target.read_text().replace('"schema_version": 1',
                                      '"schema_version": 1, "schema_version": 1', 1))
                elif attack == 'wrong_root': target.write_text('[]')
                else:
                    if attack == 'external_register': target = self.root / self.plan['source_register_ref']
                    if attack in ('external_document', 'symlink_loop'):
                        target = self.root / self.plan['documents'][0]['path']
                    original = target.read_bytes()
                    outside = Path(self.temp.name) / 'outside'; outside.write_bytes(original)
                    target.unlink(); target.symlink_to(target if attack == 'symlink_loop' else outside)
                out = self.root / 'artifacts/governance'; out.mkdir(parents=True, exist_ok=True)
                (out / lc.EXPORT).write_text('STALE SUCCESS')
                (out / lc.RESULT).write_text('{"errors":[]}')
                result = self.cli()
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertFalse((out / lc.EXPORT).exists())
                self.assertTrue(json.loads((out / lc.RESULT).read_text())['errors'])
                target.unlink(); target.write_bytes(original)

    def test_output_directory_cannot_escape_checkout(self):
        outside = Path(self.temp.name) / 'outside-output'; outside.mkdir()
        marker = outside / lc.RESULT; marker.write_text('DO NOT MODIFY')
        (self.root / 'artifacts').mkdir()
        (self.root / 'artifacts/governance').symlink_to(outside, target_is_directory=True)
        result = self.cli()
        self.assertNotEqual(0, result.returncode)
        self.assertEqual('DO NOT MODIFY', marker.read_text())
        self.assertFalse((outside / lc.EXPORT).exists())

    def test_csv_free_text_is_not_an_executable_spreadsheet_formula(self):
        self.plan['risks'][0]['title'] = '=1+1'
        self.save()
        self.assertEqual(0, self.cli().returncode)
        with (self.root / 'artifacts/governance' / lc.EXPORT).open(encoding='utf-8-sig', newline='') as handle:
            self.assertEqual("'=1+1", next(csv.DictReader(handle))['title'])


if __name__ == '__main__':
    unittest.main()
