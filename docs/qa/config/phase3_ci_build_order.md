# Phase 3 – QA Build-Reihenfolge für CI

**Datum:** 15. März 2026

---

## 1. Build-Reihenfolge

```
1. pytest -m "not live and not slow"     # Blockierend
2. python scripts/qa/build_test_inventory.py
3. python scripts/qa/enrich_replay_binding.py   # Optional
4. python scripts/qa/build_coverage_map.py
5. python scripts/qa/generate_gap_report.py --format both
```

---

## 2. Blockierende Checks

| Schritt | Blockierend | Bei Fehler |
|---------|-------------|------------|
| pytest | Ja | Merge blockieren |
| build_test_inventory | Nein* | Coverage Map fehlt Input |
| build_coverage_map | Nein | Gap Report fehlt Input |
| generate_gap_report | Nein | Nur informativ |

\* Schema-Validierung Inventory: optional, kann als separater Check laufen.

---

## 3. Output-Pfade

| Artefakt | Pfad |
|----------|------|
| QA_TEST_INVENTORY | docs/qa/artifacts/json/QA_TEST_INVENTORY.json |
| QA_COVERAGE_MAP | docs/qa/artifacts/json/QA_COVERAGE_MAP.json |
| Gap Report (MD) | docs/qa/artifacts/dashboards/PHASE3_GAP_REPORT.md |
| Gap Report (JSON) | docs/qa/artifacts/json/PHASE3_GAP_REPORT.json |

---

## 4. CI-Snippets

### GitLab CI

```yaml
qa-build:
  stage: test
  script:
    - pytest -m "not live and not slow" -q
    - python scripts/qa/build_test_inventory.py
    - python scripts/qa/build_coverage_map.py
    - python scripts/qa/generate_gap_report.py --format both
  artifacts:
    paths:
      - docs/qa/artifacts/json/QA_TEST_INVENTORY.json
      - docs/qa/artifacts/json/QA_COVERAGE_MAP.json
      - docs/qa/artifacts/dashboards/PHASE3_GAP_REPORT.md
      - docs/qa/artifacts/json/PHASE3_GAP_REPORT.json
    when: always
  allow_failure: false
```

### GitHub Actions

```yaml
- name: Run tests
  run: pytest -m "not live and not slow" -q

- name: Build QA Inventory
  run: python scripts/qa/build_test_inventory.py

- name: Build Coverage Map
  run: python scripts/qa/build_coverage_map.py

- name: Generate Gap Report
  run: python scripts/qa/generate_gap_report.py --format both

- name: Upload QA artifacts
  uses: actions/upload-artifact@v4
  with:
    name: qa-reports
    path: |
      docs/qa/artifacts/json/QA_TEST_INVENTORY.json
      docs/qa/artifacts/json/QA_COVERAGE_MAP.json
      docs/qa/artifacts/dashboards/PHASE3_GAP_REPORT.md
      docs/qa/artifacts/json/PHASE3_GAP_REPORT.json
```
