"""Reproduce the accepted planning arithmetic; no empirical delivery guarantee."""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_CEILING
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def number(value: object, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Planning inputs must be numeric, not Boolean or text')
    result = Decimal(str(value))
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise ValueError('Invalid planning input')
    return result


def bounds(values: list) -> tuple[Decimal, Decimal]:
    if not isinstance(values, list) or len(values) != 2:
        raise ValueError('Expected lower/upper pair')
    low, high = (number(v) for v in values)
    if low > high:
        raise ValueError('Lower bound exceeds upper bound')
    return low, high


def estimate(model: dict) -> dict:
    days = number(model['nominal_days_per_month'], positive=True)
    fraction = number(model['effective_fraction'], positive=True)
    if fraction > 1:
        raise ValueError('Effective fraction cannot exceed one')
    if model.get('full_includes_pilot') is not True:
        raise ValueError('Full scope already includes the pilot; do not add it again')
    if model.get('uses_453_or_1023_as_days') is not False:
        raise ValueError('Unconfirmed source-workbook units cannot drive this estimate')
    pilot = bounds(model['pilot_effort_days'])
    wait_pilot = bounds(model['pilot_external_wait_months'])
    wait_full = bounds(model['full_external_wait_months'])
    packages = model['work_packages']
    if not packages:
        raise ValueError('Work packages required')
    pairs = [bounds([p['min_days'], p['max_days']]) for p in packages]
    full = tuple(sum((p[i] for p in pairs), Decimal(0)) for i in (0, 1))
    scenarios = []
    for size in model['team_sizes']:
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError('Team size must be a positive integer')
        capacity = number(size, positive=True) * days * fraction
        rounded = lambda effort, wait: [int((effort[i] / capacity + wait[i]).to_integral_value(rounding=ROUND_CEILING)) for i in (0, 1)]
        scenarios.append({'developers': size, 'effective_person_days_per_month': float(capacity),
                          'pilot_months': rounded(pilot, wait_pilot),
                          'full_scope_months_including_pilot': rounded(full, wait_full)})
    return {'scope': 'planning arithmetic only; not measured productivity or a commitment',
            'full_effort_days': [float(x) for x in full], 'scenarios': scenarios,
            'external_qa_qc_it_validation_not_counted_as_developers': True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, default=ROOT / 'docs/delivery/capacity-model.json')
    args = parser.parse_args()
    try:
        result = estimate(json.loads(args.model.read_text(encoding='utf-8')))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'errors': [str(exc)]}, ensure_ascii=False))
        return 1
    out = ROOT / 'artifacts/governance'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'delivery-estimate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
