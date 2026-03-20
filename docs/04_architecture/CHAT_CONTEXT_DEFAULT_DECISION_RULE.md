# Kontext-Default – Entscheidungsregel

**Stand:** 2026-03-17  
**Governance:** Kontext-Injektion bleibt kontrollierte Backend-Funktion. UI konfiguriert nur.

---

## 1. Bedingung für Setzen oder Ändern eines Kontext-Defaults

Ein Kontext-Default darf nur gesetzt oder geändert werden, wenn:

1. mindestens die definierten Kernfälle getestet wurden
2. mindestens 12 feste Prompts verglichen wurden
3. die Antworten manuell reviewt wurden
4. kein klarer Hinweis auf Überkontextualisierung besteht
5. die Wahl dokumentiert wurde

---

## 2. Referenzdokumente

| Dokument | Zweck |
|----------|-------|
| `docs/qa/CHAT_CONTEXT_EVALUATION_MATRIX.md` | Kernfälle (CASE_1–CASE_6) |
| `docs/qa/context_mode_experiments/CONTEXT_EVAL_DATASET.md` | 12 feste Testprompts |
| `docs/qa/context_mode_experiments/CONTEXT_EVAL_REVIEW_TEMPLATE.md` | Review-Struktur |
| `scripts/qa/run_context_matrix.py` | Experiment-Skript |

---

## 3. Aktuelle vorläufige Default-Annahme (Arbeitshypothese)

| Parameter | Wert | Hinweis |
|-----------|------|---------|
| mode | semantic | |
| detail | standard | |
| fields | all | |

**Hinweis:** Dies ist eine **Arbeitshypothese**, nicht als endgültige Wahrheit.
