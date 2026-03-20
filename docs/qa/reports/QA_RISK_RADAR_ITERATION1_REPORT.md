# QA Risk Radar – Iteration 1 Report

**Datum:** 15. März 2026  
**Status:** Abgeschlossen

---

## 1. Neu angelegte / geänderte Dateien

| Datei | Aktion |
|-------|--------|
| docs/qa/QA_RISK_RADAR.md | Neu – priorisierte Risikoübersicht |
| docs/qa/QA_RISK_RADAR_ITERATION1_REPORT.md | Neu |
| scripts/qa/checks.py | Geändert – get_top_risks(), _parse_top_risks_from_radar() |
| scripts/qa/qa_cockpit.py | Geändert – Top-3-Risiken, Risk-Radar-Verweis |

---

## 2. Bewertete Subsysteme

| Subsystem | Priorität | Kurz |
|-----------|-----------|------|
| Chat | P2 | Kernfunktion, gut abgedeckt |
| Agentensystem | P2 | Golden Path, regression |
| Prompt-System | P2 | Cross-Layer hoch |
| RAG | P1 | Restlücke ChromaDB Netzwerk |
| Debug/EventBus | P1 | Drift-Risiko EventType |
| Metrics | P3 | Gut abgedeckt |
| Startup/Bootstrap | P1 | Ollama degraded nicht getestet |
| Tools | P3 | Gut abgedeckt |
| Provider/Ollama | P2 | Restlücke Ollama offline |
| Persistenz/SQLite | P3 | Gut abgedeckt |

---

## 3. Top-3-Risikobereiche

1. **RAG** – ChromaDB Netzwerk-Fehler nicht getestet
2. **Debug/EventBus** – Drift: Neuer EventType ohne Registry/Timeline
3. **Startup/Bootstrap** – Ollama nicht erreichbar nicht getestet

---

## 4. Empfohlene nächste QA-Schwerpunkte

1. RAG: test_chroma_unreachable (Netzwerk)
2. Startup: degraded_mode ohne Ollama (falls sinnvoll)
3. Provider: Contract für Ollama-Response-Format
4. Prompt: failure_mode für Prompt-Service

---

## 5. Cockpit-Integration

✅ **Umgesetzt**

- Top-3-Risiken werden aus QA_RISK_RADAR.md gelesen
- Anzeige in docs/qa/QA_STATUS.md (Abschnitt 5)
- Verweis auf Risk Radar in Verweise (Abschnitt 7)
- Parser in scripts/qa/checks.py (_parse_top_risks_from_radar)

---

## 6. Empfehlung für Risk Radar Iteration 2

- Risiko-Scores pro Subsystem in Cockpit/JSON
- Verknüpfung Subsystem ↔ Testdomänen
- Lücken-Check: Restlücken vs. tatsächliche Tests

---

*Risk Radar Iteration 1 Report erstellt am 15. März 2026.*
