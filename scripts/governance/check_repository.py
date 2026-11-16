"""Repository governance checks, not application or GMP validation (stdlib only)."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

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


def validate(index: list[dict], source: list[dict], tracking: dict) -> list[str]:
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
    defaults = tracking.get('defaults', {})
    if defaults.get('implementation') != 'NOT_IMPLEMENTED' or defaults.get('test_status') != 'NOT_RUN':
        errors.append('Defaults must remain NOT_IMPLEMENTED / NOT_RUN')
    overrides = tracking.get('overrides', {})
    if not isinstance(overrides, dict):
        return errors + ['Overrides must be an object']
    for rid, entry in overrides.items():
        if rid not in sources or not isinstance(entry, dict):
            errors.append(f'Unknown or malformed requirement override: {rid}')
            continue
        record = {**defaults, **entry}
        if record.get('implementation') not in IMPLEMENTATION or record.get('test_status') not in TEST:
            errors.append(f'Invalid status: {rid}')
        if record.get('test_status') == 'PASS' and (
                record.get('implementation') != 'IMPLEMENTED' or
                not all(record.get(k) for k in ('design_ref', 'case_ref', 'evidence_ref'))):
            errors.append(f'PASS needs implementation, design, test case and evidence: {rid}')
        if record.get('implementation') == 'DEFERRED' and not record.get('decision_ref'):
            errors.append(f'DEFERRED needs approved decision reference: {rid}')
    return errors


def safe_csv(value: object) -> str:
    text = str(value or '')
    return "'" + text if text[:1] in ('=', '+', '-', '@') else text


def main() -> int:
    errors = [f'Missing required file: {p}' for p in REQUIRED if not (ROOT / p).is_file()]
    manifest = json.loads((ROOT / 'docs/sources/manifest.json').read_text(encoding='utf-8'))
    source = read_requirements(ROOT / manifest['urs_path'])
    with (ROOT / 'docs/requirements/urs-index.csv').open(encoding='utf-8', newline='') as stream:
        index = list(csv.DictReader(stream))
    tracking = json.loads((ROOT / 'docs/requirements/traceability.json').read_text(encoding='utf-8'))
    errors += validate(index, source, tracking)
    fields = ['urs_id', 'original_id', 'source_table', 'source_row', 'source_category',
              'source_group', 'source_text', 'implementation', 'test_status',
              'owner', 'design_ref', 'case_ref', 'evidence_ref', 'decision_ref']
    rows = []
    for requirement in source:
        rows.append({**requirement, **tracking['defaults'],
                     **tracking.get('overrides', {}).get(requirement['urs_id'], {})})
    out = ROOT / 'artifacts/governance'
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'requirements-rtm.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: safe_csv(row.get(k, '')) for k in fields} for row in rows)
    report = {'scope': 'repository governance only; not application validation',
              'requirements': len(rows), 'errors': errors}
    (out / 'check-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
