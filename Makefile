# Linux Desktop Chat — lokale QA-Shortcuts (ohne Netzwerkpflicht für Markdown-Gate)
.PHONY: markdown-check markdown-check-ci markdown-fix theme-guard theme-guard-suggest

markdown-check:
	python3 tools/run_markdown_quality_gate.py

markdown-check-ci:
	python3 tools/run_markdown_quality_gate.py --profile ci

markdown-fix:
	python3 tools/normalize_markdown_docs.py --fix-safe -q

# Farb-Lint: Exit 1 bei Verstößen (CI). Bis Migration abgeschlossen ggf. noch nicht als Required-Gate.
theme-guard:
	python3 tools/theme_guard.py

theme-guard-suggest:
	python3 tools/theme_guard.py --suggest
