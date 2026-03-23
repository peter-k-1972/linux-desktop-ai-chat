# Improvement-Plan — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** ausschließlich `docs/audit/PROJECT_*_2026-03-22.md` (Status, Matrix, GUI/UX-Review, Doc-Gap, Backlog).  
**Keine Implementierung** — nur Planung.

---

## Executive Summary

Die nächste Improvement-Runde soll **zuerst Vertrauen und Steuerfähigkeit** herstellen: **korrekte QA-/Status-Doku** und **Absicherung des realen Chat-Pfads (`ChatWorkspace`)** sind laut Audit **P0** und Voraussetzung, bevor sinnvoll großflächig an GUI-Politur gearbeitet wird. **P1** bündelt **strukturelle Klarheit** (Shell vs. Workbench, Sprachkonzept, falscher Legacy-Kommentar). **P2** enthält **Hygiene** (Logging statt `pass`, aiohttp, Designer-Dummy-Doku), **vertiefte Tests** (Deployment/Betrieb-UI) und **große optionale Brocken** (Workbench-Inspector-Inhalt, CLI-in-GUI, Packaging), die **nach** der Basis sinnvoll terminiert werden.

**Größter Nutzen pro Aufwand in Wave 1:** IMP-002 (klein, entirrt QA) + Start IMP-001 (groß, aber unvermeidbar für Haupt-UI). **Größter Konsistenzgewinn vor „Kosmetik“:** IMP-004 + IMP-005 (strukturell, nicht Farben).

---

## Planungsgrundlage

| Artefakt | Verwendung |
|----------|------------|
| `PROJECT_STATUS_AUDIT_2026-03-22.md` | Ist-Bewertung, Risiken, MUSS-Liste M1–M4, Top-10 |
| `PROJECT_FEATURE_STATUS_MATRIX_2026-03-22.md` | Reifegrade, GUI-Erreichbarkeit, Test-Doku-Lücken pro Bereich |
| `PROJECT_GUI_UX_REVIEW_2026-03-22.md` | Navigation, doppelte Paletten, Workbench-Reibung |
| `PROJECT_DOC_CODE_GAP_REPORT_2026-03-22.md` | Konkrete Doku↔Code-Widersprüche |
| `PROJECT_IMPROVEMENT_BACKLOG_2026-03-22.md` | IMP-001–012 mit P-Stufen |

**Vollständigkeit:** Alle genannten Dateien waren zum Planungszeitpunkt vorhanden und ausreichend inhaltlich; keine Lücken ergänzt.

---

## Leitprinzipien für die Improvement-Runde

1. **Keine UI-Politur vor Test- und Doku-Wahrheit** für den primären Nutzungspfad (Chat unter Operations).  
2. **Struktur vor Schönheit:** Zwei UI-Welten und zwei Paletten-Konzepte zuerst **benennen und dokumentieren**, dann vereinheitlichen — nicht umgekehrt.  
3. **Maßnahmen in abnehmbare Inkremente** schneiden (z. B. IMP-001: erst navigieren + eine Sende-Antwort-Runde, dann erweitern).  
4. **Workbench:** Entweder kommunizieren („Demo/Stub“) oder investieren — **nicht** stillschweigend als Produktfeature lesen lassen.  
5. **Release-Transparenz beibehalten** (`RELEASE_ACCEPTANCE_REPORT.md`): Packaging bleibt bewusst nachgelagert, bis P0/P1 erledigt sind.

---

## Klassifikation (A–E)

| Klasse | Inhalt (aus Backlog/Audit) |
|--------|------------------------------|
| **A) Pflichtkorrekturen** | IMP-001, IMP-002; IMP-003 (irreführend); inhaltlich M1–M4 aus Status-Audit |
| **B) Qualitätsverbesserungen** | IMP-004, IMP-006, IMP-009, IMP-012 |
| **C) UX-/GUI-Veredelung** | IMP-005, später gezielte Polish (Release nennt generisches UX ohne Detail — **nicht** vor P1) |
| **D) Doku-/Help** | IMP-002, IMP-003, IMP-004 (Doku-Anteil), IMP-010, Gap-Report-Punkte zu README/USER_GUIDE/ARCHITECTURE |
| **E) Test-/QA-Nachrüstung** | IMP-001, IMP-012; Verifikation nach IMP-002 |

---

## Priorisierte Verbesserungspakete (Überblick)

Siehe Detail **`PROJECT_IMPROVEMENT_PACKAGES_2026-03-22.md`**.

| Paket | Kurzname | Fokus |
|-------|----------|--------|
| **P0-A** | Vertrauensbasis QA/Doku | IMP-002, IMP-003, Teile Doku-Sync |
| **P0-B** | Haupt-UI-Absicherung | IMP-001 |
| **P1-A** | Informationsarchitektur / Dual-UI | IMP-004 (+ README/USER_GUIDE/ARCHITECTURE laut Gap-Report) |
| **P1-B** | Sprache & Navigationstexte | IMP-005 |
| **P2-A** | Diagnosefähigkeit GUI | IMP-006 |
| **P2-B** | Test-/Runtime-Hygiene | IMP-009, IMP-012 |
| **P2-C** | Onboarding Maintainer | IMP-010 |
| **P2-D** | Große optional | IMP-007, IMP-008, IMP-011 |

---

## Empfohlene Reihenfolge (fachlich)

