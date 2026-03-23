# Markdown Quality Gate

## Zweck

Markdown ist in diesem Projekt **funktional kritisch**: Hilfetexte, Chat-Darstellung und Handbuch hängen an derselben Parser-/Renderer-Pipeline wie die GUI. Fehlerhafte oder inkompatible Markdown-Dateien sind **Qualitätsmängel** (nicht „Kosmetik“).

Das Quality-Gate bündelt **lokale, reproduzierbare, deterministische** Prüfungen **ohne Netzwerk**:

1. **Struktur- und Render-Risiken** (`tools/validate_markdown_docs.py` — eingebettete Logik)
2. **Safe-Normalisierung** (`tools/normalize_markdown_docs.py` im Check-Modus)
3. **Parser-/Render-Stabilität** (zentrale Pipeline `app.gui.shared.markdown.markdown_api.render_segments`)
4. **Relative Links** (inkl. Help-Topic-IDs wie im Hilfe-Index)

Ergebnisklassen und Exit-Codes sind für CI und Skripte maschinenlesbar.

## Geprüfte Dateien

Das Gate erweitert die Validator-Suche um Demodateien:

| Bereich | Muster |
|--------|--------|
| Projektroot | `README.md`, weitere `*.md` im Root |
| Dokumentation | `docs/**/*.md` |
| Hilfe | `help/**/*.md` |
| Handbuch (Markdown) | `docs_manual/**/*.md` |
| Demos / Samples | `app/resources/demo_markdown/*.md` |

Die zugrunde liegende Sammlung entspricht im Wesentlichen `tools/validate_markdown_docs.py` plus die explizit genannten Demo-Dateien.

**Ausnahme:** `app/resources/demo_markdown/broken_markdown.md` wird **nicht** gegen den strukturellen Validator oder den Normalizer-Check gehalten (absichtlich defektes Beispiel); die **Render-Stabilität** (keine Exception, erwartete Segment-Typen) läuft weiterhin.

## Problemklassen (Kurzüberblick)

- **Codeblöcke**: ungeschlossene `` ``` ``-Fences (Blocker), Tilden-Fences `~~~` (GUI-unverträglich, typisch auto-fixbar), gemischte Öffner/Schließer
- **Tabellen**: uneinheitliche Spaltenzahl, fehlende Separator-Zeile, ASCII-/Markdown-Mischformen
- **ASCII-/CLI-Blöcke**: mehrzeilige diagrammartige Inhalte ohne Fence (mittleres Risiko für die GUI)
- **Listen / Überschriften**: Tabs, Hierarchie-Sprünge
- **Whitespace**: CRLF, Tabs, trailing Spaces in sensiblen Zeilen
- **Links**: fehlende lokale Ziele, Sprungmarken (heuristisch), Help-IDs ohne Treffer

Details und Report-Ausgabe: `docs/MARKDOWN_VALIDATION_REPORT.md` (wird vom Validator bei Bedarf erzeugt) und `docs/MARKDOWN_NORMALIZATION_REPORT.md` (Normalizer mit `--report`).

## FAIL / WARN / PASS

### FAIL (Exit `2`)

Mindestens eines:

- **Blocker** aus dem Validator (z. B. nicht geschlossener fenced Codeblock, nicht UTF-8)
- **High**, sofern **nicht** als `auto_fixable` markiert (z. B. kaputte relative Links, kritische Tabellenfehler) — im **`--profile ci`** eingeschränkt auf produktnahe Pfade (siehe oben); außerhalb davon werden diese High-Findings zu **WARN** statt **FAIL**
- **Medium** in der Kategorie `links` in **Einstiegsdateien** (strengere Pfad-/Anker-Regel)
- **Parser- oder Render-Exception** bei den Stabilitätsläufen
- **Fehlende erwartete Segment-Typen** in definierten Referenzdateien (Code-/ASCII-/Tabelle/Preformatted)

Einstiegsdateien (`ENTRY_POINT_RELS` im Skript):

- `README.md`
- `docs/README.md`
- `help/getting_started/introduction.md`
- `docs_manual/README.md`

### PASS_WITH_WARNINGS (Exit `1`)

Mindestens eines, aber **kein** FAIL-Kriterium:

- Validator-Issues mit **low**, **medium**, oder **high** mit `auto_fixable=True` (z. B. Tilden-Fence-Hinweis)
- **Safe-Normalisierung** würde Dateien ändern (`normalize_markdown_docs.py --check`)

### PASS (Exit `0`)

- Keine FAIL-Bedingungen
- Keine WARN-Bedingungen

Render-Stabilität ist **wichtiger als reine Stilfragen**: Das Gate priorisiert Exceptions, Blocker und nicht-automatisch behebbare High-Findings.

## Lokale Ausführung

```bash
# Vollausgabe inkl. WARN-Zeilen (streng: alle High nicht-auto-fixbar → FAIL)
python3 tools/run_markdown_quality_gate.py

