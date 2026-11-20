"""Check draft lifecycle references/shape only, never execution or quality approval.

Schema v1 is an initial planning contract. Changing risk meaning, removing risks,
or revising this contract requires change review; this checker cannot judge those
decisions, authenticate source files/people, or prove an application control.
"""
from __future__ import annotations

import csv
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from check_evidence import exact, ids, repository_json, repository_path, text

ROOT = Path(__file__).resolve().parents[2]
PLAN = 'docs/validation/lifecycle/lifecycle-plan.json'
URS_INDEX = 'docs/requirements/urs-index.csv'
DEV_REGISTER = 'docs/standards/validation-readiness/constraints.json'
LC_IDS = {f'LC-{n:03d}' for n in range(1, 13)}
SOURCE_IDS = {f'S{n:02d}' for n in range(1, 11)} | {'S08-ZH'}
RESULT = 'lifecycle-check.json'
EXPORT = 'lifecycle-risks.csv'
ERROR_TYPES = (OSError, ValueError, TypeError, KeyError, RuntimeError,
               AttributeError, OverflowError, csv.Error)

PLAN_FIELDS = ('schema_version id kind assessed_on timezone baseline_source_head scope '
               'standard_ref source_register_ref implementation validation_execution '
               'qa_approval lc_ids documents risks verification_scenarios').split()
DOCUMENT_FIELDS = 'id kind path urs_ids lc_ids status approval_ref'.split()
RISK_FIELDS = ('id title urs_ids dev_ids lc_ids failure_effect initial_priority '
               'initial_rationale likelihood planned_controls scenario_ids status '
               'residual_assessment residual_acceptance_ref').split()
SCENARIO_FIELDS = ('id title urs_ids dev_ids lc_ids risk_ids acceptance_direction '
                   'acceptance_status status evidence_ref').split()
SOURCE_FIELDS = ('id title file_name sha256 legal_nature applicability verified_identity '
                 'version_status coverage_summary limitations official_urls adopted_topics').split()


def strings(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError('Expected nonempty text array: ' + label)
    for item in value:
        text(item, label)
    if len(set(value)) != len(value):
        raise ValueError('Duplicate text: ' + label)


def rows(value, fields, pattern, label):
    if not isinstance(value, list) or not value:
        raise ValueError('Expected nonempty collection: ' + label)
    result = {}
    for row in value:
        exact(row, fields, label)
        text(row['id'], label + '.id')
        if not re.fullmatch(pattern, row['id']) or row['id'] in result:
            raise ValueError('Invalid/duplicate ID: ' + label)
        result[row['id']] = row
    return result


def fixed(data, expected, label):
    for key, value in expected.items():
        if type(data[key]) is not type(value) or data[key] != value:
            raise ValueError('Draft-only state/identity required: ' + label + '.' + key)


def metadata(data, label):
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported schema version: ' + label)
    for key in ('id', 'scope', 'assessed_on', 'timezone'):
        text(data[key], label + '.' + key)
    if date.fromisoformat(data['assessed_on']).isoformat() != data['assessed_on']:
        raise ValueError('Expected ISO calendar date: ' + label)
    ZoneInfo(data['timezone'])


def markdown(root, relative):
    path = repository_path(root, relative)
    if path.suffix != '.md' or not path.is_file():
        raise ValueError('Missing Markdown document: ' + str(relative))
    value = path.read_text(encoding='utf-8')
    if not re.search(r'^# \S.+$', value, re.MULTILINE):
        raise ValueError('Missing document title: ' + relative)
    return value


def visible_lines(value):
    """Exclude comments/fenced examples from the document's own declarations."""
    value = re.sub(r'<!--.*?(?:-->|\Z)', '', value, flags=re.DOTALL)
    result = []
    fence = None
    for line in value.splitlines():
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence is not None:
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) +
                            '{' + str(len(fence)) + r',}[ \t]*', line):
                fence = None
            continue
        if match:
            fence = match.group(1)
            continue
        result.append(line)
    return result


def headings(value):
    return [line for line in visible_lines(value) if re.match(r'^##\s+\S', line)]


def draft_declaration(value, marker):
    # The first actual metadata declaration controls; an example/hidden token
    # cannot compensate for an APPROVED declaration. This is still a structure
    # check, not semantic review or authentication of an approval.
    for line in '\n'.join(visible_lines(value))[:1000].splitlines():
        match = re.match(r'^(?:状态|版本.*?状态)\s*[:：]\s*(.*)', line)
        if match:
            return re.match(r'(?:\*\*)?' + re.escape(marker) +
                            r'(?:\*\*)?\s*(?:[。；;]|$)', match.group(1)) is not None
    return False


