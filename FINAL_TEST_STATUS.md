# Final Test Status — Linux Desktop Chat

**Stand (Dokumentation der Metriken):** 2026-03-22  
**Repository-Snapshot (Git):** `afcac5914534c3f36818ab4ef1e72440b47b3d6d` (kurz `afcac59`, Commit-Datum 2026-03-20)  
**Umgebung (Messung):** Python 3.12.3, pytest 9.0.2, virtuelle Umgebung mit `pip install -r requirements.txt` (Messung: `.venv-ci/` im Projektroot; lokal äquivalent z. B. `.venv/`)

---

## Sammlung (reproduzierbar)

**Kommando (nur Sammlung, schnell):**

```bash
python -m pytest tests --collect-only -q
```

*(aus aktivierter venv; bei diesem Stand: 1838 Tests gesammelt in ca. 1 s)*

| Metrik | Wert |
|--------|------|
| **Sammlung** unter `tests/` | **1838** Tests |
| **Collection Errors** (bei Messung) | **0** |

### Teilmengen (Anzahl gesammelter Tests, gleiche Umgebung, collect-only)

| Pfad | Tests (collect-only) |
|------|------------------------|
| `tests/architecture/` | 115 |
| `tests/unit/` | 612 |
| `tests/smoke/` | 61 |

**Hinweis:** Die früher hier genannte Zahl **1681** bezog sich auf einen älteren Referenzlauf; die Suite ist gewachsen. Maßgeblich für Planung ist die **Sammlung am genannten Commit**; nach größeren Test-Erweiterungen erneut messen.

---

## Vollständiger Testlauf (pytest)

**Kommando (vollständige Suite, typisch):**

```bash
python -m pytest tests -q --tb=short
```

*(äquivalent: `.venv/bin/python -m pytest tests -q --tb=short`; CI: `.github/workflows/pytest-full.yml`)*

| Metrik | Hinweis |
|--------|---------|
| **Exit-Code / Laufzeit** | Vor Release oder nach größeren Änderungen **lokal oder in CI** verifizieren. Der Release-Freeze **v0.9.0** dokumentierte einen Referenzlauf mit Exit-Code **0**; die **Anzahl** der gesammelten Tests war damals niedriger als die aktuelle Sammlung (**1838**). |
| **Referenz-Laufzeit** | Zuletzt dokumentiert ca. **20,5 min** (~1226 s) auf Referenzhardware (historisch). |
| **Timeouts** | kein globales pytest-timeout in `pytest.ini` |

### Spot-Check (2026-03-22, diese Arbeitskopie)

Ein abgebrochener Lauf mit `--maxfail=5` zeigte **Fehlschläge in Architektur-Guards** (u. a. verbotene Import-Richtungen `app.core`↔`app.gui`/`app.services`, Provider-Import-Regeln, unerwartetes Root-Skript `run_workbench_demo.py`). Das ist **kein** Nachweis, dass die gesamte Suite dauerhaft rot ist, aber es zeigt: **„Vollständig grün“ ist für diesen Arbeitsstand nicht ohne erneuten vollständigen Lauf/CI zu behaupten.** Details bei Bedarf mit `pytest tests/architecture -q --tb=short`.

---

## Ausnahmefälle (klar definiert)

### A. aiohttp: „Unclosed client session“ nach Testende

- **Symptom:** Nach Abschluss der Suite kann auf **stderr** eine Meldung `Unclosed client session` erscheinen.
- **Impact:** Kann trotz Exit-Code **0** auftreten (je nach Stand); siehe `FINAL_TEST_STATUS`-Historie und `BUGFIX_CHANGELOG.md` §4.

### B. System-Python ohne Virtualenv (PEP 668)

- **Symptom:** `pip install` systemweit eingeschränkt; `pytest` ohne installierte Abhängigkeiten → Collection-Errors (`qasync`, …).
- **Kein Projekt-Bug:** Umgebungsrichtlinie der Distribution.
- **Erwartung:** CI und lokale Freigabe nutzen **venv** oder `actions/setup-python` + `requirements.txt`.

---

## Kurzfassung

Die unter `tests/` gesammelte Testanzahl am dokumentierten Commit beträgt **1838** (pytest 9.0.2). **Veraltete QA-Tabellen** (z. B. `tests/TEST_AUDIT_REPORT.md` von 2025-03-15) sind **nicht** maßgeblich — siehe Banner in dieser Datei und `tests/README.md`.

**Aktuelle Release-Abnahme:** **`docs/RELEASE_ACCEPTANCE_REPORT.md`** (nicht verwechseln mit älteren QA-Snapshots unter `docs/FINAL_QA_ACCEPTANCE_REPORT.md`).

**Verbesserungspaket:** Synchronisierung dieser Metriken erfolgte im Rahmen **Paket 0 — Vertrauensbasis QA & Metriken** (`docs/audit/improvements/paket0_vertrauensbasis_qa_metriken_*.md`).
