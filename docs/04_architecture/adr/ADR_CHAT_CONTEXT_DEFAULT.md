# ADR: Chat Context Default

**Stand:** 2026-03-17

---

## Status

Accepted

---

## Kontext

- Kontextsystem eingeführt
- Modi vorhanden (off, neutral, semantic)
- Detailtiefe vorhanden (minimal, standard, full)
- Feldauswahl vorhanden (project_only, project_chat, project_topic, all)
- QA-Matrix vorhanden (Matrix-Experimente, Review-Rubrik, Auswertungsskript)

---

## Entscheidungsoptionen

### Kandidat A

| Parameter | Wert |
|-----------|------|
| mode | semantic |
| detail | standard |
| fields | all |

Maximal anschlussfähig zum aktuellen System.

### Kandidat B

| Parameter | Wert |
|-----------|------|
| mode | semantic |
| detail | standard |
| fields | project_chat |

Vermutlich günstigerer Produktiv-Default, Topic oft entbehrlich.

### Kandidat C

| Parameter | Wert |
|-----------|------|
| mode | neutral |
| detail | standard |
| fields | all |

Kontrollierter, deklarativer Default mit weniger Lenkung.

---

## Bewertung

| Kandidat | Vorteile | Nachteile | Risiken |
|----------|----------|-----------|---------|
| A | Anschlussfähig, voller Kontext | Höhere Tokenlast, evtl. Ablenkung | Überkontextualisierung |
| B | Geringere Tokenlast, Topic entbehrlich | Weniger Topic-Fokus verfügbar | Unterkontextualisierung bei Topic-Prompts |
| C | Deklarativ, weniger Lenkung | Weniger semantische Steuerung | Evtl. schwächere Kontextnutzung |

**Hinweis:** Bewertung erfolgt manuell im Rahmen des QA-Vergleichs (CHAT_CONTEXT_DEFAULT_DECISION_INPUT.md, context_review_summary.json).

---

## Entscheidung

**semantic + standard + project_chat**

| Parameter | Wert |
|----------|------|
| chat_context_mode | semantic |
| chat_context_detail_level | standard |
| chat_context_include_project | true |
| chat_context_include_chat | true |
| chat_context_include_topic | false |

---

## Begründung

Basierend auf context_review_summary.json (72 Runs, 12 Prompts × 6 Cases):

**Top-2-Kandidaten (Daten):**

| Case | mode | detail | fields | kontextnutzen | ablenkung | kontextkosten |
|------|------|--------|--------|---------------|-----------|---------------|
| CASE_2 | neutral | standard | all | 3.75 | 4.75 | 3.75 |
| CASE_5 | semantic | standard | project_chat | 3.58 | 4.5 | 3.75 |

**Entscheidung für CASE_5 (semantic + standard + project_chat):**

- **Kontextnutzen 3.58:** Zweitbester Wert unter den Kontext-Cases (nach CASE_3 mit 4.17, der aber kontextkosten 2.75 hat)
- **Ablenkung 4.5:** Akzeptabel; semantic full (CASE_3) hat 4.25 und lenkt bei Basalfragen (P10–P12) stärker ab
- **Kontextkosten 3.75:** Akzeptabel; CASE_3 (full) hat 2.75 (deutlich zu viel)
- **project_chat:** Projekt + Chat decken projektbezogene Prompts (P04, P05, P06) ab; Topic entbehrlich für typischen Default-Use-Case
- **semantic:** Instruktionssatz „Berücksichtige diesen Kontext“ lenkt Modell gezielt; neutral (CASE_2) bietet keine semantische Steuerung

CASE_3 (semantic full all) hat höchsten Kontextnutzen (4.17), aber schlechteste Kontextkosten (2.75) und höchstes Ablenkungsrisiko (4.25) – für Default ungeeignet.

---

## Konsequenzen

- **Standard-Kontext:** Projekt + Chat mit semantischen Labels (Themenbereich, laufende Konversation); kein Topic
- **Tokenlast:** Geringer als all; Topic-Feld entfällt
- **Topic-Prompts (P07, P08):** Benutzer kann Topic in Settings aktivieren (chat_context_include_topic = true), wenn nötig
- **Reproduzierbar:** Matrix-Experiment, Review-Sheet und Summary dokumentieren die Datenbasis

---

## Entscheidungsgrenze

> **Eine Default-Änderung ist eine Architekturentscheidung und darf nicht implizit durch Einzeländerungen an Formatter, Settings oder UI entstehen.**

Änderungen am Default erfordern:
- explizite ADR-Aktualisierung
- QA-Vergleich und Dokumentation (CHAT_CONTEXT_GOVERNANCE.md)

---

## Konsequenzen

- **Auswirkungen auf Prompt-Struktur:** Default bestimmt, welche Kontextfragmente standardmäßig injiziert werden
- **Auswirkungen auf Debugbarkeit:** Reproduzierbare Matrix-Experimente und Review-Sheet ermöglichen Nachvollziehbarkeit
- **Auswirkungen auf Vergleichbarkeit:** Feste Kandidaten und Review-Rubrik sichern konsistente Bewertung

---

## Regel für spätere Default-Änderung

Wenn der Default später geändert wird, dann:

1. **ADR aktualisieren** – Status, Entscheidung, Begründung
2. **Report ergänzen** – CHAT_CONTEXT_MODE_REPORT.md, CHAT_CONTEXT_DEFAULT_DECISION_INPUT.md
3. **Regressionstests prüfen** – tests/chat/test_context_governance_regressions.py
4. **QA-Vergleich referenzieren** – context_review_summary.json, context_review_sheet.csv
