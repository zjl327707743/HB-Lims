"""Planning/source snapshot safeguards. Not application, legal or GMP validation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
from check_repository import read_requirements
from estimate_delivery import estimate
from check_evidence import repository_json

ROOT = Path(__file__).resolve().parents[2]
FUNCTION_SOURCE_SHA = '0e592d9ca10f5454832bd527d519502aecdf70152b1dcf11b52a06bda16744ea'
FUNCTION_FIELDS_SHA = 'dc387de2edae06cfeaf1e2335280b80322cfd90d26dc648052c4ef5c8ac76675'
PROPOSAL_SHA = '8b097f7d21d3d38d002b4c2c7ab97b721ef0ad81dd80f089d7ee95c1751c5da6'
CONTROL_IDS = {f'C{i:02d}' for i in range(1, 15)}
TECH_IDS = {f'T{i:02d}' for i in range(1, 9)}
REQUIRED = (
    'docs/standards/FRAMEWORK_BASELINE.md', 'docs/standards/REGULATORY_SCOPE.md',
    'docs/standards/RECORDS_AUDIT.md', 'docs/standards/LES_CONFIG_CALC.md',
    'docs/standards/REPORTS_INTEGRATIONS.md', 'docs/standards/RECOVERY_OPERATIONS.md',
    'docs/standards/VALIDATION_EVIDENCE.md', 'docs/standards/EXTENSIONS.md',
    'docs/requirements/FUNCTION_SCOPE.md', 'docs/delivery/TEAM_PLAYBOOK.md',
    'docs/delivery/FIRST_FOUR_WEEKS.md', 'docs/delivery/ROADMAP.md',
    'docs/sources/PLANNING_INPUTS.md', 'docs/templates/TASK_BRIEF.md',
    'docs/templates/HANDOFF.md', 'docs/templates/VALIDATION_EVIDENCE.json',
    'docs/templates/RELEASE_MANIFEST.json',
    'docs/governance/changes/CHANGE-20261116-FRAMEWORK-V1.md',
)


# Schema v1 describes frozen planning snapshots, not live execution progress.
# Rebaseline changes require an explicit change record and independent PR review;
# update these contracts and their rejection tests together. Never weaken them
# simply to make a proposed state pass.
def shape(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        return ['Unexpected/missing fields: ' + label]
    errors = []
    for key, types in fields.items():
        allowed = types if isinstance(types, tuple) else (types,)
        item = value[key]
        if type(item) not in allowed:
            errors.append('Invalid type: ' + label + '.' + key)
        elif isinstance(item, str) and not item.strip():
            errors.append('Empty field: ' + label + '.' + key)
    return errors


def list_type(value, kind):
    return isinstance(value, list) and all(type(x) is kind for x in value) and len(set(value)) == len(value)


FRAMEWORK_SHAPE = {k: str for k in (
    'id', 'planning_status', 'acceptance_message_time', 'publication_status',
    'technical_baseline', 'source_head', 'control_registry', 'function_scope',
    'capacity_model', 'backlog', 'application_validation', 'visual_validation',
    'qa_approval', 'production_release', 'change_record', 'note')}
FRAMEWORK_SHAPE.update({k: int for k in ('schema_version', 'source_urs_count', 'function_count',
    'control_count', 'technology_extension_count')})
FRAMEWORK_SHAPE['required_documents'] = list
CONTROL_SHAPE = {k: str for k in ('source_workbook', 'source_sha256', 'source_sheet',
    'planning_status', 'implementation', 'test_status', 'qa_approval')}
CONTROL_SHAPE.update(schema_version=int, controls=list, technology_extensions=list)
CONTROL_ROW_SHAPE = {k: str for k in ('id', 'title', 'priority', 'source_refs', 'document', 'owner_role', 'acceptance')}
CONTROL_ROW_SHAPE['source_row'] = int
TECH_ROW_SHAPE = {k: str for k in ('id', 'title', 'direction', 'adoption', 'stage')}
TECH_ROW_SHAPE['source_row'] = int
BACKLOG_SHAPE = {'schema_version': int, 'status': str, 'note': str, 'tasks': list}
TASK_SHAPE = {k: str for k in ('id', 'title', 'stage', 'owner_role', 'status', 'exit')}
TASK_SHAPE.update({k: list for k in ('depends_on', 'control_ids', 'urs_ids', 'function_ids', 'issues')})
FUNCTION_SHAPE = {k: str for k in ('source_file', 'source_sha256', 'source_sheet', 'source_range',
    'mapping_status', 'note', 'implementation', 'test_status')}
FUNCTION_SHAPE.update(schema_version=int, les_required_function_ids=list, rows=list,
    unresolved_source_semantics=list, effort_values=dict)
FUNCTION_ROW_SHAPE = {'id': int, 'source_row': int, 'source_title': (str, type(None)),
    'display_title': str, 'selected_raw': int, 'urs_refs': str, 'stage': str}
EFFORT_SHAPE = {k: str for k in ('function_total_cell', 'function_total_formula', 'staff_sheet',
    'staff_total_cell', 'staff_total_formula')}
EFFORT_SHAPE.update(function_total_value=int, staff_total_value=int, unit_confirmed=bool,
    used_for_delivery_estimate=bool)

BACKLOG_LINKS = {'B01': {'urs_ids': ['URS-105', 'URS-703', 'URS-704', 'URS-2109'],
         'control_ids': ['C01', 'C07', 'C14'],
         'function_ids': [5, 6, 7, 21],
         'depends_on': []},
 'B02': {'urs_ids': ['URS-602', 'URS-624', 'URS-800'],
         'control_ids': ['C08'],
         'function_ids': [7],
         'depends_on': []},
 'B03': {'urs_ids': ['URS-604', 'URS-620', 'URS-1401'],
         'control_ids': ['C09', 'C10'],
         'function_ids': [16, 17, 18, 19, 20, 21, 24, 26, 27, 28],
         'depends_on': []},
 'B04': {'urs_ids': ['URS-100', 'URS-101', 'URS-102'],
         'control_ids': ['C13', 'C14'],
         'function_ids': [1, 8],
         'depends_on': []},
 'B05': {'urs_ids': ['URS-618', 'URS-900', 'URS-2001', 'URS-2011'],
         'control_ids': ['C06', 'C14'],
         'function_ids': [8, 20],
         'depends_on': ['B01', 'B04']},
 'B06': {'urs_ids': ['URS-500', 'URS-607', 'URS-1201', 'URS-1306'],
         'control_ids': ['C04', 'C05'],
         'function_ids': [7, 11, 19, 25],
         'depends_on': ['B01', 'B04']},
 'B07': {'urs_ids': ['URS-601', 'URS-603', 'URS-616', 'URS-622'],
         'control_ids': ['C02', 'C03'],
         'function_ids': [7],
         'depends_on': ['B04', 'B05']},
 'B08': {'urs_ids': ['URS-200', 'URS-300', 'URS-400', 'URS-500'],
         'control_ids': ['C04', 'C06'],
         'function_ids': [1, 4, 8],
         'depends_on': ['B05', 'B06', 'B07']},
 'B09': {'urs_ids': ['URS-601', 'URS-607', 'URS-610', 'URS-613', 'URS-619'],
         'control_ids': ['C02', 'C05', 'C06'],
         'function_ids': [7, 9, 10, 11, 12, 13],
         'depends_on': ['B06', 'B07', 'B08']},
 'B10': {'urs_ids': ['URS-703', 'URS-704', 'URS-706', 'URS-800', 'URS-2105'],
         'control_ids': ['C03', 'C07', 'C08'],
         'function_ids': [1, 5, 7, 21],
         'depends_on': ['B02', 'B09']},
 'B11': {'urs_ids': ['URS-604', 'URS-620', 'URS-1400', 'URS-1401'],
         'control_ids': ['C06', 'C09', 'C10'],
         'function_ids': [9, 10, 11, 12, 13, 19, 20, 24, 26, 27, 28],
         'depends_on': ['B03', 'B09']},
 'B12': {'urs_ids': ['URS-103', 'URS-104', 'URS-105', 'URS-114'],
         'control_ids': ['C08', 'C12', 'C14'],
         'function_ids': [1, 7, 25],
         'depends_on': ['B10', 'B11']},
 'B13': {'urs_ids': ['URS-2107', 'URS-2108', 'URS-2109'],
         'control_ids': ['C01', 'C13', 'C14'],
         'function_ids': [1, 7],
         'depends_on': ['B01', 'B12']},
 'B14': {'urs_ids': ['URS-601', 'URS-602', 'URS-623', 'URS-1600', 'URS-1700', 'URS-1800'],
         'control_ids': ['C04', 'C06', 'C07', 'C09', 'C10', 'C11', 'C12', 'C13'],
         'function_ids': [2,
                          3,
                          4,
                          5,
                          7,
                          9,
                          10,
                          11,
                          12,
                          13,
                          16,
                          17,
                          18,
                          19,
                          20,
                          21,
                          22,
                          23,
                          24,
                          25,
                          26,
                          27,
                          28],
         'depends_on': ['B13']}}


def load(root: Path, relative: str) -> dict:
    return repository_json(root, relative)


def validate_framework(data: dict) -> list[str]:
    malformed = shape(data, FRAMEWORK_SHAPE, 'framework')
    if malformed:
        return malformed
    if data['schema_version'] != 1 or not list_type(data['required_documents'], str):
        return ['Invalid framework schema/documents']
    expected = {'id': 'HB-LIMS-FRAMEWORK-V1', 'planning_status': 'OWNER_ACCEPTED',
                'acceptance_message_time': '2026-11-16T10:13:30Z',
                'publication_status': 'PR_REVIEW_PENDING',
                'technical_baseline': 'docs/standards/baseline.json',
                'source_head': '254b977b0520cdb6a9f19bf452a55499baa68265',
                'application_validation': 'NOT_RUN', 'visual_validation': 'NOT_RUN',
                'qa_approval': 'NOT_GRANTED', 'production_release': 'NOT_AUTHORIZED',
                'source_urs_count': 185, 'function_count': 28, 'control_count': 14,
                'technology_extension_count': 8,
                'control_registry': 'docs/standards/controls.json',
                'function_scope': 'docs/requirements/function-scope.json',
                'capacity_model': 'docs/delivery/capacity-model.json',
                'backlog': 'docs/delivery/backlog.json'}
    errors = [f'Unsupported framework value: {key}' for key, value in expected.items() if data.get(key) != value]
    if data.get('required_documents') != list(REQUIRED):
        errors.append('Required framework document list changed')
    return errors


def validate_controls(data: dict, root: Path) -> list[str]:
    malformed = shape(data, CONTROL_SHAPE, 'controls')
    if malformed:
        return malformed
    if data['schema_version'] != 1:
        return ['Invalid control schema']
    for row in data['controls']:
        malformed += shape(row, CONTROL_ROW_SHAPE, 'control')
    for row in data['technology_extensions']:
        malformed += shape(row, TECH_ROW_SHAPE, 'technology')
    if malformed:
        return malformed
    errors = []
    rows = data.get('controls', [])
    if len(rows) != 14 or {r.get('id') for r in rows} != CONTROL_IDS:
        errors.append('All 14 unique controls are required')
    for key, value in {'planning_status': 'OWNER_ACCEPTED', 'implementation': 'NOT_IMPLEMENTED',
                       'test_status': 'NOT_RUN', 'qa_approval': 'NOT_GRANTED',
                       'source_sha256': PROPOSAL_SHA}.items():
        if data.get(key) != value:
            errors.append('Unsupported control registry claim/source: ' + key)
    for row in rows:
        if not all(row.get(k) for k in ('title', 'source_refs', 'document', 'acceptance', 'owner_role')):
            errors.append('Incomplete control: ' + str(row.get('id')))
        if row.get('id') in CONTROL_IDS and row.get('source_row') != int(row['id'][1:]) + 4:
            errors.append('Control source row changed: ' + row['id'])
        target = (root / row.get('document', '')).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            errors.append('Missing/unsafe control document: ' + str(row.get('id')))
    tech = data.get('technology_extensions', [])
    if len(tech) != 8 or {r.get('id') for r in tech} != TECH_IDS:
        errors.append('All 8 unique technology extensions are required')
    allowed = {'ENGINEERING_DIRECTION_ACCEPTED_VERSION_PENDING', 'POC_QUALIFICATION_REQUIRED',
               'DEVICE_DEPENDENT_QUALIFICATION_REQUIRED', 'PRODUCT_CAPABILITY_ACCEPTED',
               'BASIC_REQUIRED_EXTRA_PLATFORM_OPTIONAL', 'REQUIREMENT_RETAINED_COMPONENT_PENDING'}
    for row in tech:
        if row.get('adoption') not in allowed or not row.get('direction'):
            errors.append('Unsupported technology adoption claim: ' + str(row.get('id')))
    return errors


def validate_functions(data: dict) -> list[str]:
    malformed = shape(data, FUNCTION_SHAPE, 'functions')
    if malformed:
        return malformed
    malformed += shape(data['effort_values'], EFFORT_SHAPE, 'effort')
    for row in data['rows']:
        malformed += shape(row, FUNCTION_ROW_SHAPE, 'function')
    if data['schema_version'] != 1 or not list_type(data['les_required_function_ids'], int) or not list_type(data['unresolved_source_semantics'], str):
        malformed.append('Invalid function schema/lists')
    if malformed:
        return malformed
    errors = []
    rows = data.get('rows', [])
    if len(rows) != 28 or {r.get('id') for r in rows} != set(range(1, 29)):
        errors.append('All 28 unique source function rows are required')
    else:
        subset = [[r['id'], r.get('source_row'), r.get('source_title'), r.get('selected_raw')]
                  for r in sorted(rows, key=lambda r: r['id'])]
        digest = hashlib.sha256(json.dumps(subset, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        if digest != FUNCTION_FIELDS_SHA:
            errors.append('Original function IDs/rows/titles/selection values changed')
    if data.get('source_sha256') != FUNCTION_SOURCE_SHA:
        errors.append('Original workbook fingerprint changed')
    if data.get('les_required_function_ids') != [9, 10, 11, 12, 13, 24, 26, 27]:
        errors.append('LES source dependencies changed')
    if data.get('implementation') != 'NOT_IMPLEMENTED' or data.get('test_status') != 'NOT_RUN':
        errors.append('Function snapshot cannot claim implementation/validation')
    effort = data.get('effort_values', {})
    if effort.get('unit_confirmed') is not False or effort.get('used_for_delivery_estimate') is not False:
        errors.append('Unconfirmed source effort units cannot be treated as person-days')
    if effort.get('function_total_value') != 453 or effort.get('staff_total_value') != 1023:
        errors.append('Observed original effort values changed')
    return errors


def validate_backlog(data: dict, urs_ids: set[str]) -> list[str]:
    malformed = shape(data, BACKLOG_SHAPE, 'backlog')
    if malformed:
        return malformed
    if data['schema_version'] != 1:
        return ['Invalid backlog schema']
    for row in data['tasks']:
        malformed += shape(row, TASK_SHAPE, 'task')
        if not malformed:
            for field in ('depends_on', 'control_ids', 'urs_ids'):
                if not list_type(row[field], str):
                    malformed.append('Invalid/duplicate task list: ' + field)
            for field in ('function_ids', 'issues'):
                if not list_type(row[field], int):
                    malformed.append('Invalid/duplicate task list: ' + field)
    if malformed:
        return malformed
    errors = []
    rows = data.get('tasks', [])
    ids = [r.get('id') for r in rows]
    expected = {f'B{i:02d}' for i in range(1, 15)}
    if len(ids) != 14 or set(ids) != expected:
        errors.append('Expected 14 unique planned tasks')
    if data.get('status') != 'PLANNED_NOT_EXECUTED':
        errors.append('Backlog must not claim execution')
    graph = {r.get('id'): r.get('depends_on', []) for r in rows}
    for row in rows:
        rid = row.get('id')
        if row['stage'] not in {'S0', 'S1', 'S2', 'S3', 'S4', 'S5'}:
            errors.append('Invalid task stage: ' + rid)
        if rid in BACKLOG_LINKS:
            for field, required in BACKLOG_LINKS[rid].items():
                if not set(required).issubset(row[field]):
                    errors.append('Frozen planning relation removed: ' + rid + '.' + field)
        if row.get('status') != 'PLANNED' or not row.get('exit') or not row.get('owner_role'):
            errors.append('Invalid task status/acceptance/owner: ' + str(rid))
        if not set(row.get('urs_ids', [])).issubset(urs_ids):
            errors.append('Unknown URS reference: ' + str(rid))
        if not set(row.get('control_ids', [])).issubset(CONTROL_IDS):
            errors.append('Unknown control reference: ' + str(rid))
        if not set(row.get('function_ids', [])).issubset(set(range(1, 29))):
            errors.append('Unknown function reference: ' + str(rid))
        if not set(row.get('depends_on', [])).issubset(set(ids)):
            errors.append('Unknown dependency: ' + str(rid))
    active, finished = set(), set()
    def visit(node: str) -> None:
        if node in active:
            errors.append('Cyclic task dependency: ' + node)
            return
        if node in finished or node not in graph:
            return
        active.add(node)
        for child in graph[node]:
            visit(child)
        active.remove(node)
        finished.add(node)
    for node in graph:
        visit(node)
    return errors


def inspect(root: Path = ROOT) -> dict:
    framework = load(root, 'docs/standards/framework.json')
    errors = validate_framework(framework)
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append('Required framework document missing: ' + relative)
    controls = load(root, 'docs/standards/controls.json')
    functions = load(root, 'docs/requirements/function-scope.json')
    tasks = load(root, 'docs/delivery/backlog.json')
    urs = read_requirements(root / 'docs/六车间QC实验室信息管理系统用户需求说明.docx')
    if len(urs) != 185:
        errors.append('URS baseline count differs from 185')
    errors += validate_controls(controls, root) + validate_functions(functions)
    errors += validate_backlog(tasks, {r['urs_id'] for r in urs})
    model = load(root, 'docs/delivery/capacity-model.json')
    result = estimate(model)
    if result['full_effort_days'] != [750.0, 1100.0]:
        errors.append('Accepted planning work-package totals changed')
    expected_ranges = {2: ([9, 13], [27, 40]), 3: ([7, 9], [19, 28])}
    if model.get('team_sizes') != [2, 3] or model.get('nominal_days_per_month') != 22 or model.get('effective_fraction') != 0.7:
        errors.append('Accepted capacity assumptions changed; use reviewed re-estimate')
    for row in result['scenarios']:
        expected = expected_ranges.get(row['developers'])
        if expected is None or (row['pilot_months'], row['full_scope_months_including_pilot']) != expected:
            errors.append('Accepted scenario range differs from workbook')
    evidence = load(root, 'docs/templates/VALIDATION_EVIDENCE.json')
    release = load(root, 'docs/templates/RELEASE_MANIFEST.json')
    if evidence.get('status') != 'NOT_RUN' or evidence.get('executed_at') is not None:
        errors.append('Evidence template cannot claim execution')
    if release.get('qa_approval') != 'NOT_GRANTED' or release.get('production_release') != 'NOT_AUTHORIZED':
        errors.append('Release template cannot claim approval')
    return {'scope': 'planning structure/source snapshots only; original uploaded XLSX not present in CI; not runtime or GMP validation',
            'framework': framework.get('id'), 'urs_count': len(urs),
            'functions': len(functions['rows']), 'controls': len(controls['controls']),
            'technology_extensions': len(controls['technology_extensions']),
            'planned_tasks': len(tasks['tasks']), 'errors': errors}


def main() -> int:
    out = ROOT / 'artifacts/governance'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'framework-result.json').unlink(missing_ok=True)
    try:
        result = inspect(ROOT)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError, OverflowError) as exc:
        result = {'errors': [f'{type(exc).__name__}: {exc}']}
    (out / 'framework-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return int(bool(result['errors']))


if __name__ == '__main__':
    sys.exit(main())
