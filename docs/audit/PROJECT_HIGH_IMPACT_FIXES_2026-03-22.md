# High-Impact-Fixes — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** Audit-Artefakte; Fokus auf **hohen Nutzen** bei **kleinem bis mittlerem Aufwand** und **überschaubarem Risiko**.

---

## Kurzfristig am meisten bringt (Reihenfolge)

1. **IMP-002** — Test-Audit/Status-Zahlen ehrlich machen  
2. **IMP-003** — Legacy-Pfad-Kommentar korrigieren  
3. **IMP-004** — Shell vs. Workbench in README/USER_GUIDE (nur Doku)  
4. **IMP-010** — `gui_designer_dummy` in einem Absatz erklären  
5. **IMP-006** — Logging statt `pass` an Breadcrumb-Stellen  

Diese fünf **entschärfen Irreführung, Support-Friction und falsche Prioritäten** ohne neue Features.

---

## Maßnahmen-Tabelle (Nutzen / Aufwand / Risiko)

| ID | Kurzbeschreibung | Nutzen | Aufwand | Risiko | Abhängigkeit |
|----|------------------|--------|---------|--------|---------------|
| IMP-002 | QA-Doku vs. Realität | **hoch** | klein–mittel | gering | nein |
| IMP-003 | `__main__.py` Legacy-Pfad | mittel | **klein** | gering | nein |
| IMP-004 | Dual-UI kommunizieren | **hoch** | **klein** | gering | nein (Doku-only) |
| IMP-010 | Designer-Dummy-Doku | mittel | **klein** | gering | nein |
| IMP-006 | Breadcrumb-Fehler sichtbar | mittel | **klein** | gering | nein |
| IMP-005 | Sprachkonzept | **hoch** | mittel | mittel (viele Strings) | sinnvoll nach IMP-004 |
| IMP-009 | aiohttp Cleanup | mittel | mittel | mittel | nein |
| IMP-012 | mehr UI-Tests Deployment/Betrieb | mittel–hoch | mittel | gering | nein |

---

## High Impact / High Effort — dennoch nötig

| ID | Begründung |
|----|------------|
| **IMP-001** | Einziger Audit-Punkt, der **direkt** die **Produkt-Haupt-UI** absichert; ohne ihn bleibt „grün getestet“ semantisch trügerisch. **Unvermeidbar** für seriöse UX-/GUI-Runden danach. |

---

## Nicht in diese Liste (bewusst)

- **IMP-007** voll implementieren: hoher Aufwand; **vorher** IMP-004 (nur Label/Copy ist „high impact low effort“-Teil von IMP-007).  
- **IMP-008 / IMP-011:** groß, abhängig von Produktziel — siehe Deferred-Dokument.

---

## Empfehlung „Sprint 0“ (1–3 Tage Planungsgröße, ohne Implementierungsversprechen)

| Tagteil | Maßnahme |
|---------|----------|
| A | IMP-002 (Minimal: Banner + Status-Zahl + Commit) |
| B | IMP-003 + IMP-010 |
| C | IMP-004 (README + USER_GUIDE Kernabsatz) |
| parallel starten | IMP-001 Spezifikation + erste Tests |

---

*Ende High-Impact-Übersicht.*
