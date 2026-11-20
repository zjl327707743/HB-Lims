"""Repository governance checks, not application or GMP validation (stdlib only)."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from check_evidence import check_tracking_references, repository_json, repository_path, evaluation_time

ROOT = Path(__file__).resolve().parents[2]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
REQUIRED = ('README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'SECURITY.md',
    '.github/CODEOWNERS', '.github/pull_request_template.md',
    'docs/START_HERE.md', 'docs/sources/manifest.json',
    'docs/review/2026-11-16-source-review.md',
    'docs/research/competitive-landscape.md',
    'docs/architecture/adr/0001-independent-modular-monolith.md',
    'docs/governance/github-settings-checklist.md',
    'docs/validation/README.md', 'docs/delivery/ROADMAP.md',
    'apps/web/README.md', 'apps/api/README.md', 'packages/contracts/README.md',
    'tests/README.md', 'deploy/README.md')
IMPLEMENTATION = {'NOT_IMPLEMENTED', 'IN_PROGRESS', 'IMPLEMENTED', 'BLOCKED', 'DEFERRED'}
TEST = {'NOT_RUN', 'PASS', 'FAIL', 'BLOCKED'}
# Only these development-status fields may be changed outside the original URS.
TRACKING_FIELDS = frozenset({'implementation', 'test_status', 'owner',
    'design_ref', 'case_ref', 'evidence_ref', 'decision_ref'})
SOURCE_FIELDS = ('urs_id', 'original_id', 'source_table', 'source_row',
    'source_category', 'source_group', 'source_text')


def validate_tracking(tracking: dict, source_ids: set[str], root: Path | None = None, as_of=None) -> list[str]:
    """Reject authority-field injection in defaults and per-URS overrides."""
    if not isinstance(tracking, dict):
        return ['Traceability must be an object']
    defaults = tracking.get('defaults', {})
    overrides = tracking.get('overrides', {})
    if not isinstance(defaults, dict) or not isinstance(overrides, dict):
        return ['Defaults and overrides must be objects']
    errors = []
    if set(tracking) - {'schema_version', 'scope', 'defaults', 'overrides'}:
        errors.append('Unknown traceability top-level fields')
    if 'schema_version' in tracking and (type(tracking['schema_version']) is not int or tracking['schema_version'] != 1):
        errors.append('Unsupported traceability schema')
    if 'scope' in tracking and not isinstance(tracking['scope'], str):
        errors.append('Traceability scope must be text')

    def check_entry(entry: dict, location: str) -> None:
        unexpected = set(entry) - TRACKING_FIELDS
        if unexpected:
            errors.append(f'Forbidden traceability fields at {location}: {sorted(unexpected)}')
        for field, value in entry.items():
            if field in TRACKING_FIELDS and not isinstance(value, str):
                errors.append(f'Tracking value must be text: {location}.{field}')

    check_entry(defaults, 'defaults')
    if defaults.get('implementation') != 'NOT_IMPLEMENTED' or defaults.get('test_status') != 'NOT_RUN':
        errors.append('Defaults must remain NOT_IMPLEMENTED / NOT_RUN')
    for rid, entry in overrides.items():
        if rid not in source_ids or not isinstance(entry, dict):
            errors.append(f'Unknown or malformed requirement override: {rid}')
            continue
        check_entry(entry, rid)
        record = {**defaults, **entry}
        implementation = record.get('implementation')
        status = record.get('test_status')
        if (not isinstance(implementation, str) or implementation not in IMPLEMENTATION or
                not isinstance(status, str) or status not in TEST):
            errors.append(f'Invalid status: {rid}')
        if status == 'PASS' and (implementation != 'IMPLEMENTED' or
                not all(isinstance(record.get(k), str) and record[k].strip()
                        for k in ('design_ref', 'case_ref', 'evidence_ref'))):
            errors.append(f'PASS needs implementation, design, test case and evidence: {rid}')
        if implementation == 'DEFERRED' and not (isinstance(record.get('decision_ref'), str)
                                                and record['decision_ref'].strip()):
            errors.append(f'DEFERRED needs approved decision reference: {rid}')
    if not errors:
        errors += check_tracking_references(tracking, source_ids, root if root is not None else ROOT, as_of)
    return errors


def build_rtm_rows(source: list[dict], tracking: dict, as_of=None) -> list[dict]:
    errors = validate_tracking(tracking, {row['urs_id'] for row in source}, as_of=as_of)
    if errors:
        raise ValueError('; '.join(errors))
    rows = []
    for original in source:
        state = {**tracking['defaults'], **tracking.get('overrides', {}).get(original['urs_id'], {})}
        # Apply source fields last as defense in depth, even after validation.
        rows.append({**{key: state.get(key, '') for key in TRACKING_FIELDS},
                     **{key: original[key] for key in SOURCE_FIELDS}})
    return rows



def read_requirements(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo('word/document.xml')
        if info.file_size > 20_000_000:
            raise ValueError('DOCX XML exceeds review limit')
        document = ET.fromstring(archive.read(info))
    result = []
    for ti, table in enumerate(document.findall('w:body/w:tbl', NS), 1):
        group = ''
        for ri, row in enumerate(table.findall('w:tr', NS), 1):
            cells = [''.join(t.text or '' for t in c.findall('.//w:t', NS)).strip()
                     for c in row.findall('w:tc', NS)]
            if not cells:
                continue
            match = re.fullmatch(r'URS\s*([\d\s]+)', cells[0], re.I)
            if match:
                if len(cells) < 3:
                    raise ValueError('Incomplete URS row')
                result.append({'urs_id': 'URS-' + re.sub(r'\s+', '', match[1]),
                    'original_id': cells[0], 'source_table': str(ti),
                    'source_row': str(ri), 'source_category': cells[2],
                    'source_group': group, 'source_text': cells[1]})
            elif len(cells) == 1:
                group = cells[0]
    return result


def validate(index: list[dict], source: list[dict], tracking: dict, as_of=None) -> list[str]:
    errors = []
    source_ids = [r['urs_id'] for r in source]
    ids = [r.get('urs_id') for r in index]
    if len(source_ids) != 185 or len(set(source_ids)) != 185:
        errors.append('Source must contain exactly 185 unique baseline URS IDs')
    if len(ids) != 185 or len(set(ids)) != len(ids) or set(ids) != set(source_ids):
        errors.append('Index must contain all 185 unique source URS IDs')
    sources = {r['urs_id']: r for r in source}
    for row in index:
        original = sources.get(row.get('urs_id'), {})
        for field in ('source_table', 'source_row', 'source_category'):
            if row.get(field) != original.get(field):
                errors.append(f"Source locator/category mismatch: {row.get('urs_id')} {field}")
    errors += validate_tracking(tracking, set(source_ids), as_of=as_of)
    return errors


def safe_csv(value: object) -> str:
    text = str(value or '')
    return "'" + text if text[:1] in ('=', '+', '-', '@') else text


def main() -> int:
    out = ROOT / 'artifacts/governance'
    out.mkdir(parents=True, exist_ok=True)
    # Failed input/registry reads must also remove a previous successful export.
    export = out / 'requirements-rtm.csv'
    export.unlink(missing_ok=True)
    (out / 'check-result.json').unlink(missing_ok=True)
    source = []
    errors = []
    assessed_at = evaluation_time()
    try:
        errors = [f'Missing required file: {p}' for p in REQUIRED if not (ROOT / p).is_file()]
        manifest = repository_json(ROOT, 'docs/sources/manifest.json')
        source_path = repository_path(ROOT, manifest['urs_path'])
        if not source_path.is_relative_to(ROOT.resolve()):
            raise ValueError('URS path outside repository')
        source = read_requirements(source_path)
        with repository_path(ROOT, 'docs/requirements/urs-index.csv').open(encoding='utf-8', newline='') as stream:
            index = list(csv.DictReader(stream))
        tracking = repository_json(ROOT, 'docs/requirements/traceability.json')
        errors += validate(index, source, tracking, as_of=assessed_at)
        if not errors:
            rows = build_rtm_rows(source, tracking, as_of=assessed_at)
            fields = ['urs_id', 'original_id', 'source_table', 'source_row', 'source_category',
                      'source_group', 'source_text', 'implementation', 'test_status',
                      'owner', 'design_ref', 'case_ref', 'evidence_ref', 'decision_ref']
            with export.open('w', encoding='utf-8-sig', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows({k: safe_csv(row.get(k, '')) for k in fields} for row in rows)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError, OverflowError, zipfile.BadZipFile) as exc:
        errors.append(f'{type(exc).__name__}: {exc}')
    if errors:
        export.unlink(missing_ok=True)
    report = {'scope': 'repository governance and offline engineering evidence integrity only; not application validation or approval authenticity',
              'test_status_semantics': 'ENGINEERING_TEST_ONLY',
              'validation_execution': 'NOT_ASSESSED', 'independent_review': 'NOT_ASSESSED',
              'qa_release': 'NOT_ASSESSED', 'evaluated_at': assessed_at.isoformat(),
              'requirements': len(source), 'errors': errors}
    (out / 'check-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
