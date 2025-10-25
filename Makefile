.PHONY: setup fmt scan-all local-report

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

fmt:
	ruff format

scan-all:
	python scanners/run_semgrep.py
	python scanners/run_gitleaks.py
	python scanners/run_pip_audit.py
	python scanners/run_trivy.py
	python scanners/run_syft.py
	python utils/merge_reports.py
	python utils/aggregate_score.py --fail-threshold high

local-report:
	@echo "Report at reports/security-summary.md"