# CI-Profil: High (nicht auto-fixbar) nur in produktnahen Pfaden als FAIL
# (help/, docs_manual/, Demos, README, docs/README, docs/01_product_overview/, docs/02_user_manual/)
python3 tools/run_markdown_quality_gate.py --profile ci

# Kompakt (vor allem FAIL-Zeilen + Summary)
python3 tools/run_markdown_quality_gate.py --quiet

# Summary zusätzlich als JSON
python3 tools/run_markdown_quality_gate.py --json /tmp/markdown_gate.json
```

**Exit-Codes**

| Code | Bedeutung |
|------|-----------|
| `0` | PASS |
| `1` | PASS_WITH_WARNINGS |
| `2` | FAIL |

**Makefile** (im Projektroot):

```bash
make markdown-check      # Quality Gate (--profile strict)
make markdown-check-ci   # Wie in CI (--profile ci)
make markdown-fix        # Nur sichere Normalisierung schreiben
```

**Kurzskript:** `tools/dev_markdown_quality.sh` (führt das Gate aus dem Repo-Root aus).

## Empfohlener Ablauf vor Commit

1. `make markdown-fix` oder `python3 tools/normalize_markdown_docs.py --fix-safe` — beseitigt sichere, idempotente Drift.
2. `make markdown-check` oder `python3 tools/run_markdown_quality_gate.py`
3. Bei **FAIL**: Validator-Meldungen beheben (Links, Tabellen, Fences), erneut laufen lassen.
4. Bei **PASS_WITH_WARNINGS**: bewusst entscheiden, ob Warnungen vor dem Merge bereinigt werden sollen.
5. Optional: `python3 tools/validate_markdown_docs.py` für den ausführlichen Report nach `docs/MARKDOWN_VALIDATION_REPORT.md`.

## Pytest

- **Klassifikations-Unit-Tests:** `tests/unit/test_markdown_quality_gate.py`
- Optionaler Marker `markdown_gate` für zukünftige Erweiterungen (siehe `pytest.ini`).

```bash
pytest tests/unit/test_markdown_quality_gate.py -q
```

## CI

Workflow: `.github/workflows/markdown-quality.yml` — führt das Gate auf `push`/`pull_request` aus (Python 3.12, `requirements.txt`, **ohne** externe Dienste).

- Es wird **`--profile ci`** verwendet: archivierte oder interne Doku unter z. B. `docs/qa/` erzeugt bei kaputten Links **WARN** statt **FAIL**.
- Exit-Code **`1` (PASS_WITH_WARNINGS)** beendet den Job **erfolgreich** (Hinweis im Log); nur **`2` (FAIL)** bricht die Pipeline ab.
- Für Release- oder Voll-Strict-Prüfung lokal: `make markdown-check` bzw. `--profile strict`.

## Verwandte Artefakte

- `tools/validate_markdown_docs.py` — strukturelle Prüfung
- `tools/normalize_markdown_docs.py` — kontrollierte Safe-Fixes
- `app/gui/shared/markdown/` — Parser, Normalizer, Segment-Builder
- `docs/architecture/MARKDOWN_RENDERING_ARCHITECTURE.md` — Render-Architektur
