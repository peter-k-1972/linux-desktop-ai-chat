# Phase 3 – CI-Integrationsstrategie

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** Wann Inventory und Coverage Map gebaut werden; blockierende vs. nicht blockierende Checks; Gap-Reports in CI sichtbar machen.

---

## 1. Übersicht

### 1.1 Artefakte und Build-Zeitpunkt

| Artefakt | Wann bauen | Abhängigkeiten |
|----------|------------|----------------|
| QA_TEST_INVENTORY | Nach Test-Discovery (pytest collect) | pytest, REGRESSION_CATALOG, fallback_file_walk |
| QA_COVERAGE_MAP | Nach Inventory | QA_TEST_INVENTORY, QA_TEST_STRATEGY, QA_KNOWLEDGE_GRAPH, QA_AUTOPILOT_V3 |
| Replay-Binding-Enrichment | Optional, vor Coverage Map | Inventory, Incidents, Bindings |

### 1.2 CI-Phasen

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Test Execution │ -> │  QA Build       │ -> │  Gap Report     │
│  (pytest)       │    │  (Inventory,    │    │  (optional)     │
│                 │    │   Coverage Map) │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 2. Wann Inventory und Coverage Map bauen

### 2.1 Empfohlene Trigger

| Trigger | Aktion | Begründung |
|---------|--------|------------|
| **PR / Merge Request** | Inventory + Coverage Map bauen | Änderungen an Tests/Code erfordern aktuelle Metriken |
| **Scheduled (täglich)** | Vollständiger QA-Build inkl. Enrichment | Replay-Binding, semantische Anreicherung |
| **Manuell** | On-Demand über CI-Job oder lokales Script | Ad-hoc-Analyse |

### 2.2 Ablauf (PR)

```yaml
# Pseudocode CI
1. pytest -m "not live and not slow"  # Tests ausführen
2. python scripts/qa/build_test_inventory.py
3. python scripts/qa/enrich_replay_binding.py  # optional, wenn Incidents vorhanden
4. python scripts/qa/build_coverage_map.py
5. python scripts/qa/generate_gap_report.py  # optional
6. Upload Gap Report als CI-Artefakt
```

### 2.3 Build-Reihenfolge

1. **Test Execution** (blockierend): pytest muss grün sein
2. **Inventory Build** (blockierend für Coverage Map): Schema-Validierung
3. **Coverage Map Build** (nicht blockierend für Merge): Kann fehlschlagen, ohne PR zu blockieren
4. **Gap Report** (nicht blockierend): Nur informativ

---

## 3. Blockierende vs. nicht blockierende Checks

### 3.1 Blockierend (PR darf nicht mergen)

| Check | Bedingung | Aktion bei Fehler |
|-------|-----------|-------------------|
| **pytest** | Tests müssen grün sein | Merge blockieren |
| **Inventory Schema** | QA_TEST_INVENTORY valide gegen Schema | Merge blockieren |
| **Coverage Map Schema** | QA_COVERAGE_MAP valide gegen Schema | Merge blockieren |

### 3.2 Nicht blockierend (Warnung, Merge möglich)

| Check | Bedingung | Aktion bei Fehler |
|-------|-----------|-------------------|
| **Gap-Schwellen** | failure_class_uncovered > X | Warnung in CI-Log |
| **orphan_count** | > max_orphan_count_warning | Warnung |
| **regression_requirement_unbound** | Offene Regression-Bindings | Warnung |
| **replay_unbound** | Incidents ohne Replay-Test | Warnung |

### 3.3 Konfigurierbare Schwellen

```json
{
  "blocking": {
    "pytest_fail": true,
    "inventory_schema_fail": true,
    "coverage_map_schema_fail": true
  },
  "warnings": {
    "failure_class_gap_count_max": 5,
    "orphan_count_warning": 50,
    "regression_unbound_count_max": 2,
    "replay_unbound_count_max": 5
  }
}
```

---

## 4. Gap Reports in CI sichtbar machen

### 4.1 Report-Formate

| Format | Verwendung |
|--------|------------|
| **Markdown** | GitHub/GitLab MR-Comment, Artefakt |
| **JSON** | Maschinelle Weiterverarbeitung |
| **JUnit XML** | Integration in Test-Report-UI (als „virtuelle“ Tests) |

### 4.2 Markdown-Gap-Report (Beispiel)

```markdown
## QA Gap Report (Phase 3)

### Blockierende Gaps
- Keine

### Warnungen
| Gap-Typ | Anzahl | Schwere |
|---------|--------|---------|
| failure_class_uncovered | 2 | medium |
| regression_requirement_unbound | 2 | medium |
| orphan_review_backlog | 42 | low |

### Details
- **rag_silent_failure:** Kein catalog_bound Test
- **TR-002, TR-004:** Incidents nicht an Regression gebunden
```

### 4.3 CI-Artefakt-Struktur

```
ci-artifacts/
  qa/
    QA_TEST_INVENTORY.json
    QA_COVERAGE_MAP.json
    PHASE3_GAP_REPORT.md
    PHASE3_GAP_REPORT.json
```

### 4.4 Sichtbarkeit in GitLab/GitHub

- **GitLab:** Job-Artefakte; optional: MR-Comment mit Gap-Summary
- **GitHub Actions:** Upload als Artifact; optional: Issue-Comment bei PR
- **Beide:** Badge/Link zu letztem Gap-Report (z.B. „5 Gaps“)

---

## 5. Konkrete CI-Konfiguration

### 5.1 GitLab CI (Beispiel)

```yaml
qa-build:
  stage: test
  script:
    - pytest -m "not live and not slow" -q
    - python scripts/qa/build_test_inventory.py
    - python scripts/qa/build_coverage_map.py
    - python scripts/qa/generate_gap_report.py --format markdown --output PHASE3_GAP_REPORT.md
  artifacts:
    paths:
      - docs/qa/QA_TEST_INVENTORY.json
      - docs/qa/QA_COVERAGE_MAP.json
      - PHASE3_GAP_REPORT.md
    when: always
  allow_failure: false  # pytest blockiert
```

### 5.2 GitHub Actions (Beispiel)

```yaml
- name: Run tests
  run: pytest -m "not live and not slow" -q

- name: Build QA Inventory
  run: python scripts/qa/build_test_inventory.py

- name: Build Coverage Map
  run: python scripts/qa/build_coverage_map.py

- name: Generate Gap Report
  run: python scripts/qa/generate_gap_report.py --format markdown -o PHASE3_GAP_REPORT.md

- name: Upload QA artifacts
  uses: actions/upload-artifact@v4
  with:
    name: qa-reports
    path: |
      docs/qa/QA_TEST_INVENTORY.json
      docs/qa/QA_COVERAGE_MAP.json
      PHASE3_GAP_REPORT.md
```

---

## 6. Zusammenfassung

| Aspekt | Lösung |
|--------|--------|
| **Build-Zeitpunkt** | Nach pytest; PR und Scheduled |
| **Blockierend** | pytest, Schema-Validierung |
| **Nicht blockierend** | Gap-Schwellen, orphan_count, regression/replay unbound |
| **Gap-Report** | Markdown + JSON; CI-Artefakt; optional MR-Comment |
| **Artefakte** | Inventory, Coverage Map, Gap Report |
