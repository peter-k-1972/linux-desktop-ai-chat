# Doku–Code–Gap-Report — Linux Desktop Chat

**Datum:** 2026-03-22  
**Ziel:** Abgleich von Dokumentation, Hilfe und README mit nachweisbarem Code; Lücken und Widersprüche benennen.

---

## 1. Doku verspricht X, Code liefert Y

| X (Aussage / Erwartung) | Y (Ist im Repo) | Nachweis |
|-------------------------|-----------------|----------|
| Einheitliche „Command Palette“ als Power-User-Navigation | Zwei Paletten-Konzepte: Shell (`app/gui/commands/palette.py`, `navigation/command_palette.py`) vs. Workbench (`workbench/command_palette/command_palette_dialog.py`, englisch) | Code-Pfade |
| Inspector zeigt „live metadata, runtime state, editable configuration“ | Workbench: Hinweis-Label beschreibt Zukunft; viele Karten **stub** | `inspector_router.py` Zeilen 26–33, 133–147, … |
| „Vollständiger“ Chat-Golden-Path gemäß Test-Doku | Golden Path testet **`ChatWidget` (legacy)** | `tests/golden_path/test_chat_golden_path.py` Import Zeile 12 |
| Test-Audit beschreibt aktuellen Stand | **Datum 2025-03-15**, niedrige Testzahlen, alte Panel-Namen | `tests/TEST_AUDIT_REPORT.md` Kopf + Tabellen |
| Release/Test-Status nennt feste Testzahl 1681 | **collect-only** in Audit-Umgebung: **1838** Tests | `FINAL_TEST_STATUS.md` vs. `pytest tests --collect-only` (2026-03-22, `.venv-ci`) |

---

## 2. Veraltete oder irreführende Dokumente

| Dokument | Problem | Risiko |
|----------|---------|--------|
| `tests/TEST_AUDIT_REPORT.md` | Stand 2025-03-15, veraltete Metriken und Widget-Namen | Hohe Irreführung für QA-Leser |
| `FINAL_TEST_STATUS.md` | Testanzahl 1681 vs. aktuell höhere Sammlung | Vertrauen in Metriken |
| `app/__main__.py` Kommentar „`run_legacy_gui.py`“ | Datei liegt nur unter `archive/run_legacy_gui.py` | Fehlstart / Suche im Root |

**Hinweis:** `RELEASE_ACCEPTANCE_REPORT.md` benennt „historische Berichte“ selbst als potenziell älter — **konsistent** mit Befund.

---

## 3. Undokumentierte oder schwach dokumentierte Bereiche

| Bereich | Befund |
|---------|--------|
| `app/gui_designer_dummy/` | Kein zentraler README-Verweis im Haupt-README gefunden — **Zweck für neue Leser unklar** |
| `run_workbench_demo.py` vs. Produktstart | README nennt `python -m app`; Workbench-Demo **nicht** in README-Kernabschnitt prominent |
| Zwei Inspector-Router-Konzepte | Domain-Inspector unter `app/gui/inspector/` vs. Workbench `workbench/inspector/inspector_router.py` — in USER_GUIDE **nicht explizit getrennt** (nicht vollständig durchsucht; Lücke aus Stichprobe) |

---

## 4. Help vs. Realität

| Help-Inhalt | Abgleich |
|-------------|----------|
| `help/README.md`: semantische Doku-Suche benötigt Chroma-Index | Plausible technische Voraussetzung; **Nutzer ohne Index** haben eingeschränkte Hilfe — in Help genannt (**konsistent**) |
| Workflows, Deployment, Betrieb | Entsprechende Workspaces in `operations_screen.py` vorhanden — **grob konsistent** |

---

## 5. Überschriften ohne Tiefe

**Nicht systematisch quantifiziert.** Stichprobe: Feature-README `docs/FEATURES/README.md` wirkt als Index **angemessen**; einzelne Hilfe-Artikel wurden nicht alle Zeile für Zeile geprüft — **nicht belastbar belegt**, ob „leere“ Kapitel häufig sind.

---

## 6. Widersprüche zwischen Architektur und Nebenpfaden

- `docs/ARCHITECTURE.md` beschreibt **`app/gui/`** als GUI-Schicht — **korrekt**; erwähnt **nicht** die Workbench als separaten Anwendungsrahmen (kann als **Lücke** gelesen werden).  
- README: **Legacy-GUI** unter `archive/run_legacy_gui.py` — **stimmt** mit `glob` überein; Widerspruch nur zu `app/__main__.py`-Kommentar.

---

## 7. Empfohlene Doku-Maßnahmen (ohne Umsetzung)

1. **`app/__main__.py`:** Kommentar auf `archive/run_legacy_gui.py` korrigieren.  
2. **`tests/TEST_AUDIT_REPORT.md`:** Deprecation-Banner oder vollständige Neuauflage mit Datum und Testzählung.  
3. **`FINAL_TEST_STATUS.md`:** Testzahl mit Git-Commit und pytest-Version aktualisieren.  
4. **`README.md` / `USER_GUIDE.md`:** Abschnitt „Zwei Oberflächen: Shell (Standard) und Workbench-Demo“.  
5. **`docs/ARCHITECTURE.md`:** Optionaler Unterabschnitt Workbench vs. Domain-Shell.

---

*Ende Gap-Report.*
