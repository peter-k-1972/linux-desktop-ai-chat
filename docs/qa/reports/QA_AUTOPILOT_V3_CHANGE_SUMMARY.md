# QA Autopilot v3 – Change Summary (Critical/High Findings)

**Datum:** 2026-03-15  
**Scope:** Nur critical und high Findings aus Sanierungsplan

---

## 1. Geänderte Dateien

### `scripts/qa/autopilot_v3/rules.py`

**Warum geändert:** C1 (Regression-Binding), C2 (Score-Laufzeitfehler)

**Findings adressiert:** C1, C2

**Änderungen:**
- **C1:** `incident_not_bound_to_regression` prüft jetzt zusätzlich `inc.get("status") in ("bound_to_regression", "closed")`. Ein Incident gilt als gebunden, wenn `binding_status == "catalog_bound"` ODER `qa.status` in (bound_to_regression, closed). Logik angeglichen an Normalizer (normalizer.py Z. 110–116).
- **C2:** Neue Hilfsfunktion `_safe_score(x)` mit try/except für nicht-numerische Score-Werte. Filter `scores = [s for s in ... if isinstance(s, dict)]` verhindert AttributeError bei nicht-Dict-Einträgen.

---

### `scripts/qa/feedback_loop/utils.py`

**Warum geändert:** H2 (path.is_file()), H3 (path=None)

**Findings adressiert:** H2, H3

**Änderungen:**
- **H3:** `if path is None: return None` am Anfang von `load_json`.
- **H2:** `if not path.exists() or not path.is_file(): return None` – Verzeichnisse werden explizit ausgeschlossen.
- Signatur angepasst: `path: Path | None` für robuste API.

---

### `scripts/qa/autopilot_v3/utils.py` (gelöscht)

**Warum geändert:** H1 (toter Code)

**Findings adressiert:** H1

**Änderungen:** Datei entfernt. Wurde nirgends importiert; Feedback-Loop nutzt eigene Utils.

---

### `docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE.md`

**Warum geändert:** Folge von H1 – Paketstruktur-Dokumentation angepasst

**Findings adressiert:** H1 (Dokumentation)

**Änderungen:** `utils.py` aus der Paketstruktur-Liste entfernt.

---

## 2. Change Summary

### Behobene Findings

| ID | Titel | Status |
|----|-------|--------|
| **C1** | Regression-Binding ignoriert Incident-Status | behoben |
| **C2** | Laufzeitfehler bei ungültigem Score in QA_PRIORITY_SCORE | behoben |
| **H1** | Toter Code – autopilot_v3/utils.py | behoben |
| **H2** | load_json prüft nicht path.is_file() | behoben |
| **H3** | load_json nicht robust gegen path=None | behoben |

### Bewusst offen

| ID | Titel | Grund |
|----|-------|-------|
| M1–M7 | Medium Findings | Nur critical/high umgesetzt |
| L1–L2 | Low Findings | Nur critical/high umgesetzt |

---

## 3. Risiko-Hinweise

### Mögliche Folgeanpassungen

1. **`docs/qa/QA_AUTOPILOT_V3_ARCHITECTURE.md` (M1):** Die Tabelle zur Translation-Gap-Regel (Zeile 86) beschreibt weiterhin nur `binding_status != catalog_bound`. Sollte in Phase 3 um `status ∉ {bound_to_regression, closed}` ergänzt werden.

2. **`load_json`-Aufrufer:** Die Signatur `path: Path | None` ist erweitert. Bestehende Aufrufer (z.B. `_load` in loader.py) übergeben weiterhin nur gültige Paths; `path=None` wird aktuell nicht übergeben. Keine Änderung an Aufrufer-Seite nötig.

3. **QA_AUTOPILOT_V3.json:** Wird bei nächstem Lauf neu generiert. Bei Incidents mit `status=closed` oder `status=bound_to_regression` werden weniger `incident_not_bound_to_regression`-Translation-Gaps erscheinen; das ist korrekt.

4. **Golden-Tests:** Falls Snapshot-Tests mit festem Output existieren, können sich die `translation_gap_findings`-Zahlen ändern, sobald Incidents mit `status=closed`/`bound_to_regression` in den Testdaten vorkommen.

---

## 4. Verifikation

```bash
python3 scripts/qa/generate_autopilot_v3.py --timestamp "2026-01-01T00:00:00Z" --dry-run --output -
```

Exit-Code: 0. Keine Linter-Fehler.
