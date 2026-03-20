# Chat-Kontext – Governance

**Stand:** 2026-03-17  
**Ziel:** Architektur schriftlich festzurren – keine Magie, keine Hidden Rules, keine UI-Interpretation.

---

## 1. Grundprinzip

> **Kontext-Injektion ist eine kontrollierte Backend-Funktion.**

Die Entscheidung, ob und wie Kontext injiziert wird, liegt ausschließlich im Backend. Keine Heuristik, keine automatische Bewertung, keine LLM-Entscheidung.

---

## 2. Verboten

| Verbot | Begründung |
|--------|------------|
| UI entscheidet Kontextlogik | UI konfiguriert nur, interpretiert nie |
| Provider entscheidet Kontextlogik | Provider erhält fertige Messages |
| Implizite Auto-Erkennung von Relevanz | Keine versteckten Regeln |
| Dynamische LLM-basierte Kontextwahl | Keine KI-Entscheidung über Kontext |
| Versteckte Prompt-Zusätze außerhalb des Context-Moduls | Ein Ort für Kontext-Fragmente |

---

## 3. Erlaubt

| Erlaubt | Umsetzung |
|---------|-----------|
| Settings-gesteuerte Moduswahl | `chat_context_mode`: off, neutral, semantic |
| Settings-gesteuerte Detailtiefe | `chat_context_detail_level`: minimal, standard, full |
| Settings-gesteuerte Feldauswahl | `chat_context_include_project`, `_chat`, `_topic` |
| Reproduzierbare QA-Experimente | `run_context_experiment.py`, `run_context_matrix.py` |

---

## 4. Default-Politik

Der Default ist festgelegt durch **ADR_CHAT_CONTEXT_DEFAULT.md** und darf nur durch neuen ADR-Prozess geändert werden.

**Aktueller Default (ADR):**

- `chat_context_mode` = semantic
- `chat_context_detail_level` = standard
- `chat_context_include_project` = true
- `chat_context_include_chat` = true
- `chat_context_include_topic` = false (project_chat)

---

## 5. Änderungsregel

Ein neuer Kontextmechanismus darf nur eingeführt werden, wenn:

1. **Tests existieren** – mindestens ein Test pro neuer Kombination
2. **QA-Vergleich möglich ist** – Matrix oder Experiment-Script erweiterbar
3. **Doku aktualisiert wird** – CHAT_CONTEXT_GOVERNANCE.md, CHAT_CONTEXT_MODE_REPORT.md
4. **Keine Layerverletzung entsteht** – UI ↔ Settings ↔ ChatService ↔ Context

---

## 6. Technische Grenze

| Komponente | Verantwortung | Grenze |
|------------|---------------|--------|
| **Context-Modul** | Erzeugt nur Fragmente | Kein Settings-Zugriff, kein Logging |
| **ChatService** | Entscheidet, ob injiziert wird | Liest Settings, ruft Context |
| **Settings** | Liefern nur Konfiguration | Keine Kontextlogik |
| **UI** | Speichert nur Werte | Keine Interpretation |

---

## 7. Adaptive Context – erlaubte Form

Adaptive Kontextwahl ist **nur** erlaubt, wenn sie:

- explizit regelbasiert ist
- auf festen Profilen basiert
- durch Settings oder explizite Request-Hints gesteuert wird
- vollständig testbar ist
- im DEBUG nachvollziehbar bleibt (ChatContextResolutionTrace)

**Explizit verboten bleibt:**

- automatische Klassifikation aus Prompt-Inhalten
- LLM-basierte Kontextwahl
- heuristische Textanalyse
- versteckte Umschaltung ohne Trace

**Request-Hints** sind Aufruferentscheidungen, keine Systeminterpretation.

---

## 9. Context Compression and Budgeting

| Prinzip | Umsetzung |
|---------|-----------|
| **Compression ist regelbasiert** | truncate_text, enforce_line_limit – feste Regeln, keine Heuristik |
| **Budgeting ist policy- oder settingsgesteuert** | resolve_limits_for_policy, DEFAULT_LIMITS |
| **Keine semantische Auto-Kürzung** | Keine Relevanzbewertung, keine LLM-Entscheidung |
| **Keine LLM-basierte Verdichtung** | Nur Zeichen-/Zeilenlimits, kein Summarizing |
| **Jede Kürzung testbar und nachvollziehbar** | ChatContextResolutionTrace enthält limits_source, max_*_chars |

→ `docs/04_architecture/CHAT_CONTEXT_FAILSAFE_POLICY.md`, `docs/qa/CHAT_CONTEXT_COMPRESSION_CHECKLIST.md`

---

## 10. Explainability Guarantees

| Garantie | Umsetzung |
|----------|-----------|
| **Resolution trace attached** | `ChatContextResolutionTrace` enthält `explanation` bei jeder Kontext-Auflösung |
| **Deterministische Ausgabe** | Gleiche Inputs → gleiche Explanation (keine dynamische Sortierung) |
| **Strukturierte Warnings** | `ContextWarningEntry` mit `warning_type`, `effect`, optional `source_type`, `source_id`, `dropped_tokens` |
| **Failsafe sichtbar** | `warning_count`, `failsafe_triggered` auf `ContextExplanation`; Failsafe-Warnungen mit `effect` (removed_fragment \| skipped_injection) |

---

## 11. Observability Guarantees

| Garantie | Umsetzung |
|----------|-----------|
| **Debug-Logging grep-fähig** | Stabile Marker: `[CTX_RESOLUTION]`, `[CTX_BUDGET]`, `[CTX_SOURCES]`, `[CTX_WARN]` |
| **Kein Logging-Framework-Wechsel** | Standard-Logging, `_log.isEnabledFor(logging.DEBUG)` |
| **Serialisierung deterministisch** | `explanation_to_dict`, `trace_to_dict` – feste Feldreihenfolge, kein `__dict__`-Rekursion |

---

## 12. Non-Goals (Explainability)

| Nicht-Ziel | Begründung |
|------------|------------|
| Automatische Qualitätsbewertung | Keine versteckte Bewertung |
| UI-Anzeige der Explanation | Erklärung ist Developer-Tooling |
| Strukturiertes Logging-Framework | Keine neue Abhängigkeit |
| LLM-basierte Kontextauswahl | Governance §2 |

---

## 13. Debugging Contract

| Anforderung | Erfüllung |
|-------------|-----------|
| **QA kann nachvollziehen, warum Kontext fehlt** | `get_context_explanation()` liefert Trace mit `resolved_settings`, `ignored_inputs`, `warnings` |
| **Failsafe-Entscheidungen sichtbar** | `header_only_fragment_removed`, `marker_only_fragment_removed`, `empty_injection_prevented` mit `effect` |
| **Budget-Nachvollziehbarkeit** | `configured_budget_total`, `available_budget_for_context`, per-source `budget_used`/`budget_dropped` |
| **CLI-Inspection** | `scripts/dev/context_explain.py`, `scripts/dev/preview_context_fragment.py` |

---

## Ergebnis

- Scope-Disziplin für spätere Erweiterungen
- Schutz gegen Prompt-Wildwuchs
- Klare Verantwortlichkeiten pro Schicht
