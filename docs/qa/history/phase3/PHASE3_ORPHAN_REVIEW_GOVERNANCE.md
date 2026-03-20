# Phase 3 – Orphan-Test-Governance

**Datum:** 15. März 2026  
**Status:** Architektur-Entwurf  
**Zweck:** orphan_tests als Review-Kandidaten statt harte Fehler; Definition verfeinern; False Positives reduzieren.

---

## 1. Ist-Zustand und Problem

### 1.1 Aktuelle Definition (coverage_map_rules.py)

```
orphan(test) =
  (test_domain in {root, helpers, qa})
  OR
  (kein catalog_bound failure_class UND test_domain in {root, helpers})
```

### 1.2 Bekannte False Positives

- **test_domain=qa:** 158 Tests – viele sind legitime QA-Meta-Tests (z.B. Coverage-Map-Tests, Feedback-Loop-Tests)
- **test_domain=helpers:** 8 Tests – Diagnostik-Helper sind keine „echten“ Orphans
- **test_domain=root:** 130 Tests – gemischt; viele Unit-Tests ohne failure_class, aber fachlich wertvoll

### 1.3 Konsequenz

- 296 orphan_tests in QA_COVERAGE_MAP
- Hoher Anteil False Positives → Governance-Signal wird verwässert
- Risiko: orphan_tests werden ignoriert statt als Review-Kandidaten genutzt

---

## 2. Governance-Prinzip: Review-Kandidaten statt Fehler

### 2.1 Paradigmenwechsel

| Vorher | Nachher |
|--------|---------|
| orphan = „schlechter Test“ | orphan = „Review-Kandidat“ |
| Blockierend / Fehler | Informativ / Backlog |
| Einheitliche Behandlung | Kategorisiert nach Kontext |

### 2.2 Kategorien

| Kategorie | Bedeutung | Aktion |
|-----------|-----------|--------|
| **orphan_review_candidate** | Potenziell ungebunden; manuelle Prüfung sinnvoll | Backlog; Sprint-Review |
| **orphan_legitimate** | Bekannt legitim (z.B. qa-Meta, helpers) | Whitelist; nicht als Gap zählen |
| **orphan_excluded** | Explizit ausgenommen (z.B. unit ohne failure_class) | Konfigurierbar |

---

## 3. Verfeinerte Definition

### 3.1 Neue Kriterien (konfigurierbar)

**Whitelist-Domains:** Tests in diesen Domains gelten nicht als orphan, auch ohne failure_class.

```
orphan_whitelist_domains = ["qa", "helpers", "meta"]
```

**Begründung:** qa-Tests prüfen die QA-Infrastruktur; helpers sind Diagnostik; meta prüft Drift. Diese sind fachlich gebunden, nur nicht an failure_class.

**Exclusion-Pfade:** Dateipfade, die nie als orphan gezählt werden.

```
orphan_exclusion_paths = [
  "tests/qa/",           # QA-Infrastruktur-Tests
  "tests/helpers/",      # Diagnostik
  "tests/meta/"           # Meta-Tests (z.B. event_type_drift)
]
```

**Reduzierte Orphan-Domains:** Nur noch `root` als „echte“ Orphan-Domain (ohne Whitelist).

```
orphan_candidate_domains = ["root"]
```

### 3.2 Verfeinerte Regel

```
orphan(test) =
  (test_domain in orphan_candidate_domains AND test_domain NOT IN orphan_whitelist_domains)
  AND
  (kein catalog_bound failure_class)
  AND
  (file_path NOT IN orphan_exclusion_paths)
```

**Ergebnis:** Deutlich weniger Orphans; nur Tests, die wirklich als Review-Kandidaten infrage kommen.

### 3.3 Rückwärtskompatibilität

- Bestehende `detect_orphan_tests()`-Funktion bleibt; neue Parameter für Whitelist/Exclusion
- Konfigurationsdatei: `docs/qa/phase3_orphan_governance.json`

---

## 4. Konfigurationsdatei

```json
{
  "schema_version": "1.0",
  "governance_mode": "review_candidate",
  "orphan_whitelist_domains": ["qa", "helpers", "meta"],
  "orphan_exclusion_paths": [
    "tests/qa/",
    "tests/helpers/",
    "tests/meta/"
  ],
  "orphan_candidate_domains": ["root"],
  "treat_as": "review_candidate",
  "ci_blocking": false,
  "max_orphan_count_warning": 50,
  "max_orphan_count_error": 200
}
```

---

## 5. Sichtbarkeit in Coverage Map

### 5.1 Erweiterte governance-Struktur

```json
{
  "governance": {
    "orphan_tests": [...],
    "orphan_count": 42,
    "orphan_breakdown": {
      "review_candidates": 42,
      "whitelisted": 254,
      "excluded_by_path": 0
    },
    "orphan_treat_as": "review_candidate",
    "orphan_ci_blocking": false
  }
}
```

### 5.2 Gap-Report-Anpassung

- `orphan_test` wird nicht als blockierender Gap geführt
- Eigenes Label: `orphan_review_backlog`
- Severity: `low` (nur informativ)

---

## 6. False-Positive-Reduktion

### 6.1 Erwartete Reduktion

| Vorher | Nachher (geschätzt) |
|--------|---------------------|
| 296 orphan_tests | ~40–80 (nur root ohne catalog_bound) |

### 6.2 Validierung

- Stichprobe: 10 als orphan markierte Tests manuell prüfen
- Wenn > 2 False Positives: Whitelist/Exclusion erweitern
- Iterativ: Nach jeder Inventory-Generierung Metrik prüfen

---

## 7. Implementierung

### 7.1 Änderungen in coverage_map_rules.py

```python
def detect_orphan_tests(
    inventory: dict[str, Any],
    config: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """
    Orphan: Review-Kandidaten gemäß phase3_orphan_governance.json.
    Whitelist: qa, helpers, meta; Exclusion: tests/qa/, tests/helpers/, tests/meta/
    """
    config = config or _load_orphan_governance_config()
    whitelist = set(config.get("orphan_whitelist_domains", ["qa", "helpers", "meta"]))
    exclusion_paths = config.get("orphan_exclusion_paths", [])
    candidate_domains = set(config.get("orphan_candidate_domains", ["root"]))

    orphans = []
    for t in inventory.get("tests") or []:
        domain = t.get("test_domain") or "root"
        path = t.get("file_path") or ""

        if domain in whitelist:
            continue
        if any(path.startswith(p) for p in exclusion_paths):
            continue
        if domain not in candidate_domains:
            continue
        if _test_has_catalog_bound_failure_class(t):
            continue

        orphans.append({
            "test_id": t.get("test_id") or _pytest_nodeid_to_test_id(t.get("pytest_nodeid", "")),
            "reason": f"test_domain={domain}, no catalog_bound failure_class",
        })
    return orphans
```

### 7.2 Keine Änderung an bestehenden Artefakten

- QA_TEST_INVENTORY: unverändert
- QA_COVERAGE_MAP: nur governance.orphan_*; keine Änderung an coverage_by_axis
- Tests: keine Änderung

---

## 8. Zusammenfassung

| Aspekt | Lösung |
|--------|--------|
| **Paradigma** | orphan = Review-Kandidat, nicht Fehler |
| **Definition** | Whitelist (qa, helpers, meta); nur root ohne catalog_bound |
| **False Positives** | Reduktion durch Exclusion-Pfade |
| **CI** | Nicht blockierend |
| **Sichtbarkeit** | orphan_breakdown, treat_as, ci_blocking in governance |
