"""Structural technical-document guard; not runtime, visual or GMP validation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = 'docs/archive/frontend/LIMS独立前端开发规范.v1.20261116.md'
ACTIVE = 'docs/LIMS独立前端开发规范.md'
ARCHIVE_SHA = '17eda331335a73fe8e0fea9b8ad49eb5ae68cde2'
PRESERVED = ('界面与操作', '核心业务', '验收')
SELECTED = {
    'frontend': 'Next.js App Router + React + TypeScript',
    'ui': 'Ant Design + @ant-design/nextjs-registry',
    'queries': 'TanStack Query', 'forms': 'Ant Design Form',
    'tables': 'Ant Design Table', 'charts': 'Recharts', 'url_state': 'nuqs',
    'backend': 'FastAPI + Pydantic', 'orm': 'SQLAlchemy 2.0',
    'migrations': 'Alembic', 'database': 'PostgreSQL', 'queue': 'Celery',
    'cache': 'Redis', 'object_interface': 'S3', 'proxy': 'Nginx',
    'container': 'Docker Compose', 'ci': 'GitHub Actions',
}
DOCS = tuple('docs/standards/' + name for name in (
    'README.md', 'TECH_STACK.md', 'FRONTEND.md', 'BACKEND_DATA.md',
    'SECURITY_SIGNATURE.md', 'STORAGE_TASKS.md', 'DELIVERY_VALIDATION.md', 'SOURCES.md'))
CHANGE = 'docs/governance/changes/CHANGE-20261116-TECH-V1.md'


def validate_selection(config: dict) -> list[str]:
    errors = []
    if config.get('id') != 'HB-LIMS-TECH-V1' or config.get('status') != 'DEVELOPMENT_BASELINE_FOR_REVIEW':
        errors.append('Unexpected baseline ID/status; changes require a reviewed version')
    if config.get('selected') != SELECTED:
        errors.append('Selected stack differs from the reviewed TECH-V1 proposal')
    if config.get('production_storage_product') is not None or config.get('storage_product_status') != 'BLOCKED_PENDING_QUALIFICATION':
        errors.append('Production storage cannot be declared qualified by this document-only baseline')
    for key, value in {'versions_locked': False, 'application_validation': 'NOT_RUN',
                       'visual_validation': 'NOT_RUN', 'qa_approval': 'NOT_GRANTED'}.items():
        if config.get(key) != value:
            errors.append('Unsupported completion/approval claim: ' + key)
    if config.get('frontend_active') != ACTIVE or config.get('frontend_archive') != ARCHIVE or config.get('frontend_archive_git_blob') != ARCHIVE_SHA:
        errors.append('Frontend authority paths/hash changed')
    if config.get('preserved_sections') != list(PRESERVED):
        errors.append('All three preserved frontend sections are required')
    if config.get('required_documents') != list(DOCS) or config.get('change_record') != CHANGE:
        errors.append('Required documentation/change record omitted or changed')
    return errors


def validate_archive(data: bytes) -> list[str]:
    actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return [] if actual == ARCHIVE_SHA else ['Frozen V1 frontend archive bytes changed']


def sections(text: str) -> dict[str, str]:
    return {m[1].strip(): m[2].strip() for m in re.finditer(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', text, re.M | re.S)}


def validate_preserved(old: str, new: str) -> list[str]:
    before, after = sections(old), sections(new)
    return ['Preserved frontend section missing/changed: ' + title for title in PRESERVED
            if title not in before or title not in after or before[title] != after[title]]


def check_relative_links(root: Path, paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if path.relative_to(root).as_posix() == ARCHIVE:
            continue  # Historical bytes preserve their original relative link context.
        text = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for raw in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
            target = raw.strip().strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            relative = unquote(parsed.path)
            resolved = (root / relative.lstrip('/') if relative.startswith('/') else path.parent / relative).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f'Broken/out-of-repository link: {path.relative_to(root)} -> {target}')
    return errors


def inspect(root: Path = ROOT) -> dict:
    config = json.loads((root / 'docs/standards/baseline.json').read_text(encoding='utf-8'))
    errors = validate_selection(config)
    for path in (*DOCS, CHANGE, ARCHIVE, ACTIVE):
        if not (root / path).is_file():
            errors.append('Required document missing: ' + path)
    if (root / ARCHIVE).is_file() and (root / ACTIVE).is_file():
        old = (root / ARCHIVE).read_bytes()
        errors += validate_archive(old)
        errors += validate_preserved(old.decode('utf-8'), (root / ACTIVE).read_text(encoding='utf-8'))
    files = list(root.glob('*.md'))
    for directory in ('docs', 'apps', 'packages', 'tests', 'deploy', '.github'):
        files.extend((root / directory).rglob('*.md'))
    errors += check_relative_links(root, files)
    return {'scope': 'document structure and historical text only; no runtime/visual/compliance claim',
            'baseline': config.get('id'), 'markdown_files_checked': len(files),
            'preserved_sections': list(PRESERVED), 'errors': errors}


def main() -> int:
    try:
        result = inspect()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'errors': [f'{type(exc).__name__}: {exc}']}
    out = ROOT / 'artifacts/governance'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'technical-baseline-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return int(bool(result['errors']))


if __name__ == '__main__':
    sys.exit(main())
