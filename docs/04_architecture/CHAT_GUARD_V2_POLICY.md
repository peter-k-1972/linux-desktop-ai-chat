# Chat Guard v2 – Policy

**Stand:** 2026-03-17  
**Geltungsbereich:** Hybrid-Guard mit optionaler ML-Intent-Erkennung.

---

## 1. Rolle des Hybrid-Guards

- **v1 (Heuristik):** Primärschutz, immer aktiv
- **v2 (ML):** Ergänzend, optional über `chat_guard_ml_enabled`
- Der Guard sitzt zwischen User-Input und Modellaufruf
- Er blockiert nicht, sondern härtet Prompts und bereitet Routing vor

---

## 2. Heuristik bleibt Primärschutz

- Heuristische Erkennung läuft immer
- Bei eindeutigen Signalen (z.B. `/command`) gewinnt Heuristik
- ML darf Heuristik nicht blind überschreiben
- Bei Konflikt oder niedriger ML-Confidence: Heuristik/Fallback

---

## 3. ML nur ergänzend

- ML-Intent-Erkennung ist optional (Feature-Flag)
- ML hilft bei unklaren Fällen (Heuristik = chat)
- ML-Confidence unter Schwelle → Fallback auf Heuristik
- Keine Modellautonomie: Fusion-Regeln sind fest definiert

---

## 4. Keine unkontrollierte Modellautonomie

- Kein automatisches Überschreiben von Heuristik-Entscheidungen bei starken Signalen
- Kein Training zur Laufzeit
- Keine externen API-Aufrufe außer lokalem Ollama (Embedding)
- Entscheidungen müssen nachvollziehbar sein (decision_source, debug_dict)

---

## 5. Regeln für neue Intents

- Neue Intents: zuerst in Heuristik abbilden (Keywords/Muster)
- Intent-Beispielset für ML erweitern
- Beide Schichten (Heuristik + ML) müssen den Intent kennen
- Dokumentation in CHAT_GUARD_V2_REPORT.md aktualisieren

---

## 6. Regeln für Trainings-/Beispieldaten

- Intent-Beispiele: im Code (intent_examples.py), versionierbar
- Kein externes Training
- Beispiele: wenige, repräsentativ, sprachlich klar
- Änderungen an Beispielen: Review, keine willkürlichen Erweiterungen

---

## 7. Regeln für spätere Agenten-/Routing-Erweiterung

- `routing_hint` und `prompt_mode` sind vorbereitet
- Kein vollständiges Agenten-Routing in v2
- Erweiterungen müssen Heuristik als Fallback beibehalten
- Keine Umgehung des Guards