def authorities(root):
    with repository_path(root, URS_INDEX).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != ['urs_id', 'source_table', 'source_row', 'source_category']:
            raise ValueError('Unexpected URS index header')
        urs = [row['urs_id'] for row in reader]
    if (len(urs) != 185 or len(set(urs)) != 185 or
            any(not isinstance(x, str) or not re.fullmatch(r'URS-\d+', x) for x in urs)):
        raise ValueError('Invalid 185-URS authority index')
    data = repository_json(root, DEV_REGISTER)
    if not isinstance(data, dict) or not isinstance(data.get('rules'), list):
        raise ValueError('Invalid DEV authority register')
    dev = []
    for row in data['rules']:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str):
            raise ValueError('Invalid DEV rule')
        dev.append(row['id'])
    if len(dev) != 28 or len(set(dev)) != 28:
        raise ValueError('Invalid 28-DEV authority register')
    return set(urs), set(dev)


def source_register(root, relative):
    data = repository_json(root, relative)
    exact(data, 'schema_version id assessed_on timezone scope sources'.split(), 'source register')
    metadata(data, 'source register')
    sources = rows(data['sources'], SOURCE_FIELDS, r'S\d{2}(?:-ZH)?', 'sources')
    if set(sources) != SOURCE_IDS:
        raise ValueError('Source register must identify the 11 supplied references')
    for row in sources.values():
        for key in set(SOURCE_FIELDS) - {'limitations', 'official_urls', 'adopted_topics'}:
            text(row[key], row['id'] + '.' + key)
        if not re.fullmatch(r'[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid declared source SHA-256: ' + row['id'])
        for key in ('limitations', 'official_urls', 'adopted_topics'):
            strings(row[key], row['id'] + '.' + key)
        for url in row['official_urls']:
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError('Invalid official URL shape: ' + row['id'])
    # No source PDF is required in the public checkout; these are declared
    # identities/locators, not authentication of originals or legal conclusions.
    return sources


def validate(root):
    data = repository_json(root, PLAN)
    exact(data, PLAN_FIELDS, 'lifecycle plan')
    metadata(data, 'lifecycle plan')
    fixed(data, {'kind': 'PLANNING_DRAFT_NOT_APPROVED',
                 'implementation': 'NOT_IMPLEMENTED', 'validation_execution': 'NOT_RUN',
                 'qa_approval': 'NOT_GRANTED'}, 'lifecycle plan')
    text(data['baseline_source_head'], 'baseline_source_head')
    if not re.fullmatch(r'[0-9a-f]{40}', data['baseline_source_head']):
        raise ValueError('Baseline needs full source commit')
    ids(data['lc_ids'], LC_IDS, 'plan.lc_ids')
    if set(data['lc_ids']) != LC_IDS:
        raise ValueError('Plan must retain all 12 LC references')
    standard = markdown(root, data['standard_ref'])
    actual = [m.group(1) for h in headings(standard)
              if (m := re.fullmatch(r'##\s+(LC-\d{3})\s+\S.*', h))]
    if set(actual) != LC_IDS or len(actual) != len(LC_IDS):
        raise ValueError('LC IDs need unique nonempty headings in standard_ref')
    source_register(root, data['source_register_ref'])
    urs, dev = authorities(root)

    documents = rows(data['documents'], DOCUMENT_FIELDS, r'DOC-[A-Z][A-Z0-9-]*', 'documents')
    if not {'DOC-SIA', 'DOC-VP', 'DOC-SPEC'}.issubset(documents):
        raise ValueError('Document index needs SIA, VP and domain specification')
    paths = set()
    for row in documents.values():
        if row['kind'] not in ('PROJECT_DRAFT', 'UNEXECUTED_TEMPLATE'):
            raise ValueError('Unknown document kind: ' + row['id'])
        fixed(row, {'status': 'DRAFT_NOT_APPROVED', 'approval_ref': None}, row['id'])
        ids(row['urs_ids'], urs, row['id'] + '.urs_ids')
        ids(row['lc_ids'], LC_IDS, row['id'] + '.lc_ids')
        body = markdown(root, row['path'])
        path = repository_path(root, row['path'])
        if path in paths:
            raise ValueError('Different document IDs point to the same file')
        paths.add(path)
        marker = ('PLANNING_DRAFT_NOT_APPROVED' if row['kind'] == 'PROJECT_DRAFT'
                  else 'TEMPLATE_NOT_EXECUTED / NOT_APPROVED')
        if not draft_declaration(body, marker):
            raise ValueError('Document does not declare its draft/template status: ' + row['id'])
        if row['id'] in ('DOC-SIA', 'DOC-VP') and row['kind'] != 'PROJECT_DRAFT':
            raise ValueError('SIA/VP entries must reference project drafts')
        if row['id'] == 'DOC-SPEC':
            outline = headings(body)
            if not all(any(re.search(r'\b' + key + r'\b', h) for h in outline)
                       for key in ('FS', 'DS', 'CS')):
                raise ValueError('Specification template requires FS, DS and CS headings')

    risks = rows(data['risks'], RISK_FIELDS, r'RISK-\d{3,}', 'risks')
    scenes = rows(data['verification_scenarios'], SCENARIO_FIELDS, r'VS-\d{3,}', 'scenarios')
    for row in list(risks.values()) + list(scenes.values()):
        text(row['title'], row['id'] + '.title')
        ids(row['urs_ids'], urs, row['id'] + '.urs_ids')
        ids(row['dev_ids'], dev, row['id'] + '.dev_ids')
        ids(row['lc_ids'], LC_IDS, row['id'] + '.lc_ids')
    for row in risks.values():
        fixed(row, {'status': 'OPEN', 'likelihood': 'NOT_ESTIMATED',
                    'residual_assessment': 'NOT_EVALUATED', 'residual_acceptance_ref': None}, row['id'])
        for key in ('failure_effect', 'initial_rationale'):
            text(row[key], row['id'] + '.' + key)
        if row['initial_priority'] not in ('HIGH', 'MEDIUM', 'LOW'):
            raise ValueError('Invalid initial planning priority: ' + row['id'])
        strings(row['planned_controls'], row['id'] + '.planned_controls')
        ids(row['scenario_ids'], set(scenes), row['id'] + '.scenario_ids')
    for row in scenes.values():
        fixed(row, {'status': 'NOT_RUN', 'evidence_ref': None,
                    'acceptance_status': 'DRAFT_REQUIRES_DOMAIN_SPECIFICATION_AND_APPROVAL'}, row['id'])
        text(row['acceptance_direction'], row['id'] + '.acceptance_direction')
        ids(row['risk_ids'], set(risks), row['id'] + '.risk_ids')
    for risk in risks.values():
        for sid in risk['scenario_ids']:
            if risk['id'] not in scenes[sid]['risk_ids']:
                raise ValueError('Missing reverse scenario/risk link: ' + risk['id'] + '/' + sid)
    for scene in scenes.values():
        for rid in scene['risk_ids']:
            if scene['id'] not in risks[rid]['scenario_ids']:
                raise ValueError('Missing reverse risk/scenario link: ' + scene['id'] + '/' + rid)
    return data


