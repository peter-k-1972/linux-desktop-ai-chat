# Improvement-Pakete — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** Audit 2026-03-22, Backlog IMP-001–012.

---

## Paket 0 — Vertrauensbasis QA & Metriken (P0-A)

**Ziel:** QA- und Release-Artefakte **widerspiegeln den aktuellen Stand**; keine Steuerung nach veralteten Tabellen.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-002 | `tests/TEST_AUDIT_REPORT.md` deprecaten/ersetzen; `FINAL_TEST_STATUS.md` mit aktueller Testzahl, Commit, Kommando |
| (implizit Gap) | Bei Bedarf Hinweis in `RELEASE_ACCEPTANCE_REPORT.md`-Folgeversion: „maßgebliche Zahl siehe FINAL_TEST_STATUS“ |

**Warum zusammengehörig:** Beides adressiert **Dokumentationswahrheit** für dieselbe Zielgruppe (QA/Release).

**Reihenfolge innerhalb:** (1) `FINAL_TEST_STATUS.md` aktualisieren, (2) `TEST_AUDIT_REPORT.md` Banner oder Archiv + Verweis auf `tests/README.md` / aktuelle Suites.

**Test-/QA-Bedarf:** Einmal **`pytest tests --collect-only`** (oder vollständiger Lauf) protokollieren wie im Status-Audit.

**Abnahmekriterien**

- Leser sieht **ein Datum** und **Repro-Kommando** für die genannte Testzahl.  
- `TEST_AUDIT_REPORT.md` trägt sichtbar „veraltet“ oder ist inhaltlich auf 2026+ gehoben.  
- Kein Widerspruch mehr zwischen „1681“ und gemessener Sammlung **ohne** Erklärung (Commit/Stand).

---

## Paket 1 — Irreführung eliminieren (P0-A Ergänzung)

**Ziel:** Schnelle **Pflichtkorrekturen** ohne Feature-Änderung.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-003 | `app/__main__.py`-Kommentar → `archive/run_legacy_gui.py` |

**Warum zusammen:** Kleine **D/DevEx-Pflicht** aus gleicher Quelle wie Gap-Report.

**Reihenfolge:** Einzeländerung, jederzeit parallel zu Paket 0.

**Test-/QA-Bedarf:** Keine automatisierten Tests nötig; manueller Check: Dateipfad existiert.

**Abnahmekriterien:** Kommentar/DEVELOPER_GUIDE/README konsistent mit tatsächlichem Pfad (laut Gap-Report).

---

## Paket 2 — Haupt-UI-Absicherung Chat (P0-B)

**Ziel:** **Regressionssicherheit für `ChatWorkspace`** (Operations), nicht nur Legacy-`ChatWidget`.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-001 | Neue oder erweiterte pytest-qt-/Integrationstests: Navigation zu Operations Chat, mindestens ein Kernflow (Senden, Antwort sichtbar/persistiert — wie im Golden-Path definiert, aber gegen richtige Widgets) |

**Warum zusammen:** Ein einziges **thematisches** Paket „Produkt-Chat-Pfad“.

**Reihenfolge innerhalb:** (1) Szenario spezifizieren, (2) minimale Automatisierung, (3) erweitern (Streaming optional).

**Test-/QA-Bedarf:** Hoch — dies **ist** das Paket.

**Abnahmekriterien**

- Test schlägt fehl, wenn `ChatWorkspace`-Kernflow bricht (laut Audit: bisher Golden Path nur Legacy).  
- Bestehende Suite bleibt grün (keine bewusste Absenkung von Qualität).

**Abhängigkeiten:** Paket 0 nicht zwingend technisch, aber **organisatorisch** sinnvoll zuerst (klare Metriken nach Änderungen).

---

## Paket 3 — Informationsarchitektur Dual-UI (P1-A)

**Ziel:** **Eine kanonische Erklärung:** Standard = Shell; Workbench = separater Demo-/Pilot-Pfad mit anderem Reifegrad.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-004 | `README.md`, `USER_GUIDE.md`, optional `docs/ARCHITECTURE.md` (Gap-Report §7) |