1. **IMP-002** (schnell, entschärft falsche QA-Steuerung)  
2. **IMP-003** (schnell, irreführend)  
3. **IMP-001** starten (parallel möglich: erste Szenarien spezifizieren)  
4. **IMP-004** (Doku-first, geringes Risiko)  
5. **IMP-005** (nach IMP-004, damit Begriffe stabil sind)  
6. **IMP-006**  
7. **IMP-012** → **IMP-009** → **IMP-010**  
8. **IMP-007 / IMP-008 / IMP-011** nur nach Bedarf / Release-Ziel

---

## Bewusst zurückgestellt

Siehe **`PROJECT_DEFERRED_ITEMS_2026-03-22.md`**. Kurz: generische **Pixel-Politur**, **vollständige Workbench-Implementierung** vor Klärung der Produktrolle, **Packaging** vor P0/P1, **CLI-in-GUI** vor gesicherter Haupt-UI.

---

## Beantwortung der Zielfragen

1. **Voraussetzung für alles Weitere?** IMP-002 + IMP-003 (steuerbare, ehrliche Basis) und **laufender Abschluss** von IMP-001 für den realen Chat-Pfad.  
2. **Vor größerer GUI-Politur?** IMP-001 (fortschreitend), IMP-004, IMP-005 — sonst wird Politur auf falscher oder irrelevanter Oberfläche verschwendet.  
3. **UX-Probleme, die Struktur sind?** Zwei UI-Programme (Shell vs. Workbench), zwei Command-Paletten, Stub-Inspector vs. Nutzererwartung — siehe GUI-Review und Gap-Report.  
4. **Größter Reibungsverlust?** Verwechslung **Workbench ↔ Produkt** + **Sprachmix** + fehlende **Haupt-UI-Testabsicherung** (grüne Suite, falsches Widget).  
5. **Komplexität reduzieren?** IMP-004 (eine kanonische Story), langfristig IMP-007 (Stub entschärfen oder entfernen) — nicht gleichzeitig mit Politur erzwingen.  
6. **Bedienbarkeit ohne Architekturbruch?** IMP-005 (einheitliche Sprache in Registry-Strings/Palette), Dashboard-Hinweis auf Standardpfad (aus GUI-Review „Verbesserungspotenzial“ — **klein**, Doku/Copy).  
7. **Peinlich / gefährlich?** Veraltetes `TEST_AUDIT_REPORT.md` (falsche Prioritäten), falsche Legacy-Pfadangabe, fehlender ChatWorkspace-Test (Regression unter dem Radar).  
8. **High Impact / Low Risk?** IMP-002, IMP-003, IMP-004 (Doku), IMP-010 — siehe **`PROJECT_HIGH_IMPACT_FIXES_2026-03-22.md`**.  
9. **High Impact / High Effort, unvermeidlich?** IMP-001 (Haupt-UI-QA); optional IMP-008 wenn 1.0-Verteilung.  
10. **Nicht zuerst priorisieren?** Breite **visuelle Kosmetik**, **vollständige Workbench-Realisierung** ohne Rollenklärung, **IMP-011** vor IMP-001, **Packaging** vor Test-/Doku-P0.

---

## Top-Listen (verbindlich für diese Planung)

### Top 10 Verbesserungen insgesamt

1. IMP-001 — ChatWorkspace / Shell-Pfad testen  
2. IMP-002 — Test-Audit + Status-Zahlen synchronisieren  
3. IMP-004 — Shell vs. Workbench kommunizieren  
4. IMP-005 — Sprachkonzept  
5. IMP-003 — `__main__.py`-Legacy-Kommentar  
6. IMP-006 — Breadcrumb `pass` reduzieren  
7. IMP-012 — Deployment/Betrieb UI-Tiefe  
8. IMP-009 — aiohttp-Cleanup  
9. IMP-010 — `gui_designer_dummy` dokumentieren  
10. IMP-007 — Workbench-Stub entschärfen (nach IMP-004)

### Top 5 Pflichtkorrekturen (A)

1. IMP-002  
2. IMP-001 (fortlaufend bis Abnahmekriterium erfüllt)  
3. IMP-003  
4. Inhaltlich M2/M3 aus Status-Audit (= in IMP-002 abgedeckt)  
5. M4 (= IMP-001)

### Top 5 UX-/GUI-Verbesserungen (C, strukturell vor „Politur“)

1. IMP-004  
2. IMP-005  
3. IMP-007 (Erwartungsmanagement)  
4. Dashboard-Orientierung (Hinweis Standardpfad — aus GUI-Review, **klein**)  
5. Einheitliche Palette-Begriffe nach IMP-004/005 (Konsequenz, nicht neues Feature)

### Top 5 Test-/QA-Nachrüstungen (E)

1. IMP-001  
2. IMP-012  
3. IMP-009 (Testhygiene / Rauschen)  
4. Re-Validierung nach IMP-002 (manuelle Stichprobe laut bestehender Release-Prozesse — Audit erwähnt Checklisten)  
5. Architektur-Guards unverändert laufen lassen; keine Erweiterung **vor** IMP-001 nötig

### Top 5 Doku-/Help-Korrekturen (D)

1. IMP-002 (`TEST_AUDIT_REPORT`, `FINAL_TEST_STATUS`)  
2. IMP-003  
3. README/USER_GUIDE: zwei Oberflächen (Gap-Report §7)  
4. `docs/ARCHITECTURE.md`: optional Workbench-Unterabschnitt (Gap-Report)  
5. IMP-010

### Top 5 High-Impact / Low-Effort

1. IMP-003  
2. IMP-002 (Banner + Zahl + Commit — ohne komplette Neuschreibung des Audits)  
3. IMP-010  
4. IMP-004 (nur Doku-Welle, kein Code)  
5. IMP-006 (gezieltes Logging — kleiner Eingriff)

---

*Ende Improvement-Plan.*
