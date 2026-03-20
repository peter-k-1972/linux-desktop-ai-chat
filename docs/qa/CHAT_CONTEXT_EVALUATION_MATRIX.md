# Chat-Kontext – Evaluationsmatrix

**Stand:** 2026-03-17  
**Ziel:** Kontrollierte, kleine Matrix für belastbare Default-Entscheidungen.

---

## 1. Dimensionen

| Dimension | Werte | Beschreibung |
|-----------|-------|--------------|
| **mode** | off, neutral, semantic | Ob und wie Kontext injiziert wird |
| **detail** | minimal, standard, full | Umfang der semantischen Ausschmückung |
| **fields** | all, project_only, project_chat, project_topic | Welche Felder gerendert werden |

---

## 2. Keine Vollmatrix

Es wird **nicht** jede Kombination getestet.  
27 Kombinationen (3×3×3) wären unübersichtlich und wenig aussagekräftig.

---

## 3. Gezielte Kernfälle

| Case | Mode | Detail | Fields | Zweck |
|------|------|--------|--------|-------|
| **CASE 1** | off | standard | all | Basislinie ohne Kontext |
| **CASE 2** | neutral | standard | all | Deklarativer Standard |
| **CASE 3** | semantic | full | all | Maximale Kontextwirkung |
| **CASE 4** | semantic | minimal | project_only | Kleinster sinnvoller Arbeitskontext |
| **CASE 5** | semantic | standard | project_chat | Arbeitshypothese für produktiven Default-Kandidaten |
| **CASE 6** | neutral | minimal | project_only | Tokenarme Minimalvariante |

---

## 4. Mapping fields → Render-Optionen

| fields | include_project | include_chat | include_topic |
|--------|-----------------|--------------|---------------|
| all | ✓ | ✓ | ✓ |
| project_only | ✓ | ✗ | ✗ |
| project_chat | ✓ | ✓ | ✗ |
| project_topic | ✓ | ✗ | ✓ |

---

## 5. Evaluation dimensions (system quality)

| Dimension | Implementierung |
|-----------|-----------------|
| **Explainability completeness** | ContextExplanation mit sources, decisions, compressions, warnings, resolved_settings, ignored_inputs; Trace mit policy_chain |
| **Budget visibility** | configured_budget_total, effective_budget_total, available_budget_for_context, per-source budget_used/budget_dropped |
| **Dropped-context visibility** | dropped_by_source, dropped_reasons, dropped_total_tokens; per-source reason (budget_exhausted, truncated_to_budget, profile_restriction) |
| **Inspection reproducibility** | Fixture-basierte Requests, deterministischer Serializer, Snapshot-Tests für CLI-Output |

---

## 6. Ausführung

```bash
python scripts/qa/run_context_matrix.py
```

Output: `docs/qa/context_mode_experiments/context_matrix_001.json`
