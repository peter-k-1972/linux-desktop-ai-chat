# Kontext-Review – Bewertungsrubrik

**Stand:** 2026-03-17  
**Ziel:** Manuelle Bewertung der Experimentläufe für belastbare Architekturentscheidung.  
**Governance:** Keine automatische Qualitätsbewertung, keine LLM-Selbstbewertung.

---

## Skala (1–5)

Alle Dimensionen nutzen dieselbe Skala:

| Wert | Bedeutung |
|------|-----------|
| 1 | Stark negativ / unbrauchbar |
| 2 | Eher negativ |
| 3 | Neutral / akzeptabel |
| 4 | Eher positiv |
| 5 | Stark positiv / sehr gut |

---

## 1. Fachliche Brauchbarkeit

**Definition:** Ist die Antwort des Modells fachlich sinnvoll und für die gestellte Frage brauchbar?

| Wert | Bedeutung |
|------|-----------|
| 1 | Antwort unbrauchbar: falsch, irrelevant oder nicht beantwortbar |
| 3 | Antwort akzeptabel: grundsätzlich richtig, aber lückenhaft oder ungenau |
| 5 | Antwort sehr gut: präzise, vollständig, direkt auf die Frage bezogen |

---

## 2. Kontextnützlichkeit

**Definition:** Hat der injizierte Kontext erkennbar einen positiven Einfluss auf die Antwort?

| Wert | Bedeutung |
|------|-----------|
| 1 | Kontext offensichtlich nutzlos oder schadet der Antwort |
| 3 | Kontext teils hilfreich, teils neutral – kein klarer Mehrwert erkennbar |
| 5 | Kontext klar wirksam: Antwort nutzt Projekt/Chat/Topic gezielt und sinnvoll |

---

## 3. Fokus-Treue

**Definition:** Bleibt die Antwort beim Thema oder driftet sie ab?

| Wert | Bedeutung |
|------|-----------|
| 1 | Starke Abweichung: Antwort ignoriert Fokus oder geht in irrelevante Richtung |
| 3 | Teilweise fokussiert: Kernfrage getroffen, aber unnötige Abschweifungen |
| 5 | Hohe Fokustreue: Antwort bleibt konsequent beim Thema und der Intention |

---

## 4. Ablenkungsrisiko

**Definition:** Lenkt der Kontext die Antwort in unerwünschte Richtungen oder überladen?

| Wert | Bedeutung |
|------|-----------|
| 1 | Stark ablenkend: Kontext führt zu falschen Schwerpunkten oder Überinterpretation |
| 3 | Leicht ablenkend: gelegentliche Übergewichtung von Kontextdetails |
| 5 | Kein Ablenkungsrisiko: Kontext unterstützt ohne Übersteuerung |

**Hinweis:** Niedrige Werte = hohes Ablenkungsrisiko. 5 = minimales Risiko.

---

## 5. Kontextkosten-Eindruck

**Definition:** Subjektiver Eindruck: Ist der Kontextumfang im Verhältnis zum Nutzen angemessen?

| Wert | Bedeutung |
|------|-----------|
| 1 | Deutlich zu viel: Kontext wirkt überladen, Tokenlast unverhältnismäßig |
| 3 | Akzeptabel: Umfang und Nutzen in etwa ausgewogen |
| 5 | Sehr gut dosiert: Kontext knapp und zielgerichtet, Kosten-Nutzen stimmig |

---

## Verwendung

- Eine Zeile pro Run (prompt_id + case_id + mode + detail + fields).
- Jede Dimension einzeln bewerten (1–5).
- Keine Zwischenwerte (z. B. 2.5) – bei Unsicherheit die nächste ganze Zahl wählen.
- Notiz-Spalte für Auffälligkeiten oder Begründungen nutzen.
