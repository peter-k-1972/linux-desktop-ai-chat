# Chat-Kontext-Semantik – Analyse

**Stand:** 2026-03-17  
**Ziel:** Kontext nicht nur deklarativ, sondern semantisch wirksam für bessere Antworten.

---

## 1. Aktuelle Kontextwirkung

### 1.1 Bisheriges Format (deklarativ)

```
Kontext:
- Projekt: XYZ
- Chat: Debug Session
- Topic: API
```

### 1.2 Beobachtete Effekte

| Aspekt | Einschätzung |
|--------|--------------|
| **Modell-Reaktion** | Kontext wird oft ignoriert – reine Namensliste ohne Bedeutung |
| **Redundanz** | Keine – Kontext ist kompakt |
| **Interpretation** | Unklar, was das Modell mit Projekt/Chat/Topic anfangen soll |
| **Antwortstil** | Keine Steuerung – Modell behandelt wie beliebige Metadaten |
| **Relevanz** | Keine Anweisung, Kontext bei Antwort zu berücksichtigen |

### 1.3 Ursache

- **Nur „was“:** Kontext nennt Namen, aber nicht „wie relevant“
- **Keine Handlungsanweisung:** Modell weiß nicht, dass es den Kontext nutzen soll
- **Neutrale Formulierung:** Kein Rahmen (Arbeitskontext, Gesprächsstrang)

---

## 2. Ziel: Semantisch wirksamer Kontext

### 2.1 Erweiterung (minimal)

- **Rahmen:** „Arbeitskontext“ statt nur „Kontext“
- **Semantische Hints:** Kurze Erklärung, was jedes Element bedeutet
- **Handlungsanweisung:** Eine kurze Zeile „Berücksichtige diesen Kontext bei der Antwort.“

### 2.2 Beispiel (angereichert)

```
Arbeitskontext:
- Projekt: XYZ (Themenbereich)
- Chat: Debug Session (laufende Konversation)
- Topic: API (fokussierter Bereich)

Berücksichtige diesen Kontext bei der Antwort.
```

### 2.3 Längenvergleich

| Variante | Zeichen (Beispiel) |
|----------|---------------------|
| Neutral (aktuell) | ~55 |
| Semantisch angereichert | ~120 |

Keine Prompt-Explosion – moderater Zuwachs.

---

## 3. Risiken und Vermeidung

| Risiko | Vermeidung |
|--------|-------------|
| **Prompt-Explosion** | Nur kurze Hints, eine Zeile Anweisung |
| **Redundanz** | Keine Wiederholung, Hints einmalig |
| **Modell-spezifisch** | Generische Formulierung, kein Modell-Tuning |
| **Übersteuerung** | Subtil – Kontext berücksichtigen, nicht vorschreiben |

---

## 4. Konfigurierbarkeit (optional)

- **Semantik-Modus:** Ein/Aus für angereicherten Kontext (z.B. Setting)
- **Anweisung:** Optional weglassen, wenn zu direkt
- **Hints:** Generisch halten – (Themenbereich), (laufende Konversation), (fokussierter Bereich)

---

## 5. Empfohlene Umsetzung

1. **Rahmen:** „Arbeitskontext:“ statt „Kontext:“
2. **Hints:** In Klammern nach jedem Element
3. **Anweisung:** Eine Zeile am Ende
4. **Keine neuen Daten:** Hints sind generisch, keine DB-Erweiterung nötig
