# QA_ACCEPTANCE_MATRIX – Gap-Schließung Linux Desktop Chat

**Stand:** 2026-03-20  
**Verwendung:** Pro Zeile: bei Release-/Meilenstein-Abschluss **Muss erfüllt sein** mit Nachweis abhaken. Spalte **Blocker** impliziert: ohne Erfüllung keine Gesamtfreigabe (Phase 6).

---

## Matrix

| ID | Bereich | Muss erfüllt sein | Wie wird geprüft? | Testart | Freigabekriterium | Blocker |
|----|---------|-------------------|-------------------|---------|-------------------|---------|
| QA-01 | Doku: CC Agents | Doku beschreibt `AgentManagerPanel` + `AgentService`; kein aktiver `app/ui/agents`-Pfad als Ist | Manuelles Review + `rg` auf Schlüsselsätze in genannten Dateien | Review / statisch | R-DOC-01, R-DOC-02 erledigt | Ja |
| QA-02 | Doku: Command Center Pfade | Kein behaupteter Quellpfad `app/ui/command_center/*` ohne Archiv-Hinweis | `rg "app/ui/command_center" docs/` | Statisch | R-DOC-03 erledigt | Ja |
| QA-03 | Doku: DOC_GAP | BLOCKER/HIGH-Einträge ohne Ist-Bestätigung entfernt oder aktualisiert | Diff-Review `DOC_GAP_ANALYSIS.md` | Review | R-DOC-04 erledigt | Ja |
| QA-04 | Doku: README vs CC | README behauptet nicht vollständige Live-Tools/Data Stores, wenn noch Demo | Vergleich README mit `tools_panels.py` / `data_stores_panels.py` Ist | Review | R-DOC-05 + R-GUI-01/02 umgesetzt oder Fußnote | Ja |
| QA-05 | GUI: CC Tools | Kein unmarkiertes `dummy_data` als Produktivdat **oder** Nav-Eintrag entfernt **oder** verpflichtendes Demo-Banner sichtbar | UI-Walkthrough + Code-Review | Manuell + Review | R-GUI-01 + R-GUI-04 | Ja |
| QA-06 | GUI: CC Data Stores | Analog QA-05 für Stores/Health | UI-Walkthrough + Code-Review | Manuell + Review | R-GUI-02 + R-GUI-05 | Ja |
| QA-07 | GUI: Dashboard | Kein Widerspruch Docstring („Platzhalter“) vs. sichtbare „fertige“ KPI ohne Erklärung | UI-Walkthrough `DashboardScreen` | Manuell | R-GUI-03 + R-GUI-06 | Ja |
| QA-08 | Code: agents_panels | Keine doppelte kanonische `AgentRegistryPanel`-Verwechslung im CC; Exporte konsistent | `rg AgentRegistryPanel app/gui/domains/control_center` + Import-Graph | Statisch + optional Test R-TEST-06 | R-GUI-07 | Ja |
| QA-09 | GUI: Subpanels | Knowledge/Prompt/Agent-Task: kein irreführendes „(Platzhalter)“ ohne Kontext **oder** echte Daten | Stichprobe UI | Manuell | R-GUI-08–10 nach Scope | Nein* |
| QA-10 | Backend: Live-Pfade | Wenn QA-05/06 „Live“: Health/Listen stammen aus dokumentierter Quelle | Trace 1 Request in Logs oder Debugger-Dokumentation | Manuell/Integration | R-BE-01/02 | Ja** |
| QA-11 | Settings: Project/Workspace | Leerer Bereich nur mit konsistenter Doku **oder** mindestens ein persistierter Key getestet | UI + Persistenz-Neustart | Manuell / Integration | R-BE-03 | Nein* |
| QA-12 | Pipelines: Placeholder | Comfy/Media-Schritt liefert vorhersehbaren Fehler; keine stillen Erfolge | Unit-Test + ggf. kleine Pipeline-Definition | Unit | R-TEST-05 | Nein* |
| QA-13 | critic.py | TODO aufgelöst: implementiert, entfernt oder dokumentiert deaktiviert | Code-Review + `rg critic` Aufrufer | Review | R-BE-08 | Nein* |
| QA-14 | Tests: Collection | `pytest --collect-only` erfolgreich in Referenz-CI | CI-Job-Log | CI | R-TEST-01 | Ja |
| QA-15 | Tests: Regression | Chat/Kontext/Markdown/Architektur-Kernsuites grün nach Merge | CI vollständiger Test-Job | CI | R-TEST-07 | Ja |
| QA-16 | Doku: CLI/Repro | Entwickler können Repro/CLI ohne Quellcode-Lesepflicht starten | Fremdlauf: neuer Clone folgt neuer Anleitung | Manuell | R-DOC2-01 | Nein* |
| QA-17 | Doku: Archiv app/ui | Von `docs/README` erreichbare Links ohne falsche Pfade **oder** Archiv-Banner | Link-Check + Review | Statisch | R-DOC2-02 | Nein* |
| QA-18 | Freigabe | `MASTER_REMEDIATION_PLAN` §8 erfüllt; Restrisiken in Release-Note | Checkliste dieses Dokuments | Prozess | R-QA-01 | Ja |

\* **Nein** = nicht zwingend für minimale Freigabe, wenn explizit im Release als „deferred“ mit Ticket dokumentiert; für **volle** Gap-Schließung aus Audit **Ja** behandeln.  
\** **Ja** nur wenn Live-Strategie gewählt; bei Demo/Nav-Hide durch QA-05/06 abgedeckt.

---

## Empfohlene minimale Blocker-Liste (MVP-Freigabe „Audit-Gaps geschlossen – UX ehrlich“)

- QA-01, QA-02, QA-03, QA-04, QA-05, QA-06, QA-07, QA-08, QA-14, QA-15, QA-18  

## Empfohlene erweiterte Liste („vollständige“ Report-Abdeckung)

- Alle Zeilen **Blocker = Ja** sowie QA-09–QA-13, QA-16, QA-17 ohne Deferral-Tickets.

---

## Nachweisformate (objektiv)

| Prüfung | Akzeptabler Nachweis |
|---------|----------------------|
| Review | PR-Link + Review-Kommentar „QA-0x erfüllt“ |
| Statisch | CI-Job oder Paste `rg`/Exit-Code 1 = fail |
| Unit/Integration | Grüner CI-Step mit Testname |
| Manuell | Kurzes Video/Screenshot-Set oder Checklisten-PDF im Ticket |

---

*Ende QA_ACCEPTANCE_MATRIX*