def cell(value):
    value = ' | '.join(value) if isinstance(value, list) else str(value)
    # Exported free text must not become a spreadsheet formula when opened.
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def main():
    errors, data, out = [], None, None
    result = {'kind': 'LIFECYCLE_PLANNING_STRUCTURE_CHECK',
              'scope': 'References, draft states and minimum document structure only.',
              'application_validation': 'NOT_RUN', 'qa_approval': 'NOT_GRANTED',
              'source_authenticity': 'NOT_AUTHENTICATED_BY_THIS_CHECK',
              'risk_acceptance': 'NOT_ASSESSED_BY_THIS_CHECK', 'errors': errors}
    try:
        # Validate the parent before unlinking final entries. Unlink removes an
        # output symlink itself and never follows it to an external destination.
        out = repository_path(ROOT, 'artifacts/governance')
        out.mkdir(parents=True, exist_ok=True)
        for name in (EXPORT, RESULT):
            try:
                (out / name).unlink(missing_ok=True)
            except ERROR_TYPES as exc:
                errors.append('Cannot remove old lifecycle output ' + name + ': ' + str(exc))
        if errors:
            raise ValueError('Old lifecycle output cleanup failed; evaluation was not performed')
        data = validate(ROOT)
        fields = ('id', 'title', 'urs_ids', 'dev_ids', 'lc_ids', 'initial_priority',
                  'scenario_ids', 'status', 'residual_assessment')
        with (out / EXPORT).open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(('planning_kind', 'baseline_source_head') + fields)
            for row in data['risks']:
                writer.writerow([cell(data['kind']), cell(data['baseline_source_head'])]
                                + [cell(row[key]) for key in fields])
        result['counts'] = {key: len(data[key]) for key in
                            ('lc_ids', 'documents', 'risks', 'verification_scenarios')}
    except ERROR_TYPES as exc:
        errors.append('Lifecycle planning check failed: ' + str(exc))
    if out is not None:
        if errors:
            try:
                (out / EXPORT).unlink(missing_ok=True)
            except ERROR_TYPES as exc:
                errors.append('Cannot remove failed lifecycle export: ' + str(exc))
        try:
            (out / RESULT).unlink(missing_ok=True)
            (out / RESULT).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',
                                      encoding='utf-8')
        except ERROR_TYPES as exc:
            errors.append('Cannot write lifecycle check result: ' + str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
