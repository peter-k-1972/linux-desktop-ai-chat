# Improvement-Roadmap (Waves) — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** Audit-Artefakte 2026-03-22 und Backlog IMP-001–012.

---

## Wave 1 — Pflichtkorrekturen (P0)

**Ziel:** Irreführung und **Regressionssicht** auf die **primäre Oberfläche** beheben; QA-Entscheidungen wieder auf **faktenbasierte** Artefakte stützen.

| Inhalt | IMP | Erwarteter Nutzen | Risiken |
|--------|-----|-------------------|---------|
| Test-Metriken / veraltetes Test-Audit | IMP-002 | Keine falschen „Lücken“-Listen mehr; Release-Zahlen nachvollziehbar | Gering: nur Doku, aber Redaktionsaufwand |
| Haupt-Chat-UI absichern | IMP-001 | Regressionen in `ChatWorkspace` sichtbar | Mittel: Qt/async-Tests, Wartungspflege |
| Legacy-Pfad-Kommentar | IMP-003 | Weniger Fehlstarts für Neueinsteiger | Gering |

**Abhängigkeiten:** IMP-001 kann **parallel** zu IMP-002/003 starten, sobald Szenarien feststehen; **Abnahme Wave 1** sinnvoll, wenn IMP-002+003 erledigt und IMP-001 **Mindestkriterium** erreicht (siehe Paket-Dokument).

**Risiko gesamt:** Mittel nur durch IMP-001-Technik; Doku-Teile gering.

---

## Wave 2 — Strukturelle Verbesserungen (P1)

**Ziel:** **Eine klare Nutzer- und Maintainer-Story** für „was ist das Produkt“ vs. „was ist Demo“; **Sprachkonsistenz** für primäre Touchpoints.

| Inhalt | IMP | Erwarteter Nutzen | Risiken |
|--------|-----|-------------------|---------|
| Shell vs. Workbench kommunizieren | IMP-004 | Weniger falsche Feature-Erwartungen | Gering–mittel (Texte + ggf. ein Satz im README) |
| DE/EN-Konzept für Nav/Palette | IMP-005 | Weniger kognitive Reibung | Mittel: viele String-Stellen, aber kein Architekturbruch |

**Abhängigkeiten:** **Nach** Wave 1 Doku-Klarheit (IMP-002), damit Begriffe in IMP-004/005 nicht sofort wieder veralten.

**Risiko:** Falsch verkürzte Übersetzung ohne Glossar — mitigierbar durch kleines **Begriffsverzeichnis** (ein Abschnitt in Doku, aus Audit-Empfehlung ableitbar).

---

## Wave 3 — UX-/GUI-Qualitätsrunde (C, selektiv)

**Ziel:** Erwartungskonforme Oberflächen **ohne** neue Architektur — **nach** Strukturklärung.

| Inhalt | IMP | Erwarteter Nutzen | Risiken |
|--------|-----|-------------------|---------|
| Workbench-Inspector entschärfen oder füllen | IMP-007 | Kein „scheinbar fertig“ | Hoch bei Vollimplementierung — deshalb **zuerst** nur Labels/Copy erlaubt |
| Breadcrumb-Fehler sichtbar machen | IMP-006 | Schnellere Fehlersuche | Gering |

**Abhängigkeiten:** IMP-004 vor **großem** IMP-007-Umfang; IMP-006 kann **früher** (Wave 2 Ende oder Wave 3 Start).

**Bewusst nicht in Wave 3 zuerst:** Breite **Theme-/Pixel-Politur** (Release nennt generisches UX ohne Detail — **zurückgestellt** bis P1 erledigt).

---

## Wave 4 — Doku-/QA-Synchronisierung (D + E, Rest)

**Ziel:** Nachziehen, was **nach** Code-/Test-Änderungen dokumentiert und verifiziert werden muss.

| Inhalt | IMP | Erwarteter Nutzen | Risiken |
|--------|-----|-------------------|---------|
| aiohttp Session-Cleanup | IMP-009 | Sauberere Testläufe | Mittel: Fixture-/Client-Lifecycle |
| Deployment/Betrieb UI-Tests | IMP-012 | UI-Regressionen erkennbar | Mittel |
| Designer-Dummy erklären | IMP-010 | Onboarding | Gering |
| Architektur-Doku Workbench | Gap-Report | Weniger Lücken für neue Architekten | Gering |

**Abhängigkeiten:** IMP-002 regelmäßig **aktualisieren**, wenn sich Testzahl ändert; IMP-012 nach stabilen UI-Pfaden.

---

## Wellen-Logik (kurz)

| Wave | Dauer-Charakter | Stop-Kriterium |
|------|-----------------|----------------|
| 1 | Kurz (Doku) + länger (IMP-001) | Mindest-Chat-UI-Tests grün + Doku ehrlich |
| 2 | Mittel | README/USER_GUIDE/ARCHITECTURE konsistent mit Dual-UI-Spruch |
| 3 | Variabel | Keine Stub-Texte mehr als „fertig“ lesbar **oder** explizit „Demo“ |
| 4 | Kontinuierlich | Hygiene + zusätzliche UI-Suites |

---

## Optionale Parallelspur (Release-abhängig)

- **IMP-008 Packaging:** erst wenn **Wave 1–2** abgeschlossen und Verteilungsziel feststeht (Audit: Release nennt Lücke).  
- **IMP-011 CLI in GUI:** erst wenn IMP-001 zeigt, dass Haupt-UI stabil genug für neue Eintrittspunkte ist.

---

*Ende Roadmap.*
