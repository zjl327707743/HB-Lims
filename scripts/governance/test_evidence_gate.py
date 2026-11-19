"""Engineering metadata integrity tests with synthetic files; not LIMS validation."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import check_repository as cr
from check_evidence import KIND, REGISTRY, check_tracking_references


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.urs = {'URS-100', 'URS-101'}
        self.as_of = datetime(2026, 11, 20, tzinfo=timezone.utc)
        self.extra_runs = []
        self.target = {'source_commit': 'a' * 40,
                       'artifact_digests': {'api': 'sha256:' + 'b' * 64},
                       'config_digest': 'sha256:' + 'c' * 64}
        self.run = {'kind': 'ENGINEERING_TEST_EXECUTION', 'evidence_id': 'E-1', 'urs_ids': ['URS-100'],
                    'design_ref': 'D-1', 'case_ref': 'T-1', 'owner': 'synthetic-owner',
                    'executor': 'synthetic-executor', 'executed_at': '2026-11-19T08:00:00+08:00',
                    'target': copy.deepcopy(self.target), 'result': 'PASS',
                    'raw_evidence': [self.file('fixtures/raw.log', 'SYNTHETIC test output\n')],
                    'retest_of': [], 'retest_disposition': None}
        self.data = {'schema_version': 1, 'kind': KIND, 'target': self.target, 'scope_id': 'synthetic-pilot',
                     'designs': [{'id': 'D-1', 'urs_ids': ['URS-100'], 'artifact': self.file('fixtures/design.md', 'Synthetic design')}],
                     'cases': [{'id': 'T-1', 'urs_ids': ['URS-100'], 'design_ref': 'D-1',
                                'artifact': self.file('fixtures/case.md', 'Synthetic expected rejection')}],
                     'executions': [], 'scope_decisions': []}
        self.run['design_sha256'] = self.data['designs'][0]['artifact']['sha256']
        self.run['case_sha256'] = self.data['cases'][0]['artifact']['sha256']
        self.tracking = {'defaults': {'implementation': 'NOT_IMPLEMENTED', 'test_status': 'NOT_RUN'},
                         'overrides': {'URS-100': {'implementation': 'IMPLEMENTED', 'test_status': 'PASS',
                              'owner': 'synthetic-owner', 'design_ref': 'D-1', 'case_ref': 'T-1', 'evidence_ref': 'E-1'}}}

    def file(self, rel, content, classification='SYNTHETIC'):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        return {'path': rel, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'classification': classification}

    def check(self):
        self.data['executions'] = [{'id': 'E-1', 'urs_ids': ['URS-100'],
             'artifact': self.file('fixtures/run.json', json.dumps(self.run))}]
        for prior in self.extra_runs:
            self.data['executions'].append({'id': prior['evidence_id'], 'urs_ids': prior['urs_ids'],
                'artifact': self.file('fixtures/' + prior['evidence_id'] + '.json', json.dumps(prior))})
        self.file(REGISTRY, json.dumps(self.data))
        return cr.validate_tracking(self.tracking, self.urs, self.root, self.as_of)

    def test_valid_synthetic_engineering_evidence(self):
        self.assertEqual([], self.check())

    def test_nonexistent_references_rejected(self):
        self.tracking['overrides']['URS-100'].update(design_ref='DOES_NOT_EXIST', case_ref='DOES_NOT_EXIST', evidence_ref='DOES_NOT_EXIST')
        self.assertTrue(self.check())

    def test_wrong_urs_rejected(self):
        self.tracking['overrides']['URS-101'] = self.tracking['overrides'].pop('URS-100')
        self.assertTrue(self.check())

    def test_unassigned_owner_rejected(self):
        self.tracking['overrides']['URS-100']['owner'] = 'UNASSIGNED'
        self.assertTrue(self.check())

    def test_wrong_owner_rejected(self):
        self.tracking['overrides']['URS-100']['owner'] = 'other-person'
        self.assertTrue(self.check())

    def test_failed_execution_cannot_be_pass(self):
        self.run['result'] = 'FAIL'
        self.assertTrue(self.check())

    def test_wrong_commit_rejected(self):
        self.run['target']['source_commit'] = 'd' * 40
        self.assertTrue(self.check())

    def test_wrong_artifact_rejected(self):
        self.run['target']['artifact_digests']['api'] = 'sha256:' + 'd' * 64
        self.assertTrue(self.check())

    def test_wrong_config_rejected(self):
        self.run['target']['config_digest'] = 'sha256:' + 'd' * 64
        self.assertTrue(self.check())

    def test_changed_raw_bytes_rejected(self):
        (self.root / 'fixtures/raw.log').write_text('changed')
        self.assertTrue(self.check())

    def test_empty_raw_evidence_rejected(self):
        self.run['raw_evidence'] = []
        self.assertTrue(self.check())

    def test_external_evidence_blocks_current_gate(self):
        self.run['raw_evidence'][0]['path'] = 'controlled://quality/evidence/one'
        self.assertTrue(self.check())

    def test_path_escape_rejected(self):
        self.run['raw_evidence'][0]['path'] = '../outside.log'
        self.assertTrue(self.check())

    def test_real_quality_data_classification_rejected(self):
        self.run['raw_evidence'][0]['classification'] = 'REAL_QUALITY_DATA'
        self.assertTrue(self.check())

    def test_wrong_case_rejected(self):
        self.run['case_ref'] = 'T-MISSING'
        self.assertTrue(self.check())

    def test_qa_status_in_engineering_record_rejected(self):
        self.run['qa_approval'] = 'APPROVED'
        self.assertTrue(self.check())

    def test_unzoned_time_rejected(self):
        self.run['executed_at'] = '2026-11-19T08:00:00'
        self.assertTrue(self.check())

    def test_duplicate_registry_id_rejected(self):
        self.data['designs'].append(copy.deepcopy(self.data['designs'][0]))
        self.assertTrue(self.check())

    def test_unknown_registry_field_rejected(self):
        self.data['qa_release'] = 'APPROVED'
        self.assertTrue(self.check())

    def test_missing_registry_rejected(self):
        self.assertTrue(check_tracking_references(self.tracking, self.urs, self.root))

    def test_duplicate_json_key_rejected(self):
        self.file(REGISTRY, '{"schema_version":1,"schema_version":1}')
        self.assertTrue(check_tracking_references(self.tracking, self.urs, self.root))

    def defer(self):
        self.tracking['overrides']['URS-100'] = {'implementation': 'DEFERRED', 'owner': 'synthetic-owner', 'decision_ref': 'DEC-1'}

    def decision(self, **overrides):
        record = {'kind': 'REDACTED_SCOPE_DECISION', 'decision_id': 'DEC-1', 'urs_ids': ['URS-100'],
                  'scope': 'synthetic-pilot', 'decision': 'DEFERRED', 'status': 'APPROVED',
                  'approved_by': 'synthetic-qa-fixture', 'approved_at': '2026-11-19T08:00:00+08:00',
                  'valid_until': None, 'no_expiry_reason': 'Fixture scope remains until controlled replacement',
                  'revoked': False,
                  'controlled_record_locator': 'controlled://synthetic-fixture-only/DEC-1'}
        record.update(overrides)
        self.data['scope_decisions'] = [{'id': 'DEC-1', 'urs_ids': ['URS-100'],
            'artifact': self.file('fixtures/decision.json', json.dumps(record), 'APPROVED_REDACTED')}]

    def test_nonexistent_deferral_rejected(self):
        self.defer()
        self.assertTrue(self.check())

    def test_structurally_consistent_redacted_decision(self):
        # This only tests metadata consistency; these fake fixture identities never
        # become a real approved decision or get added to the repository registry.
        self.defer(); self.decision()
        self.assertEqual([], self.check())

    def test_unapproved_deferral_rejected(self):
        self.defer(); self.decision(status='PENDING')
        self.assertTrue(self.check())

    def test_wrong_scope_deferral_rejected(self):
        self.defer(); self.decision(scope='other-pilot')
        self.assertTrue(self.check())

    def test_synthetic_approval_not_public_approval_record(self):
        self.defer(); self.decision()
        self.data['scope_decisions'][0]['artifact']['classification'] = 'SYNTHETIC'
        self.assertTrue(self.check())

    def test_design_changed_and_rehashed_does_not_rewrite_old_run(self):
        self.data['designs'][0]['artifact'] = self.file('fixtures/design.md', 'Changed synthetic design')
        self.assertTrue(self.check())

    def test_case_changed_and_rehashed_does_not_rewrite_old_run(self):
        self.data['cases'][0]['artifact'] = self.file('fixtures/case.md', 'Changed synthetic expected result')
        self.assertTrue(self.check())

    def test_future_execution_rejected(self):
        self.run['executed_at'] = '2099-01-01T00:00:00Z'
        self.assertTrue(self.check())

    def test_future_scope_approval_rejected(self):
        self.defer(); self.decision(approved_at='2099-01-01T00:00:00Z')
        self.assertTrue(self.check())

    def test_expired_scope_approval_rejected(self):
        self.defer(); self.decision(valid_until='2026-11-19T23:59:59Z', no_expiry_reason=None)
        self.assertTrue(self.check())

    def test_validity_end_is_exclusive(self):
        self.defer(); self.decision(valid_until=self.as_of.isoformat(), no_expiry_reason=None)
        self.assertTrue(self.check())

    def test_valid_dated_scope_approval(self):
        self.defer(); self.decision(valid_until='2027-01-01T00:00:00Z', no_expiry_reason=None)
        self.assertEqual([], self.check())

    def test_no_expiry_requires_reason(self):
        self.defer(); self.decision(no_expiry_reason='')
        self.assertTrue(self.check())

    def test_revoked_approval_rejected(self):
        self.defer(); self.decision(status='REVOKED', revoked=True)
        self.assertTrue(self.check())

    def test_revoked_history_is_retained_when_not_selected(self):
        self.decision(status='REVOKED', revoked=True)
        self.assertEqual([], self.check())

    def test_naive_evaluation_time_rejected(self):
        self.as_of = datetime(2026, 11, 20)
        self.assertTrue(self.check())

    def previous(self, result='FAIL', executed_at='2026-11-18T08:00:00+08:00', evidence_id='E-0'):
        prior = copy.deepcopy(self.run)
        prior.update(evidence_id=evidence_id, result=result, executed_at=executed_at,
                     retest_of=[], retest_disposition=None)
        self.extra_runs.append(prior)
        return prior

    def retest_disposition(self, related=None, **overrides):
        related = related or ['E-0']
        self.run['retest_of'] = related
        disposition = {'kind': 'ENGINEERING_RETEST_DISPOSITION', 'disposition_id': 'ERD-1',
                       'related_execution_ids': related, 'retest_execution_id': 'E-1',
                       'reason': 'Synthetic fixture failure investigated; repeat execution reviewed',
                       'reviewer': 'synthetic-other-reviewer', 'reviewed_at': '2026-11-19T10:00:00+08:00'}
        disposition.update(overrides)
        self.run['retest_disposition'] = self.file('fixtures/retest.json', json.dumps(disposition))

    def test_later_failure_cannot_be_hidden_by_selecting_old_pass(self):
        self.previous(executed_at='2026-11-19T09:00:00+08:00')
        self.assertTrue(self.check())

    def test_later_blocked_cannot_be_hidden_by_selecting_old_pass(self):
        self.previous(result='BLOCKED', executed_at='2026-11-19T09:00:00+08:00')
        self.assertTrue(self.check())

    def test_simultaneous_failure_in_different_timezone_is_ambiguous(self):
        self.previous(executed_at='2026-11-19T00:00:00Z')
        self.assertTrue(self.check())

    def test_prior_failure_needs_explicit_retest_disposition(self):
        self.previous()
        self.assertTrue(self.check())

    def test_valid_engineering_retest_preserves_failure_history(self):
        self.previous(); self.retest_disposition()
        self.assertEqual([], self.check())
        self.assertEqual('FAIL', self.extra_runs[0]['result'])
        self.assertEqual(2, len(self.data['executions']))

    def test_retest_missing_original_failure_is_rejected(self):
        self.retest_disposition()
        self.assertTrue(self.check())

    def test_retest_must_account_for_each_same_target_failure(self):
        self.previous(); self.previous(evidence_id='E-00')
        self.retest_disposition()
        self.assertTrue(self.check())

    def test_retest_review_cannot_be_self_declared_by_executor(self):
        self.previous(); self.retest_disposition(reviewer='synthetic-executor')
        self.assertTrue(self.check())

    def test_future_retest_review_is_rejected(self):
        self.previous(); self.retest_disposition(reviewed_at='2099-01-01T00:00:00Z')
        self.assertTrue(self.check())

    def test_historical_other_target_failure_does_not_rewrite_current_result(self):
        prior = self.previous(); prior['target']['source_commit'] = 'd' * 40
        self.assertEqual([], self.check())

    def test_registry_symlink_escape_rejected(self):
        self.assertEqual([], self.check())
        registry = self.root / REGISTRY
        with tempfile.TemporaryDirectory() as outside:
            other = Path(outside) / 'registry.json'; other.write_bytes(registry.read_bytes())
            registry.unlink(); registry.symlink_to(other)
            self.assertTrue(check_tracking_references(self.tracking, self.urs, self.root, self.as_of))

    def test_raw_symlink_loop_is_reported_as_error(self):
        raw = self.root / 'fixtures/raw.log'
        raw.unlink(); raw.symlink_to(raw)
        self.assertTrue(self.check())

    def test_raw_symlink_loop_replaces_stale_green_main_report(self):
        shutil.copytree(cr.ROOT, self.root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', 'artifacts'))
        raw = self.root / 'fixtures/raw.log'
        raw.unlink(); raw.symlink_to(raw)
        self.run['executed_at'] = '2020-01-01T00:00:00Z'
        self.assertTrue(self.check())
        self.file('docs/requirements/traceability.json', json.dumps(self.tracking))
        out = self.root / 'artifacts/governance'; out.mkdir(parents=True, exist_ok=True)
        (out / 'requirements-rtm.csv').write_text('STALE PASS')
        (out / 'check-result.json').write_text('{"errors":[]}')
        with mock.patch.object(cr, 'ROOT', self.root), mock.patch('builtins.print'):
            self.assertEqual(1, cr.main())
        self.assertFalse((out / 'requirements-rtm.csv').exists())
        self.assertTrue(json.loads((out / 'check-result.json').read_text())['errors'])


class FailedExportTests(unittest.TestCase):
    def test_manifest_symlink_escape_replaces_stale_green_report(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp); src = root / 'docs/sources'; src.mkdir(parents=True)
            other = Path(outside) / 'manifest.json'; other.write_text('{"urs_path":"fake.docx"}')
            (src / 'manifest.json').symlink_to(other)
            out = root / 'artifacts/governance'; out.mkdir(parents=True)
            (out / 'check-result.json').write_text('{"errors":[]}')
            with mock.patch.object(cr, 'ROOT', root), mock.patch('builtins.print'):
                self.assertEqual(1, cr.main())
            self.assertTrue(json.loads((out / 'check-result.json').read_text())['errors'])

    def test_bad_json_clears_previous_rtm_and_reports_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / 'docs/sources'; src.mkdir(parents=True)
            (src / 'manifest.json').write_text('{ invalid json')
            out = root / 'artifacts/governance'; out.mkdir(parents=True)
            (out / 'requirements-rtm.csv').write_text('STALE PASS')
            with mock.patch.object(cr, 'ROOT', root), mock.patch('builtins.print'):
                self.assertEqual(1, cr.main())
            self.assertFalse((out / 'requirements-rtm.csv').exists())
            self.assertTrue(json.loads((out / 'check-result.json').read_text())['errors'])

    def test_missing_input_clears_previous_rtm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'artifacts/governance'; out.mkdir(parents=True)
            (out / 'requirements-rtm.csv').write_text('STALE PASS')
            with mock.patch.object(cr, 'ROOT', root), mock.patch('builtins.print'):
                self.assertEqual(1, cr.main())
            self.assertFalse((out / 'requirements-rtm.csv').exists())


if __name__ == '__main__':
    unittest.main()