**Warum zusammen:** Gleiche **Nutzer/Maintainer-Frage**, mehrere Dateien.

**Reihenfolge:** README (sichtbarste) → USER_GUIDE → ARCHITECTURE.

**Test-/QA-Bedarf:** Optional: Link-Check manuell; keine Code-Tests.

**Abnahmekriterien:** Neuer Leser versteht **ohne Code-Lektüre**, welches Fenster „das Produkt“ ist.

---

## Paket 4 — Sprache & Touchpoints (P1-B)

**Ziel:** **Weniger DE/EN-Mix** in Navigation und Paletten (GUI-UX-Review).

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-005 | Entscheidung DE oder EN (oder Regel „UI DE, Fachbegriffe EN mit Glossar“); Umsetzung in `navigation_registry.py`-Strings und Palette-Texte laut Audit |

**Warum zusammen:** Ein **Sprachkonzept** verhindert 20 Einzel-Pullrequests ohne Rahmen.

**Reihenfolge:** (1) Regel festlegen, (2) Registry, (3) Paletten, (4) Stichprobe Runtime-Strings.

**Test-/QA-Bedarf:** Bestehende UI-Tests auf geänderte Strings prüfen; ggf. Snapshot-Anpassung.

**Abnahmekriterien:** Kein widersprüchlicher Mix **auf derselben Oberfläche** (Sidebar vs. Palette) ohne dokumentierte Ausnahme.

**Abhängigkeiten:** Paket 3 **vorher** oder parallel Start, damit Texte nicht zweimal geändert werden.

---

## Paket 5 — Diagnosefähigkeit (P2-A)

**Ziel:** Fehler in Navigations-/Breadcrumb-Pfaden nicht verschlucken.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-006 | `operations_screen.py`, `qa_governance_screen.py`: `except Exception: pass` → Logging oder engere Exceptions |

**Warum zusammen:** Gleiches **Anti-Pattern**, gleiche Wirkung.

**Reihenfolge:** Beliebig nach Wave 1.

**Test-/QA-Bedarf:** Optional Unit-Test mit provoziertem Breadcrumb-Fehler (falls testbar ohne GUI-Vollast).

**Abnahmekriterien:** Fehler erscheint in Log oder Debug-UI; kein stiller Drop.

---

## Paket 6 — Test- & Runtime-Hygiene (P2-B)

**Ziel:** Rauschen und UI-Lücken reduzieren.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-009 | aiohttp Client-Session-Lebenszyklus in Tests |
| IMP-012 | pytest-qt o. ä. für Deployment/Betrieb-Workspace über Smoke hinaus |

**Warum zusammen:** **Qualität der Testausführung** + **mehr UI-Abdeckung** Operations.

**Reihenfolge:** IMP-009 zuerst (breite Suite), IMP-012 danach (fokussiert).

**Abnahmekriterien:** Weniger/nein erwartbare stderr-Warnung laut `FINAL_TEST_STATUS.md`; neue UI-Tests grün.

---

## Paket 7 — Maintainer-Onboarding (P2-C)

**Ziel:** Ordnerzweck klar.

**Enthaltene Maßnahmen**

| ID | Maßnahme |
|----|----------|
| IMP-010 | Eintrag in `DEVELOPER_GUIDE.md` zu `app/gui_designer_dummy/` |

**Abnahmekriterien:** Suche im Repo liefert Erklärung ohne Rätselraten.

---

## Paket 8 — Große Optionen (P2-D)

**Ziel:** Nur nach Klärung der Produktrolle (Paket 3).

| ID | Thema |
|----|--------|
| IMP-007 | Workbench-Inspector: Copy „Demo“ oder echte Daten |
| IMP-008 | Packaging-Spike |
| IMP-011 | CLI Replay/Repro in GUI |

**Abnahmekriterien:** Pro ID separat definieren beim Kickoff (nicht im Audit vorab spezifiziert).

---

*Ende Paketbeschreibung.*
