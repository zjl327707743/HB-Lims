"""Verify frozen URS, prototype and archived frontend V1; never execute inputs.

Owner-authorized V2 replacement is recorded in CHANGE-20261116-TECH-V1.
The old frontend bytes remain frozen at their archive path, not exempted.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts' / 'source-review'
SOURCES = {
    'LIMS_V3.1_已采用交付包.zip': '92ffe7f1cfd967bd4222729d053f8997d8013f5b',
    'docs/六车间QC实验室信息管理系统用户需求说明.docx': 'ce31845d7fe0c77146c9f13962a87ed3585edc45',
    'docs/archive/frontend/LIMS独立前端开发规范.v1.20261116.md': '17eda331335a73fe8e0fea9b8ad49eb5ae68cde2',
}
EXPECTED_HTML_SHA256 = '8571548ef60bfa9d5d54508beea4b7713787929d7fa22601b368cf4f15860515'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def safe_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    members = archive.infolist()
    if len(members) > 1000 or sum(x.file_size for x in members) > 50_000_000:
        raise ValueError('Archive exceeds review limits')
    names = set()
    for item in members:
        path = PurePosixPath(item.filename)
        if path.is_absolute() or '..' in path.parts or '\\' in item.filename:
            raise ValueError('Unsafe archive path')
        if item.filename in names:
            raise ValueError('Duplicate archive member')
        names.add(item.filename)
        if item.file_size > 20_000_000 or item.flag_bits & 1:
            raise ValueError('Oversized or encrypted archive member')
    return members


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        safe_members(archive)
        root = ET.fromstring(archive.read('word/document.xml'))
    body = root.find('w:body', NS)
    if body is None:
        raise ValueError('DOCX body missing')
    lines: list[str] = []
    table_index = 0
    for element in body:
        kind = element.tag.rsplit('}', 1)[-1]
        if kind == 'tbl':
            table_index += 1
            lines.append(f'\n[TABLE {table_index}]')
            for row_index, row in enumerate(element.findall('w:tr', NS), 1):
                cells = [' '.join(t.text or '' for t in c.findall('.//w:t', NS)) for c in row.findall('w:tc', NS)]
                lines.append(f'ROW {row_index}: ' + ' | '.join(cells))
        elif kind == 'p':
            text = ''.join(t.text or '' for t in element.findall('.//w:t', NS))
            if text.strip():
                lines.append(text)
    return '\n'.join(lines) + '\n'


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'docs/sources/manifest.json').read_text(encoding='utf-8'))
    listed = manifest['files']
    declared = {item['path']: item for item in listed}
    errors: list[str] = []
    if len(listed) != 3 or set(declared) != set(SOURCES):
        errors.append('Manifest must retain all three frozen source objects')
    results = []
    for relative, expected in SOURCES.items():
        source = ROOT / relative
        data = source.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        digest = hashlib.sha256(data).hexdigest()
        results.append({'path': relative, 'bytes': len(data), 'git_blob_sha': blob, 'sha256': digest, 'matches_baseline': blob == expected})
        if blob != expected:
            errors.append('Original baseline changed: ' + relative)
        entry = declared.get(relative, {})
        if entry.get('git_blob_sha') != expected or entry.get('sha256') != digest:
            errors.append('Manifest hash mismatch: ' + relative)
        target = OUT / 'sources' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (OUT / 'urs-extracted.txt').write_text(extract_docx_text(ROOT / manifest['urs_path']), encoding='utf-8')
    entries = []
    found_html = False
    with zipfile.ZipFile(ROOT / 'LIMS_V3.1_已采用交付包.zip') as archive:
        for item in safe_members(archive):
            if item.is_dir():
                continue
            data = archive.read(item)
            digest = hashlib.sha256(data).hexdigest()
            entries.append({'path': item.filename, 'bytes': len(data), 'sha256': digest})
            if PurePosixPath(item.filename).name == '海滨LIMS.html':
                found_html = True
                if digest != EXPECTED_HTML_SHA256:
                    errors.append('Prototype HTML hash changed')
            if PurePosixPath(item.filename).suffix.lower() in {'.md', '.txt', '.csv', '.json', '.html'}:
                target = OUT / 'package' / item.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    if not found_html:
        errors.append('Approved prototype HTML missing')
    report = {'baseline_commit': manifest['baseline_commit'], 'sources': results, 'package_entries': entries, 'errors': errors}
    (OUT / 'inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source_count': len(results), 'archive_entry_count': len(entries), 'errors': errors}, ensure_ascii=False))
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
