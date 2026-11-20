"""R1 regression: a tracking status must never rewrite original URS fields."""
import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import check_repository as cr

class RtmAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = cr.read_requirements(cr.ROOT / 'docs/六车间QC实验室信息管理系统用户需求说明.docx')
        with (cr.ROOT / 'docs/requirements/urs-index.csv').open() as f:
            cls.index = list(csv.DictReader(f))
        cls.base = json.loads((cr.ROOT / 'docs/requirements/traceability.json').read_text())

    def setUp(self):
        self.t = copy.deepcopy(self.base)

    def test_each_authority_key_rejected_in_overrides(self):
        for key in cr.SOURCE_FIELDS:
            with self.subTest(key=key):
                t = copy.deepcopy(self.t)
                t['overrides']['URS-100'] = {key:'forged'}
                self.assertTrue(cr.validate(self.index, self.source, t))

    def test_each_authority_key_rejected_in_defaults(self):
        for key in cr.SOURCE_FIELDS:
            with self.subTest(key=key):
                t = copy.deepcopy(self.t); t['defaults'][key] = 'forged'
                self.assertTrue(cr.validate(self.index, self.source, t))

    def test_unknown_tracking_key_is_not_silently_ignored(self):
        self.t['overrides']['URS-100'] = {'evidence_reff':'misspelled'}
        self.assertTrue(cr.validate(self.index, self.source, self.t))

    def test_nontext_tracking_values_rejected(self):
        for value in (None, [], {}, 12, True):
            with self.subTest(value=value):
                t = copy.deepcopy(self.t);t['overrides']['URS-100']={'owner':value}
                self.assertTrue(cr.validate(self.index,self.source,t))

    def test_malformed_defaults_fail_closed(self):
        for value in (None, [], 'bad'):
            with self.subTest(value=value):
                t = copy.deepcopy(self.t);t['defaults']=value
                self.assertTrue(cr.validate(self.index,self.source,t))

    def test_malformed_status_does_not_crash(self):
        self.t['overrides']['URS-100']={'implementation':[]}
        self.assertTrue(cr.validate(self.index,self.source,self.t))

    def test_whitespace_not_evidence(self):
        self.t['overrides']['URS-100']={'implementation':'IMPLEMENTED','test_status':'PASS',
            'design_ref':' ','case_ref':' ','evidence_ref':' '}
        self.assertTrue(cr.validate(self.index,self.source,self.t))

    def test_whitespace_not_deferral_approval(self):
        self.t['overrides']['URS-100']={'implementation':'DEFERRED','decision_ref':'  '}
        self.assertTrue(cr.validate(self.index,self.source,self.t))

    def test_legitimate_status_update_preserves_all_source_columns(self):
        self.t['overrides']['URS-100']={'implementation':'IN_PROGRESS','owner':'synthetic-reviewer'}
        self.assertEqual([],cr.validate(self.index,self.source,self.t))
        for original, output in zip(self.source,cr.build_rtm_rows(self.source,self.t)):
            self.assertEqual({k:original[k] for k in cr.SOURCE_FIELDS},
                             {k:output[k] for k in cr.SOURCE_FIELDS})

    def test_builder_rejects_invalid_input(self):
        self.t['overrides']['URS-100']={'urs_id':'URS-9999'}
        with self.assertRaises(ValueError):cr.build_rtm_rows(self.source,self.t)

    def test_main_removes_stale_export_and_writes_errors(self):
        self.t['overrides']['URS-100']={'source_text':'FORGED'}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in cr.REQUIRED:
                f=root/rel; f.parent.mkdir(parents=True,exist_ok=True); f.write_text('placeholder')
            (root/'docs/sources/manifest.json').write_text(json.dumps({'urs_path':'synthetic.docx'}))
            req=root/'docs/requirements';req.mkdir(exist_ok=True)
            with (req/'urs-index.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(self.index[0]));writer.writeheader();writer.writerows(self.index)
            (req/'traceability.json').write_text(json.dumps(self.t))
            out=root/'artifacts/governance';out.mkdir(parents=True);(out/'requirements-rtm.csv').write_text('stale')
            with mock.patch.object(cr,'ROOT',root), mock.patch.object(cr,'read_requirements',return_value=self.source), mock.patch('builtins.print'):
                self.assertEqual(1,cr.main())
            self.assertFalse((out/'requirements-rtm.csv').exists())
            self.assertTrue(json.loads((out/'check-result.json').read_text())['errors'])

if __name__ == '__main__':unittest.main()
