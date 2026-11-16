.PHONY: governance estimate

# These targets check documents/planning only; they do not validate a LIMS application.
governance:
	python3 scripts/governance/verify_sources.py
	python3 scripts/governance/check_repository.py
	python3 scripts/governance/check_technical_baseline.py
	python3 scripts/governance/check_framework.py
	python3 scripts/governance/estimate_delivery.py
	python3 -m unittest discover -s scripts/governance -p 'test_*.py' -v

estimate:
	python3 scripts/governance/estimate_delivery.py
