"""Offline engineering-reference integrity checks. Never authenticates QA approval."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

REGISTRY = 'docs/validation/engineering-evidence.json'
KIND = 'ENGINEERING_REFERENCES_NOT_QUALITY_APPROVAL'
PLACEHOLDERS = {'', 'UNASSIGNED', 'TBD', 'TODO', 'DOES_NOT_EXIST', 'PLACEHOLDER'}


def strict_json(path: Path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('Duplicate JSON key: ' + key)
            out[key] = value
        return out
    def invalid_constant(value):
        raise ValueError('Non-JSON numeric constant: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=invalid_constant)


def repository_path(root: Path, relative):
    """Resolve every input, including registries themselves, inside the checkout."""
    if (not isinstance(relative, str) or not relative or '://' in relative or
            Path(relative).is_absolute() or '..' in Path(relative).parts):
        raise ValueError('External/unsafe repository input')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Repository input escapes checkout')
    return path


def repository_json(root: Path, relative):
    return strict_json(repository_path(root, relative))


def evaluation_time(as_of=None):
    now = as_of if as_of is not None else datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError('Evaluation time must be timezone-aware')
    return now.astimezone(timezone.utc)


def exact(data, fields, label):
    if not isinstance(data, dict) or set(data) != set(fields):
        raise ValueError('Unexpected/missing fields: ' + label)


def text(value, label):
    if not isinstance(value, str) or value.strip().upper() in PLACEHOLDERS or value != value.strip():
        raise ValueError('Missing/placeholder text: ' + label)


def ids(value, allowed, label):
    if (not isinstance(value, list) or not value or
            any(not isinstance(x, str) for x in value) or len(set(value)) != len(value) or
            not set(value).issubset(allowed)):
        raise ValueError('Invalid/missing IDs: ' + label)


def timestamp(value, label):
    text(value, label)
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamp needs timezone: ' + label)
    return parsed.astimezone(timezone.utc)


def target(value):
    exact(value, ('source_commit', 'artifact_digests', 'config_digest'), 'target')
    if not isinstance(value['source_commit'], str) or not re.fullmatch(r'[0-9a-f]{40}', value['source_commit']):
        raise ValueError('Target requires full source commit')
    digests = value['artifact_digests']
    if not isinstance(digests, dict) or not digests:
        raise ValueError('Target requires artifact digests')
    for key, digest in digests.items():
        text(key, 'artifact name')
        if not isinstance(digest, str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', digest):
            raise ValueError('Invalid artifact digest')
    if not isinstance(value['config_digest'], str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', value['config_digest']):
        raise ValueError('Invalid configuration digest')


def artifact(root: Path, value, *, require_redacted=False):
    exact(value, ('path', 'sha256', 'classification'), 'artifact')
    allowed = {'APPROVED_REDACTED'} if require_redacted else {'SYNTHETIC', 'APPROVED_REDACTED'}
    if value['classification'] not in allowed:
        raise ValueError('Only synthetic/approved-redacted artifacts allowed in public repository')
    relative = value['path']
    p = repository_path(root, relative)
    if not p.is_file():
        raise ValueError('Missing/unsafe local artifact: ' + relative)
    if p.stat().st_size > 20_000_000:
        raise ValueError('Evidence artifact exceeds offline inspection limit')
    if not isinstance(value['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', value['sha256']):
        raise ValueError('Invalid artifact SHA-256: ' + relative)
    if hashlib.sha256(p.read_bytes()).hexdigest() != value['sha256']:
        raise ValueError('Artifact hash mismatch: ' + relative)
    return p


def registry(root: Path, urs_ids: set[str], as_of=None):
    """Resolve registered immutable artifacts, not real-world identity/approval truth."""
    now = evaluation_time(as_of)
    data = repository_json(root, REGISTRY)
    exact(data, ('schema_version', 'kind', 'target', 'scope_id', 'designs', 'cases', 'executions', 'scope_decisions'), 'registry')
    if type(data['schema_version']) is not int or data['schema_version'] != 1 or data['kind'] != KIND:
        raise ValueError('Unsupported engineering registry')
    if data['target'] is not None:
        target(data['target'])
    if data['scope_id'] is not None:
        text(data['scope_id'], 'current scope ID')
    indexes = {}
    for kind in ('designs', 'cases', 'executions', 'scope_decisions'):
        rows = data[kind]
        if not isinstance(rows, list):
            raise ValueError('Registry collection must be an array: ' + kind)
        index = {}
        for row in rows:
            fields = {'id', 'urs_ids', 'artifact'}
            if kind == 'cases':
                fields.add('design_ref')
            exact(row, fields, kind)
            text(row['id'], kind + '.id')
            if row['id'] in index:
                raise ValueError('Duplicate registry ID: ' + row['id'])
            ids(row['urs_ids'], urs_ids, kind + '.urs_ids')
            p = artifact(root, row['artifact'], require_redacted=kind == 'scope_decisions')
            obj = dict(row)
            if kind in ('executions', 'scope_decisions'):
                obj['record'] = strict_json(p)
            index[row['id']] = obj
        indexes[kind] = index
    for row in indexes['cases'].values():
        design = indexes['designs'].get(row['design_ref'])
        if design is None or not set(row['urs_ids']).issubset(design['urs_ids']):
            raise ValueError('Case design reference/URS mismatch: ' + row['id'])
    for row in indexes['executions'].values():
        run = row['record']
        exact(run, ('kind', 'evidence_id', 'urs_ids', 'design_ref', 'design_sha256', 'case_ref',
                    'case_sha256', 'owner', 'executor', 'executed_at', 'target', 'result',
                    'raw_evidence', 'retest_of', 'retest_disposition'), 'engineering execution')
        if run['kind'] != 'ENGINEERING_TEST_EXECUTION' or run['evidence_id'] != row['id'] or run['urs_ids'] != row['urs_ids']:
            raise ValueError('Engineering execution identity/URS mismatch')
        target(run['target'])
        text(run['owner'], 'run owner'); text(run['executor'], 'run executor')
        if timestamp(run['executed_at'], 'run timestamp') > now:
            raise ValueError('Engineering execution is in the future')
        if run['result'] not in ('PASS', 'FAIL', 'BLOCKED'):
            raise ValueError('Invalid engineering execution result')
        case = indexes['cases'].get(run['case_ref'])
        if case is None or case['design_ref'] != run['design_ref'] or not set(run['urs_ids']).issubset(case['urs_ids']):
            raise ValueError('Engineering execution case/design/URS mismatch')
        design = indexes['designs'][run['design_ref']]
        if (run['design_sha256'] != design['artifact']['sha256'] or
                run['case_sha256'] != case['artifact']['sha256']):
            raise ValueError('Execution is bound to different design/case bytes')
        if not isinstance(run['raw_evidence'], list) or not run['raw_evidence']:
            raise ValueError('Engineering execution needs raw evidence')
        for raw in run['raw_evidence']:
            artifact(root, raw)
    # Preserve previous failures. A later PASS can be a retest only through an
    # explicit engineering disposition; this is not a QA or validation approval.
    for row in indexes['executions'].values():
        run = row['record']
        related = run['retest_of']
        if (not isinstance(related, list) or any(not isinstance(x, str) for x in related) or
                len(set(related)) != len(related)):
            raise ValueError('Invalid retest relation list')
        if not related:
            if run['retest_disposition'] is not None:
                raise ValueError('Disposition has no linked prior execution')
            continue
        if run['result'] != 'PASS':
            raise ValueError('This schema records retest disposition on a subsequent PASS only')
        for previous_id in related:
            previous = indexes['executions'].get(previous_id)
            if previous is None:
                raise ValueError('Retest references missing history')
            failed = previous['record']
            if (failed['result'] not in ('FAIL', 'BLOCKED') or failed['case_ref'] != run['case_ref'] or
                    not set(run['urs_ids']).intersection(failed['urs_ids']) or
                    timestamp(failed['executed_at'], 'prior execution') >= timestamp(run['executed_at'], 'retest')):
                raise ValueError('Retest does not follow a related failed/blocked execution')
        disposition = strict_json(artifact(root, run['retest_disposition']))
        exact(disposition, ('kind', 'disposition_id', 'related_execution_ids', 'retest_execution_id',
                            'reason', 'reviewer', 'reviewed_at'), 'retest disposition')
        ids(disposition['related_execution_ids'], set(related), 'disposition execution IDs')
        if (disposition['kind'] != 'ENGINEERING_RETEST_DISPOSITION' or
                disposition['retest_execution_id'] != run['evidence_id'] or
                set(disposition['related_execution_ids']) != set(related)):
            raise ValueError('Retest disposition identity/history mismatch')
        text(disposition['disposition_id'], 'disposition ID')
        text(disposition['reason'], 'retest reason'); text(disposition['reviewer'], 'retest reviewer')
        if disposition['reviewer'] in (run['owner'], run['executor']):
            raise ValueError('Retest disposition requires a different declared reviewer')
        reviewed = timestamp(disposition['reviewed_at'], 'retest review')
        if reviewed < timestamp(run['executed_at'], 'retest') or reviewed > now:
            raise ValueError('Retest review time is inconsistent with execution/evaluation')
    for row in indexes['scope_decisions'].values():
        decision = row['record']
        exact(decision, ('kind', 'decision_id', 'urs_ids', 'scope', 'decision', 'status',
                         'approved_by', 'approved_at', 'valid_until', 'no_expiry_reason',
                         'revoked', 'controlled_record_locator'), 'scope decision')
        if (decision['kind'] != 'REDACTED_SCOPE_DECISION' or decision['decision_id'] != row['id'] or
                decision['urs_ids'] != row['urs_ids'] or decision['decision'] != 'DEFERRED' or
                decision['status'] not in ('APPROVED', 'REVOKED') or type(decision['revoked']) is not bool or
                (decision['status'] == 'REVOKED') != decision['revoked']):
            raise ValueError('Scope decision identity/status mismatch')
        text(decision['scope'], 'approved scope'); text(decision['approved_by'], 'approver')
        text(decision['controlled_record_locator'], 'controlled approval locator')
        approved = timestamp(decision['approved_at'], 'approval timestamp')
        if approved > now:
            raise ValueError('Scope approval is in the future')
        if decision['valid_until'] is None:
            text(decision['no_expiry_reason'], 'no-expiry rationale')
        else:
            if timestamp(decision['valid_until'], 'approval validity') <= approved:
                raise ValueError('Scope validity must follow approval')
            if decision['no_expiry_reason'] is not None:
                raise ValueError('Dated approval cannot also claim no expiry')
    return data, indexes


def check_tracking_references(tracking: dict, urs_ids: set[str], root: Path, as_of=None) -> list[str]:
    errors = []
    try:
        now = evaluation_time(as_of)
        data, refs = registry(root, urs_ids, now)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, AttributeError, OverflowError) as exc:
        return ['Evidence registry unavailable/invalid: ' + str(exc)]
    for rid, change in tracking.get('overrides', {}).items():
        if rid not in urs_ids or not isinstance(change, dict):
            continue
        row = {**tracking.get('defaults', {}), **change}
        try:
            if row.get('test_status') == 'PASS':
                text(row.get('owner'), 'PASS owner')
                design = refs['designs'].get(row.get('design_ref'))
                case = refs['cases'].get(row.get('case_ref'))
                evidence = refs['executions'].get(row.get('evidence_ref'))
                if any(item is None or rid not in item['urs_ids'] for item in (design, case, evidence)):
                    raise ValueError('PASS reference missing or wrong URS')
                run = evidence['record']
                if (run['result'] != 'PASS' or run['owner'] != row['owner'] or
                        run['case_ref'] != row['case_ref'] or run['design_ref'] != row['design_ref'] or
                        case['design_ref'] != row['design_ref'] or data['target'] is None or
                        run['target'] != data['target']):
                    raise ValueError('PASS result/owner/design/case/target mismatch')
                for other in refs['executions'].values():
                    failed = other['record']
                    if (rid not in failed['urs_ids'] or failed['case_ref'] != run['case_ref'] or
                            failed['target'] != run['target'] or failed['result'] not in ('FAIL', 'BLOCKED')):
                        continue
                    if timestamp(failed['executed_at'], 'failure') >= timestamp(run['executed_at'], 'PASS'):
                        raise ValueError('Selected PASS has a later or simultaneous FAIL/BLOCKED')
                    if failed['evidence_id'] not in run['retest_of']:
                        raise ValueError('Prior same-target failure lacks explicit retest disposition')
            if row.get('implementation') == 'DEFERRED':
                text(row.get('owner'), 'DEFERRED owner')
                decision = refs['scope_decisions'].get(row.get('decision_ref'))
                if (decision is None or rid not in decision['urs_ids'] or data['scope_id'] is None or
                        decision['record']['scope'] != data['scope_id']):
                    raise ValueError('DEFERRED requires a registered matching current-scope decision')
                approved = decision['record']
                if (approved['revoked'] or approved['status'] != 'APPROVED' or
                        (approved['valid_until'] is not None and
                         timestamp(approved['valid_until'], 'approval validity') <= now)):
                    raise ValueError('Scope approval is revoked or expired at evaluation time')
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f'{rid}: {exc}')
    return errors
