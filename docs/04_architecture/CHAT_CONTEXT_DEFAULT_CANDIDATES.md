# Kontext-Default – Kandidaten

**Stand:** 2026-03-17  
**Ziel:** Produktiven Kandidaten sauber vorbereiten. Kein sofortiger Default-Wechsel.

---

## Hinweis

**Das System trifft keine automatische Wahl eines Defaults.**  
Die Auswahl ist eine dokumentierte Architekturentscheidung nach QA-Vergleich.

---

## 1. Kandidaten

### KANDIDAT A

| Parameter | Wert |
|-----------|------|
| mode | semantic |
| detail | standard |
| fields | all |

**Begründung:** Maximal anschlussfähig zum aktuellen System.

---

### KANDIDAT B

| Parameter | Wert |
|-----------|------|
| mode | semantic |
| detail | standard |
| fields | project_chat |

**Begründung:** Vermutlich günstigerer Produktiv-Default, Topic oft entbehrlich.

---

### KANDIDAT C

| Parameter | Wert |
|-----------|------|
| mode | neutral |
| detail | standard |
| fields | all |

**Begründung:** Kontrollierter, deklarativer Default mit weniger Lenkung.

---

## 2. Entscheidungskriterien (pro Kandidat)

| Kandidat | Antwortqualität | Kontextnützlichkeit | Ablenkungsrisiko | Prompt-Länge | Debug-Nachvollziehbarkeit |
|----------|-----------------|---------------------|------------------|--------------|---------------------------|
| A | | | | | |
| B | | | | | |
| C | | | | | |

**Hinweis:** Bewertung erfolgt manuell im Rahmen des QA-Vergleichs (Matrix-Experiment, Review-Template).
