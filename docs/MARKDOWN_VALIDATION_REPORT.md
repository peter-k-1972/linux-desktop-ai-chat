# MARKDOWN VALIDATION REPORT

_Generated: 2026-03-20 22:35:29 UTC — tool: `tools/validate_markdown_docs.py`_

## Summary

- **files_checked**: 395
- **issues_total**: 310
- **blockers**: 0
- **high**: 120
- **medium**: 189
- **low**: 1

## By File

### `app-tree.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/00_map_of_the_system.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/01_product_overview/architecture.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/01_product_overview/introduction.md`

- **Status**: high
- **HIGH** · `links` · Zeile 3: Lokaler Link-Ziel existiert nicht: ../help/getting_started/introduction.md (aufgelöst: docs/help/getting_started/introduction.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **MEDIUM** · `ascii_blocks` · Zeile 28: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `links` · Zeile 30: Lokaler Link-Ziel existiert nicht: ../help/operations/agents_overview.md (aufgelöst: docs/help/operations/agents_overview.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 30: Lokaler Link-Ziel existiert nicht: agents.md (aufgelöst: docs/01_product_overview/agents.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 31: Lokaler Link-Ziel existiert nicht: ../help/operations/knowledge_overview.md (aufgelöst: docs/help/operations/knowledge_overview.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 31: Lokaler Link-Ziel existiert nicht: rag.md (aufgelöst: docs/01_product_overview/rag.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 32: Lokaler Link-Ziel existiert nicht: ../help/settings/settings_overview.md (aufgelöst: docs/help/settings/settings_overview.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 32: Lokaler Link-Ziel existiert nicht: settings.md (aufgelöst: docs/01_product_overview/settings.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/01_product_overview/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/01_product_overview/UX_CONCEPT.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 697: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/02_user_manual/agents.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/ai_studio.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/media_generation.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/models.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/prompts.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/rag.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/settings.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/02_user_manual/tools.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 22: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/02_user_manual/workflows.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/03_feature_reference/CHAT_WORKSPACE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/03_feature_reference/KNOWLEDGE_WORKSPACE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/03_feature_reference/PROJECT_HUB_IMPLEMENTATION.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 65: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 58: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 63: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 68: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 73: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `headings` · Zeile 102, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **MEDIUM** · `headings` · Zeile 109, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/03_feature_reference/README.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 7: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/adr/ADR_CHAT_CONTEXT_DEFAULT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/AGENTS_UI_PHASE1_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/AGENTS_UI_PHASE1_VALIDATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/AGENTS_UI_PHASE2_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 143: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/AGENTS_UI_PHASE2_EXECUTION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/AGENTS_UI_PHASE3_STABILIZATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 164, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/04_architecture/APP_MODEL_CLUSTER_DEPENDENCY_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/APP_MOVE_MATRIX.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 24: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 160: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 229: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/04_architecture/APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/APP_REFACTOR_EXECUTION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/APP_TARGET_PACKAGE_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/APP_UI_TO_GUI_TRANSITION_PLAN.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 113: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 118: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 188: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/ARCHITECTURE_BASELINE_2026_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_DRIFT_RADAR_STATUS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_GRAPH_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 23: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 70: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 78: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 86: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/ARCHITECTURE_HEALTH_CHECK.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 84: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/ARCHITECTURE_HEALTH_CHECK_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_MAP.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_MAP_CONTRACT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_MAP_CONTRACT_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ARCHITECTURE_MAP_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/BREADCRUMB_NAVIGATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_ACTIONS_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_ACTIONS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_DEFAULT_CANDIDATES.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_DEFAULT_DECISION_INPUT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_DEFAULT_DECISION_RULE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_FAILSAFE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md`

- **Status**: high
- **MEDIUM** · `ascii_blocks` · Zeile 45: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `tables` · Zeile 112: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/04_architecture/CHAT_CONTEXT_INJECTION_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_INJECTION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_MODE_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_MODE_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 40: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 70: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/CHAT_CONTEXT_SEMANTICS_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_CONTEXT_SEMANTICS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_GUARD_V1_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_GUARD_V1_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_GUARD_V2_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_GUARD_V2_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_GUARD_V2_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_HARDENING_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 59: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/CHAT_HARDENING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_INPUT_THEME_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_INPUT_THEME_HARDENING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_MESSAGE_HEIGHT_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 43: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/CHAT_MESSAGE_RENDER_PATH_COMPARISON.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_MESSAGE_RENDERING_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_MESSAGE_RENDERING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_RESPONSE_COMPLETENESS_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `codeblocks` · Zeile 116: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.

### `docs/04_architecture/CHAT_RESPONSE_COMPLETENESS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_STREAMING_TOGGLE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_THEME_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_THEME_HARDENING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_UI_PHASE1_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_UI_PHASE2_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_UI_PHASE3_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_UI_PHASE4_SIDEPANEL_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 57: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 104: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/CHAT_UX_HARDENING_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CHAT_UX_HARDENING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 77: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/COMMAND_PALETTE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/CONTROL_CENTER_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/DESIGN_SYSTEM_LIGHT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/DOCS_ARCHITECTURE_PATH_DECISION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/EVENTBUS_GOVERNANCE_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/EVENTBUS_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/EVENTBUS_GOVERNANCE_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/FEATURE_GOVERNANCE_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/FEATURE_GOVERNANCE_GUARDS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/FEATURE_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/FULL_SYSTEM_CHECKUP_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 42: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 48: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/FULL_SYSTEM_CHECKUP_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/FULL_SYSTEM_GOVERNANCE_MATRIX.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 113: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/GUI_ARCHITECTURE_GUARDRAILS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_DOMAIN_DEPENDENCY_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_DOMAIN_DEPENDENCY_GUARDS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_GOVERNANCE_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_GOVERNANCE_GUARDS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/GUI_REPOSITORY_ARCHITECTURE.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 400: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/ICON_SYSTEM.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/LEGACY_MAIN_GOVERNANCE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/LLM_MODULE_STRUCTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/META_NAVIGATION_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 113: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 118: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 123: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 128: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/PIPELINE_ENGINE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/PIPELINE_ENGINE_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/PROJECTS_AND_CHAT_STRUCTURE_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/PROJECTS_AND_CHAT_STRUCTURE_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 82: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/PROMPT_STUDIO_CONSOLIDATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_ANALYSIS.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 83: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 37: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 51: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/04_architecture/PYSIDE6_UI_ARCHITECTURE.md`

- **Status**: high
- **MEDIUM** · `headings` · Zeile 230, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **HIGH** · `tables` · Zeile 519: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 7 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/04_architecture/QA_GOVERNANCE_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/RAG_ARCHITEKTUR.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 56, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/04_architecture/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 34: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 110: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 119: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/04_architecture/REGISTRY_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/REGISTRY_GOVERNANCE_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ROOT_CLEANUP_SPRINT_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ROOT_ENTRYPOINT_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ROOT_ENTRYPOINT_CLEANUP_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/RUNTIME_DEBUG_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/RUNTIME_LIFECYCLE_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/RUNTIME_LIFECYCLE_HARDENING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/RUNTIME_LIFECYCLE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SCREEN_CLASS_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SERVICE_GOVERNANCE_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SERVICE_GOVERNANCE_GUARDS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SERVICE_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SERVICE_LAYER_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SETTINGS_AND_WORKSPACES_HARDENING_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SETTINGS_AND_WORKSPACES_HARDENING_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SETTINGS_ARCHITECTURE.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 41: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/SETTINGS_BACKEND_DEPENDENCY_INVERSION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SETTINGS_CONSOLIDATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SIDEPANEL_SUBTREE_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEA_MIGRATION_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 29: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEB_MIGRATION_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 52: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEC_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/STARTUP_GOVERNANCE_POLICY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/STARTUP_GOVERNANCE_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 25: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/THEME_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/TOOLS_GOVERNANCE_DECISION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/TOPIC_STRUCTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 11: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 376: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 419: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 423: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_EXECUTION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/UI_MANUAL_REVIEW_FINAL_CLEANUP_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 444: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 449: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 464: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/05_developer_guide/IMPLEMENTATION_SUMMARY.md`

- **Status**: high
- **HIGH** · `links` · Zeile 4: Lokaler Link-Ziel existiert nicht: ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md (aufgelöst: docs/05_developer_guide/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/05_developer_guide/MODELS_PROVIDERS_IMPLEMENTATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/05_developer_guide/PHASE1_CHANGES.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/05_developer_guide/PROMPT_STUDIO_IMPLEMENTATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/05_developer_guide/QA_GOVERNANCE_IMPLEMENTATION.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 51: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/05_developer_guide/README.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 10: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/05_developer_guide/RUNTIME_DEBUG_IMPLEMENTATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`

- **Status**: high
- **MEDIUM** · `headings` · Zeile 197, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **HIGH** · `tables` · Zeile 199: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `links` · Zeile 227: Lokaler Link-Ziel existiert nicht: chat_sessions (aufgelöst: docs/06_operations_and_qa/chat_sessions).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **LOW** · `links` · Zeile 227: Sprungmarke „#chat_sessions“ evtl. ohne passende Überschrift in dieser Datei (Slug-Heuristik).
  - *Empfohlene Korrektur*: Überschrift oder Anker prüfen (Slug-Konvention).
- **HIGH** · `links` · Zeile 229: Lokaler Link-Ziel existiert nicht: ../../help/chat_overview.md (aufgelöst: help/chat_overview.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/06_operations_and_qa/CHAT_DELETE_BUG_FIX.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/CHAT_GLOBAL_MODE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/CHAT_LIST_PROJECT_UX.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 77, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/06_operations_and_qa/CONSOLIDATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/CONSOLIDATION_RULES.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 11: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 13: ASCII-/CLI-ähnlicher Block (8 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/06_operations_and_qa/HEADER_BUTTONS_UX.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/INTROSPECTION_PANEL_IMPLEMENTATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/KNOWLEDGE_SOURCE_EXPLORER_UX.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 74, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/06_operations_and_qa/LAYOUT_RESIZE_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/SETTINGS_UX_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_ACCEPTANCE_REVIEW_PHASE1.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_ACCEPTANCE_REVIEW_REPORT.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 90: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/06_operations_and_qa/UX_BREAK_IT_TEST_PHASE2.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 73: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 5 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 24: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 43: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_AUDIT_2_2026-03-16.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_TEST.md`

- **Status**: high
- **MEDIUM** · `ascii_blocks` · Zeile 9: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `tables` · Zeile 86: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/06_operations_and_qa/UX_DEFECTS_FINAL_KILL_SWEEP_2026-03-16.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_DEFECTS_MANUAL_TESTING.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md`

- **Status**: high
- **MEDIUM** · `headings` · Zeile 63, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **HIGH** · `tables` · Zeile 64: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/06_operations_and_qa/UX_FIXES_IMPLEMENTATION_SUMMARY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_QA_VALIDATION_PHASE4.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 109: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/06_operations_and_qa/UX_RELEASE_READINESS_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_RELEASE_READINESS_REPORT_PHASE5.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 12: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **MEDIUM** · `ascii_blocks` · Zeile 24: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 34: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 39: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 47: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 172: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 216: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/06_operations_and_qa/UX_STABILIZATION_PLAN.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 141: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/06_operations_and_qa/UX_VISUAL_HIERARCHY_IMPLEMENTATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/06_operations_and_qa/WORKSPACE_GRAPH_IMPLEMENTATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/07_troubleshooting/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/08_glossary/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_PERFORMANCE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 54: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 71: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 91: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 8 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 109: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 9 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 119: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 129: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 139: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 159: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 170: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **MEDIUM** · `headings` · Zeile 199, Spalte 1: Sprung in der Überschriftenhierarchie (H2 → H4).
  - *Empfohlene Korrektur*: Zwischenüberschrift H3 einfügen oder Ebene anpassen.
- **HIGH** · `tables` · Zeile 201: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 8 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_STATUS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/architecture/FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/architecture/MARKDOWN_RENDERING_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/architecture/README.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 10: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/AUDIT_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/CHANGELOG_NORMALIZATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/dev/CONTEXT_INSPECTION_WORKFLOW.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/DEVELOPER_GUIDE.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 129: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/DOC_DRIFT_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/DOC_GAP_ANALYSIS.md`

- **Status**: high
- **HIGH** · `links` · Zeile 29: Lokaler Link-Ziel existiert nicht: models.md (aufgelöst: docs/models.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/DOC_UPDATE_QUEUE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURE_REGISTRY.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 345: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/FEATURES/agents.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/chains.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/chat.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/context.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 27: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/FEATURES/prompts.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/providers.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/rag.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/FEATURES/settings.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 7: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **MEDIUM** · `ascii_blocks` · Zeile 34: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `codeblocks` · Zeile 42: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.

### `docs/implementation/MARKDOWN_DEMO_PANEL.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/implementation/MARKDOWN_RENDERING_INTEGRATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/MARKDOWN_NORMALIZATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/MARKDOWN_VALIDATION_REPORT.md`

- **Status**: medium
- **MEDIUM** · `codeblocks` · Zeile 37: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 127: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 133: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 135: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 137: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 139: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 149: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 175: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 232: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 234: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 236: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 267: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 273: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 275: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 277: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 283: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 354: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 382: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 384: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 425: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 446: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 508: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 510: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 526: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 582: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 584: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 600: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 641: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 667: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 669: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 671: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 673: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 694: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 843: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 864: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 870: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 886: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 907: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 909: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 911: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 913: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 929: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 931: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 933: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 960: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 966: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1012: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1018: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1060: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1072: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1089: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1120: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1138: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1140: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1142: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1144: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1146: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1148: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1236: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1257: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1279: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1300: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1647: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1659: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1671: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1673: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1715: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1725: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1737: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1739: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1997: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 1999: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2162: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2188: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2209: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2220: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2241: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2247: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2249: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2251: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2257: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2418: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 2429: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.
- **MEDIUM** · `codeblocks` · Zeile 3141: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
  - *Empfohlene Korrektur*: Backticks paaren oder Zeile in einen Codeblock legen.

### `docs/qa/00_map_of_qa_system.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/AGENT_UI_ARCHITECTURE_EVALUATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/autopilot/QA_AUTOPILOT_V2_ARCHITECTURE.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 54: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.
- **HIGH** · `tables` · Zeile 305: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 5 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/qa/architecture/autopilot/QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/autopilot/QA_AUTOPILOT_V3_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/COMMAND_CENTER_DASHBOARD_UNIFICATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/coverage/QA_COVERAGE_MAP_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/coverage/QA_COVERAGE_MAP_GENERATOR.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md`

- **Status**: high
- **HIGH** · `links` · Zeile 161: Lokaler Link-Ziel existiert nicht: QA_EVOLUTION_MAP.md (aufgelöst: docs/qa/architecture/graphs/QA_EVOLUTION_MAP.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 162: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/graphs/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 163: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/graphs/QA_RISK_RADAR.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/architecture/graphs/QA_DEPENDENCY_GRAPH.md`

- **Status**: high
- **HIGH** · `links` · Zeile 112: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/graphs/QA_RISK_RADAR.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 113: Lokaler Link-Ziel existiert nicht: ../architecture.md (aufgelöst: docs/qa/architecture/architecture.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`

- **Status**: high
- **MEDIUM** · `tables` · Zeile 364: Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.
  - *Empfohlene Korrektur*: Zwischen Kopf- und Datenzeilen eine |---|---|-Zeile einfügen.
- **HIGH** · `links` · Zeile 374: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 375: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_ARTIFACT_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 377: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/incident_replay/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 378: Lokaler Link-Ziel existiert nicht: QA_CONTROL_CENTER.md (aufgelöst: docs/qa/architecture/incident_replay/QA_CONTROL_CENTER.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 379: Lokaler Link-Ziel existiert nicht: QA_AUTOPILOT.md (aufgelöst: docs/qa/architecture/incident_replay/QA_AUTOPILOT.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`

- **Status**: high
- **HIGH** · `links` · Zeile 95: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_SCHEMA.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 126: Lokaler Link-Ziel existiert nicht: QA_REPLAY_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_REPLAY_SCHEMA.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 166: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 197: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 260: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/QA_INCIDENT_PILOT_ITERATION.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 283: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_SCHEMA.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 284: Lokaler Link-Ziel existiert nicht: QA_REPLAY_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_REPLAY_SCHEMA.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 285: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 287: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/QA_INCIDENT_PILOT_ITERATION.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 288: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_ARTIFACT_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 289: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/incident_replay/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 290: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/incident_replay/QA_RISK_RADAR.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_INTEGRATION.md`

- **Status**: high
- **HIGH** · `links` · Zeile 328: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **MEDIUM** · `tables` · Zeile 369: Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.
  - *Empfohlene Korrektur*: Zwischen Kopf- und Datenzeilen eine |---|---|-Zeile einfügen.

### `docs/qa/architecture/inventory/QA_TEST_INVENTORY_ARCHITECTURE.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 93: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/qa/architecture/inventory/QA_TEST_INVENTORY_README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/architecture/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/artifacts/dashboards/PHASE3_GAP_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md`

- **Status**: high
- **HIGH** · `links` · Zeile 96: Lokaler Link-Ziel existiert nicht: QA_STABILITY_INDEX.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **MEDIUM** · `ascii_blocks` · Zeile 96: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `links` · Zeile 97: Lokaler Link-Ziel existiert nicht: QA_SELF_HEALING.json (aufgelöst: docs/qa/artifacts/dashboards/QA_SELF_HEALING.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 98: Lokaler Link-Ziel existiert nicht: QA_STABILITY_HISTORY.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_HISTORY.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md`

- **Status**: high
- **HIGH** · `links` · Zeile 85: Lokaler Link-Ziel existiert nicht: QA_PRIORITY_SCORE.json (aufgelöst: docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **MEDIUM** · `ascii_blocks` · Zeile 85: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `links` · Zeile 86: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 88: Lokaler Link-Ziel existiert nicht: QA_STABILITY_INDEX.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 89: Lokaler Link-Ziel existiert nicht: QA_DEPENDENCY_GRAPH.md (aufgelöst: docs/qa/artifacts/dashboards/QA_DEPENDENCY_GRAPH.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md`

- **Status**: high
- **MEDIUM** · `ascii_blocks` · Zeile 53: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 97: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `links` · Zeile 104: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 105: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_INTEGRATION.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_INTEGRATION.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_EVOLUTION_MAP.md`

- **Status**: high
- **HIGH** · `links` · Zeile 91: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 92: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_HEATMAP.md`

- **Status**: high
- **HIGH** · `links` · Zeile 88: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_LEVEL3_COVERAGE_MAP.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.md`

- **Status**: high
- **HIGH** · `links` · Zeile 73: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_RISK_RADAR.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md`

- **Status**: high
- **HIGH** · `links` · Zeile 119: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **MEDIUM** · `ascii_blocks` · Zeile 119: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `links` · Zeile 120: Lokaler Link-Ziel existiert nicht: CHAOS_QA_PLAN.md (aufgelöst: docs/qa/artifacts/dashboards/CHAOS_QA_PLAN.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md`

- **Status**: high
- **HIGH** · `links` · Zeile 95: Lokaler Link-Ziel existiert nicht: QA_PRIORITY_SCORE.json (aufgelöst: docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **MEDIUM** · `ascii_blocks` · Zeile 95: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **HIGH** · `links` · Zeile 96: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 97: Lokaler Link-Ziel existiert nicht: CHAOS_QA_PLAN.md (aufgelöst: docs/qa/artifacts/dashboards/CHAOS_QA_PLAN.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 98: Lokaler Link-Ziel existiert nicht: QA_STATUS.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STATUS.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/artifacts/dashboards/QA_STATUS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 109: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 118: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/qa/artifacts/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CHAT_CONTEXT_COMPRESSION_CHECKLIST.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CHAT_CONTEXT_EVALUATION_MATRIX.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CHAT_CONTEXT_EVALUATION_TEMPLATE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CHAT_CONTEXT_PRODUCTION_CHECKLIST.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CHAT_CONTEXT_TOKEN_DISCIPLINE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/config/phase3_ci_build_order.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/config/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CONTEXT_EXPLAINABILITY_AUDIT_DELTA.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 30: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/qa/CONTEXT_EXPLAINABILITY_REMAINING_WORK_ORDER.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CONTEXT_EXPLAINABILITY_VERIFICATION_CHECKLIST.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/context_mode_experiments/CONTEXT_EVAL_DATASET.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/context_mode_experiments/CONTEXT_EVAL_REVIEW_TEMPLATE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/context_mode_experiments/CONTEXT_REVIEW_RUBRIC.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/CONTEXT_OBSERVABILITY_FAILURE_DIAGNOSTICS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/feedback_loop/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/ARCHITECTURE_DRIFT_SENTINELS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/CI_TEST_LEVELS.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 90, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **MEDIUM** · `headings` · Zeile 150, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **MEDIUM** · `headings` · Zeile 163, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/qa/governance/incident_schemas/BINDINGS_JSON_FIELD_STANDARD.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 383: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/qa/governance/incident_schemas/INCIDENT_YAML_FIELD_STANDARD.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_ANALYTICS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`

- **Status**: high
- **HIGH** · `links` · Zeile 202: Lokaler Link-Ziel existiert nicht: incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 241: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 247: Lokaler Link-Ziel existiert nicht: incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 298: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 302: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 337: Lokaler Link-Ziel existiert nicht: incidents/templates/bindings.template.json (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/bindings.template.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 356: Lokaler Link-Ziel existiert nicht: incidents/templates/notes.template.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/notes.template.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_LIFECYCLE.md`

- **Status**: high
- **HIGH** · `links` · Zeile 359: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 362: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_REGISTRY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_LIFECYCLE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md`

- **Status**: high
- **HIGH** · `links` · Zeile 337: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 345: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 347: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 348: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/governance/incident_schemas/REGRESSION_CATALOG.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 349: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/governance/incident_schemas/QA_RISK_RADAR.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/governance/incident_schemas/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md`

- **Status**: high
- **HIGH** · `links` · Zeile 357: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 365: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 367: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 368: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/QA_INCIDENT_PILOT_ITERATION.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/governance/incident_schemas/QA_VALIDATION_STANDARD.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/incident_schemas/REPLAY_YAML_FIELD_STANDARD.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/REGRESSION_CATALOG.md`

- **Status**: high
- **HIGH** · `links` · Zeile 129: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/governance/QA_INCIDENT_ARTIFACT_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 130: Lokaler Link-Ziel existiert nicht: incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 131: Lokaler Link-Ziel existiert nicht: incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 132: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 133: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md (aufgelöst: docs/qa/governance/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 134: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_INTEGRATION.md (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_INTEGRATION.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 135: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 136: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.
- **HIGH** · `links` · Zeile 137: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_SCHEMA.json (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_SCHEMA.json).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/governance/schemas/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/governance/TEST_GOVERNANCE_RULES.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_CI_INTEGRATION_PLAN.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 53, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/qa/history/phase3/PHASE3_GAP_PRIORITIZATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_IMPLEMENTATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_ORPHAN_REVIEW_GOVERNANCE.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_REPLAY_BINDING_ARCHITECTURE.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 77: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 91: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/qa/history/phase3/PHASE3_RESTRISIKEN_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_SEMANTIC_ENRICHMENT_PLAN.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_SUMMARY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/phase3/PHASE3_TECHNICAL_DOCS.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 108, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/qa/history/phase3/PHASE3_VERIFICATION_REVIEW.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/history/QA_DOCUMENTATION_STRUCTURE_PROPOSAL.md`

- **Status**: high
- **HIGH** · `links` · Zeile 299: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/history/QA_RISK_RADAR.md).
  - *Empfohlene Korrektur*: Pfad korrigieren oder Zieldatei anlegen.

### `docs/qa/history/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/incidents/QA_INCIDENT_PILOT_ITERATION.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/incidents/templates/notes.template.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/incidents/templates/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/plans/CHAOS_QA_PLAN.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/plans/QA_AUTOPILOT_V3_SANIERUNGSPLAN.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/plans/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_AUTOPILOT_V3_ARCHITECTURE_REVIEW.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_AUTOPILOT_V3_CHANGE_SUMMARY.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_AUTOPILOT_V3_FINAL_RELEASE_CHECK.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md`

- **Status**: medium
- **MEDIUM** · `headings` · Zeile 65, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.
- **MEDIUM** · `headings` · Zeile 137, Spalte 1: Sprung in der Überschriftenhierarchie (H1 → H3).
  - *Empfohlene Korrektur*: Zwischenüberschrift H2 einfügen oder Ebene anpassen.

### `docs/qa/reports/QA_AUTOPILOT_V3_VERIFICATION_REPORT.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 19: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/qa/reports/QA_COCKPIT_ITERATION2_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_COVERAGE_MAP_MAPPING_RULES.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_COVERAGE_MAP_PHASE2_PROMPTS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_COVERAGE_MAP_REVIEW.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_LEVEL3_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_RISK_RADAR_ITERATION1_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_TEST_INVENTORY_MAPPING_RULES.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/QA_TEST_INVENTORY_REVIEW.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/qa/reports/UX_DEFECTS_QA_GAP_ANALYSIS.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 45: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 4 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

### `docs/qa/RESTRUCTURING_IMPLEMENTATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/README.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 58: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/refactoring/COMMAND_CENTER_UI_TO_GUI_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/COMMAND_CENTER_UI_TO_GUI_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/GUI_POST_MIGRATION_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/GUI_POST_MIGRATION_CONSOLIDATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 20: ASCII-/CLI-ähnlicher Block (11 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/refactoring/KNOWLEDGE_UI_TO_GUI_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/PROJECT_UI_TO_GUI_ANALYSIS.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/PROJECT_UI_TO_GUI_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 20: ASCII-/CLI-ähnlicher Block (9 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/refactoring/PROMPTS_UI_TO_GUI_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/SETTINGS_UI_TO_GUI_ANALYSIS.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 21: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/refactoring/SETTINGS_UI_TO_GUI_MIGRATION_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/UI_LEGACY_FINAL_AUDIT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/refactoring/UI_LEGACY_FINAL_CLEANUP_REPORT.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs/SYSTEM_MAP.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 166: ASCII-/CLI-ähnlicher Block (6 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/TRACE_MAP.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 90: ASCII-/CLI-ähnlicher Block (6 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 132: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.
- **MEDIUM** · `ascii_blocks` · Zeile 140: ASCII-/CLI-ähnlicher Block (21 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs/USER_GUIDE.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 14: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `docs_manual/architecture.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/generated/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/index/manual_index.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/agents/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/chains/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/chat/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/context/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/gui/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/prompts/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/providers/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/rag/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/modules/settings/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/roles/admin/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/roles/business/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/roles/entwickler/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/roles/fachanwender/README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/standards.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/templates/module_template.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/templates/role_template.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/templates/workflow_template.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/workflows/agent_usage.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/workflows/chat_usage.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/workflows/context_control.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `docs_manual/workflows/settings_usage.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/control_center/cc_data_stores.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/control_center/cc_models.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/control_center/cc_providers.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/control_center/cc_tools.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/control_center/control_center_agents.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/control_center/control_center_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/getting_started/introduction.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 36: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `help/operations/agents_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/operations/chat_overview.md`

- **Status**: medium
- **MEDIUM** · `ascii_blocks` · Zeile 43: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
  - *Empfohlene Korrektur*: Als ```-Codeblock oder eingerückten Block (4 Spaces) kennzeichnen.

### `help/operations/knowledge_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/operations/projects_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/operations/prompt_studio_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/qa_governance/qa_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/runtime_debug/runtime_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/settings/settings_chat_context.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/settings/settings_overview.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/settings/settings_prompts.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/settings/settings_rag.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `help/troubleshooting/troubleshooting.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `README.md`

- **Status**: ok
- Keine festgestellten Probleme in den geprüften Kategorien.

### `SIDEBAR_IMPLEMENTATION.md`

- **Status**: high
- **HIGH** · `tables` · Zeile 7: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
  - *Empfohlene Korrektur*: Jede Zeile auf gleiche Anzahl | … | Zellen bringen.

## By Problem Type

### codeblocks

- `docs/04_architecture/CHAT_RESPONSE_COMPLETENESS_ANALYSIS.md` Zeile 116 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 37 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 127 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 133 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 135 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 137 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 139 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 149 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 175 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 232 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 234 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 236 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 267 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 273 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 275 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 277 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 283 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 354 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 382 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 384 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 425 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 446 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 508 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 510 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 526 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 582 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 584 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 600 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 641 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 667 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 669 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 671 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 673 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 694 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 843 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 864 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 870 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 886 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 907 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 909 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 911 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 913 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 929 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 931 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 933 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 960 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 966 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1012 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1018 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1060 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1072 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1089 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1120 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1138 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1140 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1142 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1144 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1146 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1148 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1236 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1257 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1279 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1300 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1647 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1659 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1671 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1673 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1715 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1725 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1737 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1739 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1997 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 1999 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2162 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2188 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2209 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2220 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2241 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2247 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2249 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2251 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2257 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2418 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 2429 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md` Zeile 3141 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md` Zeile 42 — **medium**: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.

### tables

- `SIDEBAR_IMPLEMENTATION.md` Zeile 7 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/01_product_overview/UX_CONCEPT.md` Zeile 697 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/02_user_manual/tools.md` Zeile 22 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/APP_MOVE_MATRIX.md` Zeile 24 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/04_architecture/APP_MOVE_MATRIX.md` Zeile 160 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/04_architecture/APP_MOVE_MATRIX.md` Zeile 229 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md` Zeile 112 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_ANALYSIS.md` Zeile 83 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md` Zeile 37 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md` Zeile 51 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/PYSIDE6_UI_ARCHITECTURE.md` Zeile 519 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 7 Zellen).
- `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md` Zeile 34 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md` Zeile 110 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md` Zeile 119 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` Zeile 199 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/06_operations_and_qa/UX_BREAK_IT_TEST_PHASE2.md` Zeile 73 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 5 vs. 6 Zellen).
- `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md` Zeile 43 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_TEST.md` Zeile 86 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md` Zeile 64 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 12 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/06_operations_and_qa/UX_STABILIZATION_PLAN.md` Zeile 141 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 54 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 71 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 91 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 8 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 109 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 9 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 119 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 129 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 139 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 159 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 170 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 201 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 8 Zellen).
- `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md` Zeile 7 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md` Zeile 30 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/qa/architecture/autopilot/QA_AUTOPILOT_V2_ARCHITECTURE.md` Zeile 54 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/qa/architecture/autopilot/QA_AUTOPILOT_V2_ARCHITECTURE.md` Zeile 305 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 5 Zellen).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md` Zeile 364 — **medium**: Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_INTEGRATION.md` Zeile 369 — **medium**: Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.
- `docs/qa/architecture/inventory/QA_TEST_INVENTORY_ARCHITECTURE.md` Zeile 93 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/qa/governance/incident_schemas/BINDINGS_JSON_FIELD_STANDARD.md` Zeile 383 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/qa/reports/QA_AUTOPILOT_V3_VERIFICATION_REPORT.md` Zeile 19 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/qa/reports/UX_DEFECTS_QA_GAP_ANALYSIS.md` Zeile 45 — **high**: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 4 Zellen).

### ascii_blocks

- `docs/01_product_overview/introduction.md` Zeile 28 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_HUB_IMPLEMENTATION.md` Zeile 65 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md` Zeile 58 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md` Zeile 63 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md` Zeile 68 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md` Zeile 73 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/README.md` Zeile 7 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/AGENTS_UI_PHASE2_ANALYSIS.md` Zeile 143 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md` Zeile 113 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md` Zeile 118 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md` Zeile 188 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GRAPH_REPORT.md` Zeile 23 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md` Zeile 70 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md` Zeile 78 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md` Zeile 86 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_HEALTH_CHECK.md` Zeile 84 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md` Zeile 45 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_CONTEXT_REPORT.md` Zeile 40 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_CONTEXT_REPORT.md` Zeile 70 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_HARDENING_ANALYSIS.md` Zeile 59 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_MESSAGE_HEIGHT_ANALYSIS.md` Zeile 43 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_UI_PHASE4_SIDEPANEL_REPORT.md` Zeile 57 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_UI_PHASE4_SIDEPANEL_REPORT.md` Zeile 104 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md` Zeile 77 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/FULL_SYSTEM_CHECKUP_ANALYSIS.md` Zeile 42 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/FULL_SYSTEM_CHECKUP_ANALYSIS.md` Zeile 48 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md` Zeile 113 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/GUI_REPOSITORY_ARCHITECTURE.md` Zeile 400 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md` Zeile 113 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md` Zeile 118 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md` Zeile 123 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md` Zeile 128 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PROJECTS_AND_CHAT_STRUCTURE_REPORT.md` Zeile 82 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/SETTINGS_ARCHITECTURE.md` Zeile 41 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEA_MIGRATION_REPORT.md` Zeile 29 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEB_MIGRATION_REPORT.md` Zeile 52 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/STARTUP_GOVERNANCE_REPORT.md` Zeile 25 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md` Zeile 11 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md` Zeile 376 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md` Zeile 419 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md` Zeile 423 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md` Zeile 444 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md` Zeile 449 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md` Zeile 464 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/05_developer_guide/QA_GOVERNANCE_IMPLEMENTATION.md` Zeile 51 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/05_developer_guide/README.md` Zeile 10 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/CONSOLIDATION_RULES.md` Zeile 11 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md` Zeile 13 — **medium**: ASCII-/CLI-ähnlicher Block (8 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_ACCEPTANCE_REVIEW_REPORT.md` Zeile 90 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md` Zeile 24 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_TEST.md` Zeile 9 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_QA_VALIDATION_PHASE4.md` Zeile 109 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 24 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 34 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 39 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 47 — **medium**: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 172 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md` Zeile 216 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/DEVELOPER_GUIDE.md` Zeile 129 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/FEATURES/context.md` Zeile 27 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/FEATURE_REGISTRY.md` Zeile 345 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/README.md` Zeile 58 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/SYSTEM_MAP.md` Zeile 166 — **medium**: ASCII-/CLI-ähnlicher Block (6 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/TRACE_MAP.md` Zeile 90 — **medium**: ASCII-/CLI-ähnlicher Block (6 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/TRACE_MAP.md` Zeile 132 — **medium**: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/TRACE_MAP.md` Zeile 140 — **medium**: ASCII-/CLI-ähnlicher Block (21 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/USER_GUIDE.md` Zeile 14 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/architecture/README.md` Zeile 10 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md` Zeile 34 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md` Zeile 96 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md` Zeile 85 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md` Zeile 53 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md` Zeile 97 — **medium**: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md` Zeile 119 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md` Zeile 95 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_STATUS.md` Zeile 109 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_STATUS.md` Zeile 118 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/history/phase3/PHASE3_REPLAY_BINDING_ARCHITECTURE.md` Zeile 77 — **medium**: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/history/phase3/PHASE3_REPLAY_BINDING_ARCHITECTURE.md` Zeile 91 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md` Zeile 20 — **medium**: ASCII-/CLI-ähnlicher Block (11 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md` Zeile 20 — **medium**: ASCII-/CLI-ähnlicher Block (9 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/refactoring/SETTINGS_UI_TO_GUI_ANALYSIS.md` Zeile 21 — **medium**: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `help/getting_started/introduction.md` Zeile 36 — **medium**: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `help/operations/chat_overview.md` Zeile 43 — **medium**: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.

### lists

_Keine Treffer._

### headings

- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md` Zeile 102:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md` Zeile 109:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md` Zeile 164:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/04_architecture/PYSIDE6_UI_ARCHITECTURE.md` Zeile 230:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/04_architecture/RAG_ARCHITEKTUR.md` Zeile 56:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` Zeile 197:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/CHAT_LIST_PROJECT_UX.md` Zeile 77:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/KNOWLEDGE_SOURCE_EXPLORER_UX.md` Zeile 74:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md` Zeile 63:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md` Zeile 199:1 — **medium**: Sprung in der Überschriftenhierarchie (H2 → H4).
- `docs/qa/governance/CI_TEST_LEVELS.md` Zeile 90:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/governance/CI_TEST_LEVELS.md` Zeile 150:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/governance/CI_TEST_LEVELS.md` Zeile 163:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/history/phase3/PHASE3_CI_INTEGRATION_PLAN.md` Zeile 53:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/history/phase3/PHASE3_TECHNICAL_DOCS.md` Zeile 108:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/reports/QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md` Zeile 65:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/reports/QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md` Zeile 137:1 — **medium**: Sprung in der Überschriftenhierarchie (H1 → H3).

### whitespace

_Keine Treffer._

### links

- `docs/01_product_overview/introduction.md` Zeile 3 — **high**: Lokaler Link-Ziel existiert nicht: ../help/getting_started/introduction.md (aufgelöst: docs/help/getting_started/introduction.md).
- `docs/01_product_overview/introduction.md` Zeile 30 — **high**: Lokaler Link-Ziel existiert nicht: ../help/operations/agents_overview.md (aufgelöst: docs/help/operations/agents_overview.md).
- `docs/01_product_overview/introduction.md` Zeile 30 — **high**: Lokaler Link-Ziel existiert nicht: agents.md (aufgelöst: docs/01_product_overview/agents.md).
- `docs/01_product_overview/introduction.md` Zeile 31 — **high**: Lokaler Link-Ziel existiert nicht: ../help/operations/knowledge_overview.md (aufgelöst: docs/help/operations/knowledge_overview.md).
- `docs/01_product_overview/introduction.md` Zeile 31 — **high**: Lokaler Link-Ziel existiert nicht: rag.md (aufgelöst: docs/01_product_overview/rag.md).
- `docs/01_product_overview/introduction.md` Zeile 32 — **high**: Lokaler Link-Ziel existiert nicht: ../help/settings/settings_overview.md (aufgelöst: docs/help/settings/settings_overview.md).
- `docs/01_product_overview/introduction.md` Zeile 32 — **high**: Lokaler Link-Ziel existiert nicht: settings.md (aufgelöst: docs/01_product_overview/settings.md).
- `docs/05_developer_guide/IMPLEMENTATION_SUMMARY.md` Zeile 4 — **high**: Lokaler Link-Ziel existiert nicht: ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md (aufgelöst: docs/05_developer_guide/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` Zeile 227 — **high**: Lokaler Link-Ziel existiert nicht: chat_sessions (aufgelöst: docs/06_operations_and_qa/chat_sessions).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` Zeile 227 — **low**: Sprungmarke „#chat_sessions“ evtl. ohne passende Überschrift in dieser Datei (Slug-Heuristik).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md` Zeile 229 — **high**: Lokaler Link-Ziel existiert nicht: ../../help/chat_overview.md (aufgelöst: help/chat_overview.md).
- `docs/DOC_GAP_ANALYSIS.md` Zeile 29 — **high**: Lokaler Link-Ziel existiert nicht: models.md (aufgelöst: docs/models.md).
- `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md` Zeile 161 — **high**: Lokaler Link-Ziel existiert nicht: QA_EVOLUTION_MAP.md (aufgelöst: docs/qa/architecture/graphs/QA_EVOLUTION_MAP.md).
- `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md` Zeile 162 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/graphs/REGRESSION_CATALOG.md).
- `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md` Zeile 163 — **high**: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/graphs/QA_RISK_RADAR.md).
- `docs/qa/architecture/graphs/QA_DEPENDENCY_GRAPH.md` Zeile 112 — **high**: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/graphs/QA_RISK_RADAR.md).
- `docs/qa/architecture/graphs/QA_DEPENDENCY_GRAPH.md` Zeile 113 — **high**: Lokaler Link-Ziel existiert nicht: ../architecture.md (aufgelöst: docs/qa/architecture/architecture.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md` Zeile 374 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md` Zeile 375 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_ARTIFACT_STANDARD.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md` Zeile 377 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/incident_replay/REGRESSION_CATALOG.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md` Zeile 378 — **high**: Lokaler Link-Ziel existiert nicht: QA_CONTROL_CENTER.md (aufgelöst: docs/qa/architecture/incident_replay/QA_CONTROL_CENTER.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md` Zeile 379 — **high**: Lokaler Link-Ziel existiert nicht: QA_AUTOPILOT.md (aufgelöst: docs/qa/architecture/incident_replay/QA_AUTOPILOT.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 95 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 126 — **high**: Lokaler Link-Ziel existiert nicht: QA_REPLAY_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_REPLAY_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 166 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 197 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 260 — **high**: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/QA_INCIDENT_PILOT_ITERATION.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 283 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 284 — **high**: Lokaler Link-Ziel existiert nicht: QA_REPLAY_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_REPLAY_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 285 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 287 — **high**: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/QA_INCIDENT_PILOT_ITERATION.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 288 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_ARTIFACT_STANDARD.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 289 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/incident_replay/REGRESSION_CATALOG.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md` Zeile 290 — **high**: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/incident_replay/QA_RISK_RADAR.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_INTEGRATION.md` Zeile 328 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md).
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md` Zeile 96 — **high**: Lokaler Link-Ziel existiert nicht: QA_STABILITY_INDEX.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.json).
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md` Zeile 97 — **high**: Lokaler Link-Ziel existiert nicht: QA_SELF_HEALING.json (aufgelöst: docs/qa/artifacts/dashboards/QA_SELF_HEALING.json).
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md` Zeile 98 — **high**: Lokaler Link-Ziel existiert nicht: QA_STABILITY_HISTORY.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_HISTORY.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md` Zeile 85 — **high**: Lokaler Link-Ziel existiert nicht: QA_PRIORITY_SCORE.json (aufgelöst: docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md` Zeile 86 — **high**: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md` Zeile 88 — **high**: Lokaler Link-Ziel existiert nicht: QA_STABILITY_INDEX.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md` Zeile 89 — **high**: Lokaler Link-Ziel existiert nicht: QA_DEPENDENCY_GRAPH.md (aufgelöst: docs/qa/artifacts/dashboards/QA_DEPENDENCY_GRAPH.md).
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md` Zeile 104 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md` Zeile 105 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_INTEGRATION.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_INTEGRATION.md).
- `docs/qa/artifacts/dashboards/QA_EVOLUTION_MAP.md` Zeile 91 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
- `docs/qa/artifacts/dashboards/QA_EVOLUTION_MAP.md` Zeile 92 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/artifacts/dashboards/QA_HEATMAP.md` Zeile 88 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
- `docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.md` Zeile 73 — **high**: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
- `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md` Zeile 119 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
- `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md` Zeile 120 — **high**: Lokaler Link-Ziel existiert nicht: CHAOS_QA_PLAN.md (aufgelöst: docs/qa/artifacts/dashboards/CHAOS_QA_PLAN.md).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md` Zeile 95 — **high**: Lokaler Link-Ziel existiert nicht: QA_PRIORITY_SCORE.json (aufgelöst: docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.json).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md` Zeile 96 — **high**: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md` Zeile 97 — **high**: Lokaler Link-Ziel existiert nicht: CHAOS_QA_PLAN.md (aufgelöst: docs/qa/artifacts/dashboards/CHAOS_QA_PLAN.md).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md` Zeile 98 — **high**: Lokaler Link-Ziel existiert nicht: QA_STATUS.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STATUS.json).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 129 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/governance/QA_INCIDENT_ARTIFACT_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 130 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 131 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 132 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 133 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md (aufgelöst: docs/qa/governance/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 134 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_INTEGRATION.md (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_INTEGRATION.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 135 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 136 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/REGRESSION_CATALOG.md` Zeile 137 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_SCHEMA.json (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_SCHEMA.json).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 202 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 241 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 247 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 298 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 302 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 337 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/bindings.template.json (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/bindings.template.json).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md` Zeile 356 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/notes.template.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/notes.template.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_LIFECYCLE.md` Zeile 359 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_LIFECYCLE.md` Zeile 362 — **high**: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md` Zeile 337 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md` Zeile 345 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md` Zeile 347 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md` Zeile 348 — **high**: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/governance/incident_schemas/REGRESSION_CATALOG.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md` Zeile 349 — **high**: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/governance/incident_schemas/QA_RISK_RADAR.md).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md` Zeile 357 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md` Zeile 365 — **high**: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md` Zeile 367 — **high**: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md` Zeile 368 — **high**: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/QA_INCIDENT_PILOT_ITERATION.md).
- `docs/qa/history/QA_DOCUMENTATION_STRUCTURE_PROPOSAL.md` Zeile 299 — **high**: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/history/QA_RISK_RADAR.md).

## Quick Fix Candidates

### Automatisch normalisierbar

_Keine._

### Manuell prüfen

- `SIDEBAR_IMPLEMENTATION.md`:7 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/01_product_overview/UX_CONCEPT.md`:697 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/01_product_overview/introduction.md`:3 — **high** / links: Lokaler Link-Ziel existiert nicht: ../help/getting_started/introduction.md (aufgelöst: docs/help/getting_started/introduction.md).
- `docs/01_product_overview/introduction.md`:28 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/01_product_overview/introduction.md`:30 — **high** / links: Lokaler Link-Ziel existiert nicht: ../help/operations/agents_overview.md (aufgelöst: docs/help/operations/agents_overview.md).
- `docs/01_product_overview/introduction.md`:30 — **high** / links: Lokaler Link-Ziel existiert nicht: agents.md (aufgelöst: docs/01_product_overview/agents.md).
- `docs/01_product_overview/introduction.md`:31 — **high** / links: Lokaler Link-Ziel existiert nicht: ../help/operations/knowledge_overview.md (aufgelöst: docs/help/operations/knowledge_overview.md).
- `docs/01_product_overview/introduction.md`:31 — **high** / links: Lokaler Link-Ziel existiert nicht: rag.md (aufgelöst: docs/01_product_overview/rag.md).
- `docs/01_product_overview/introduction.md`:32 — **high** / links: Lokaler Link-Ziel existiert nicht: ../help/settings/settings_overview.md (aufgelöst: docs/help/settings/settings_overview.md).
- `docs/01_product_overview/introduction.md`:32 — **high** / links: Lokaler Link-Ziel existiert nicht: settings.md (aufgelöst: docs/01_product_overview/settings.md).
- `docs/02_user_manual/tools.md`:22 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/03_feature_reference/PROJECT_HUB_IMPLEMENTATION.md`:65 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`:58 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`:63 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`:68 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`:73 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`:102 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/03_feature_reference/PROJECT_SWITCHER_AND_OVERVIEW.md`:109 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/03_feature_reference/README.md`:7 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/AGENTS_UI_PHASE2_ANALYSIS.md`:143 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/APP_CORE_DECOUPLING_PLAN.md`:164 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/04_architecture/APP_MOVE_MATRIX.md`:24 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/04_architecture/APP_MOVE_MATRIX.md`:160 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/04_architecture/APP_MOVE_MATRIX.md`:229 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md`:113 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md`:118 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_BASELINE_2026.md`:188 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GRAPH_REPORT.md`:23 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`:70 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`:78 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_GUARD_RULES.md`:86 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/ARCHITECTURE_HEALTH_CHECK.md`:84 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md`:45 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_CONTEXT_GOVERNANCE.md`:112 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/CHAT_CONTEXT_REPORT.md`:40 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_CONTEXT_REPORT.md`:70 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_HARDENING_ANALYSIS.md`:59 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_MESSAGE_HEIGHT_ANALYSIS.md`:43 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_RESPONSE_COMPLETENESS_ANALYSIS.md`:116 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/04_architecture/CHAT_UI_PHASE4_SIDEPANEL_REPORT.md`:57 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/CHAT_UI_PHASE4_SIDEPANEL_REPORT.md`:104 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md`:77 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/FULL_SYSTEM_CHECKUP_ANALYSIS.md`:42 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/FULL_SYSTEM_CHECKUP_ANALYSIS.md`:48 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/FULL_SYSTEM_RESTPOINT_REMEDIATION_REPORT.md`:113 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/GUI_REPOSITORY_ARCHITECTURE.md`:400 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md`:113 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md`:118 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md`:123 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PIPELINE_ENGINE_ANALYSIS.md`:128 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PROJECTS_AND_CHAT_STRUCTURE_REPORT.md`:82 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_ANALYSIS.md`:83 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md`:37 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_REPORT.md`:51 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/PYSIDE6_UI_ARCHITECTURE.md`:230 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/04_architecture/PYSIDE6_UI_ARCHITECTURE.md`:519 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 7 Zellen).
- `docs/04_architecture/RAG_ARCHITEKTUR.md`:56 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md`:34 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md`:110 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/04_architecture/REGISTRY_GOVERNANCE_ANALYSIS.md`:119 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/04_architecture/SETTINGS_ARCHITECTURE.md`:41 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEA_MIGRATION_REPORT.md`:29 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/SIDEPANEL_SUBTREE_PHASEB_MIGRATION_REPORT.md`:52 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/STARTUP_GOVERNANCE_REPORT.md`:25 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md`:11 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md`:376 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md`:419 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/UI_COMPATIBILITY_CLEANUP_AUDIT.md`:423 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md`:444 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md`:449 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/04_architecture/WORKSPACE_IMPLEMENTATION_PLAN.md`:464 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/05_developer_guide/IMPLEMENTATION_SUMMARY.md`:4 — **high** / links: Lokaler Link-Ziel existiert nicht: ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md (aufgelöst: docs/05_developer_guide/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md).
- `docs/05_developer_guide/QA_GOVERNANCE_IMPLEMENTATION.md`:51 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/05_developer_guide/README.md`:10 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`:197 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`:199 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`:227 — **high** / links: Lokaler Link-Ziel existiert nicht: chat_sessions (aufgelöst: docs/06_operations_and_qa/chat_sessions).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`:227 — **low** / links: Sprungmarke „#chat_sessions“ evtl. ohne passende Überschrift in dieser Datei (Slug-Heuristik).
- `docs/06_operations_and_qa/ARCHITECTURE_PROPOSAL_REPOSITORY_DOCS_HELP.md`:229 — **high** / links: Lokaler Link-Ziel existiert nicht: ../../help/chat_overview.md (aufgelöst: help/chat_overview.md).
- `docs/06_operations_and_qa/CHAT_LIST_PROJECT_UX.md`:77 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/CONSOLIDATION_RULES.md`:11 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/DOCS_HELP_IMPLEMENTATION_REPORT.md`:13 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (8 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/KNOWLEDGE_SOURCE_EXPLORER_UX.md`:74 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/UX_ACCEPTANCE_REVIEW_REPORT.md`:90 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_BREAK_IT_TEST_PHASE2.md`:73 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 5 vs. 6 Zellen).
- `docs/06_operations_and_qa/UX_BUG_FIXES_PHASE3.md`:24 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_AUDIT_2026-03-16.md`:43 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_TEST.md`:9 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_DEFECTS_BEHAVIOR_TEST.md`:86 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md`:63 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/06_operations_and_qa/UX_EMPTY_STATE_IMPLEMENTATION.md`:64 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/06_operations_and_qa/UX_QA_VALIDATION_PHASE4.md`:109 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:12 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:24 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:34 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:39 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:47 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:172 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_IMPLEMENTATION_LOG.md`:216 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/06_operations_and_qa/UX_STABILIZATION_PLAN.md`:141 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/DEVELOPER_GUIDE.md`:129 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/DOC_GAP_ANALYSIS.md`:29 — **high** / links: Lokaler Link-Ziel existiert nicht: models.md (aufgelöst: docs/models.md).
- `docs/FEATURES/context.md`:27 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/FEATURE_REGISTRY.md`:345 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:37 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:127 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:133 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:135 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:137 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:139 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:149 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:175 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:232 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:234 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:236 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:267 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:273 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:275 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:277 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:283 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:354 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:382 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:384 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:425 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:446 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:508 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:510 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:526 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:582 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:584 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:600 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:641 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:667 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:669 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:671 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:673 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:694 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:843 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:864 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:870 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:886 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:907 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:909 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:911 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:913 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:929 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:931 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:933 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:960 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:966 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1012 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1018 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1060 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1072 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1089 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1120 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1138 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1140 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1142 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1144 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1146 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1148 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1236 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1257 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1279 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1300 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1647 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1659 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1671 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1673 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1715 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1725 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1737 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1739 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1997 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:1999 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2162 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2188 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2209 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2220 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2241 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2247 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2249 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2251 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2257 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2418 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:2429 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/MARKDOWN_VALIDATION_REPORT.md`:3141 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/README.md`:58 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/SYSTEM_MAP.md`:166 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (6 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/TRACE_MAP.md`:90 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (6 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/TRACE_MAP.md`:132 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/TRACE_MAP.md`:140 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (21 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/USER_GUIDE.md`:14 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:54 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:71 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:91 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 8 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:109 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 9 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:119 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:129 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:139 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:159 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:170 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 7 Zellen).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:199 — **medium** / headings: Sprung in der Überschriftenhierarchie (H2 → H4).
- `docs/architecture/CHAT_CONTEXT_EXPLAINABILITY_SCHEMA.md`:201 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 8 Zellen).
- `docs/architecture/README.md`:10 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md`:7 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md`:34 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/implementation/MARKDOWN_BLOCK_VALIDATION.md`:42 — **medium** / codeblocks: Ungerade Anzahl von Backticks in der Zeile — Inline-Code oder Abschluss evtl. kaputt.
- `docs/qa/CONTEXT_EXPLAINABILITY_GAP_MATRIX.md`:30 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 8 vs. 9 Zellen).
- `docs/qa/architecture/autopilot/QA_AUTOPILOT_V2_ARCHITECTURE.md`:54 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/qa/architecture/autopilot/QA_AUTOPILOT_V2_ARCHITECTURE.md`:305 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 5 Zellen).
- `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md`:161 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_EVOLUTION_MAP.md (aufgelöst: docs/qa/architecture/graphs/QA_EVOLUTION_MAP.md).
- `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md`:162 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/graphs/REGRESSION_CATALOG.md).
- `docs/qa/architecture/graphs/QA_ARCHITECTURE_GRAPH.md`:163 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/graphs/QA_RISK_RADAR.md).
- `docs/qa/architecture/graphs/QA_DEPENDENCY_GRAPH.md`:112 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/graphs/QA_RISK_RADAR.md).
- `docs/qa/architecture/graphs/QA_DEPENDENCY_GRAPH.md`:113 — **high** / links: Lokaler Link-Ziel existiert nicht: ../architecture.md (aufgelöst: docs/qa/architecture/architecture.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`:364 — **medium** / tables: Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`:374 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`:375 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_ARTIFACT_STANDARD.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`:377 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/incident_replay/REGRESSION_CATALOG.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`:378 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_CONTROL_CENTER.md (aufgelöst: docs/qa/architecture/incident_replay/QA_CONTROL_CENTER.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_INTEGRATION.md`:379 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_AUTOPILOT.md (aufgelöst: docs/qa/architecture/incident_replay/QA_AUTOPILOT.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:95 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:126 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_REPLAY_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_REPLAY_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:166 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:197 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:260 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/QA_INCIDENT_PILOT_ITERATION.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:283 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:284 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_REPLAY_SCHEMA.md (aufgelöst: docs/qa/architecture/incident_replay/QA_REPLAY_SCHEMA.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:285 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_LIFECYCLE.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_LIFECYCLE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:287 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/QA_INCIDENT_PILOT_ITERATION.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:288 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/architecture/incident_replay/QA_INCIDENT_ARTIFACT_STANDARD.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:289 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/architecture/incident_replay/REGRESSION_CATALOG.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_ARCHITECTURE.md`:290 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/architecture/incident_replay/QA_RISK_RADAR.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_INTEGRATION.md`:328 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md (aufgelöst: docs/qa/architecture/incident_replay/incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md).
- `docs/qa/architecture/incident_replay/QA_INCIDENT_REPLAY_INTEGRATION.md`:369 — **medium** / tables: Tabellenblock ohne erkannte Separator-Zeile (| --- |) — Rendering kann inkonsistent sein.
- `docs/qa/architecture/inventory/QA_TEST_INVENTORY_ARCHITECTURE.md`:93 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 4 vs. 6 Zellen).
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md`:96 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_STABILITY_INDEX.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.json).
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md`:96 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md`:97 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_SELF_HEALING.json (aufgelöst: docs/qa/artifacts/dashboards/QA_SELF_HEALING.json).
- `docs/qa/artifacts/dashboards/QA_ANOMALY_DETECTION.md`:98 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_STABILITY_HISTORY.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_HISTORY.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md`:85 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_PRIORITY_SCORE.json (aufgelöst: docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md`:85 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md`:86 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md`:88 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_STABILITY_INDEX.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.json).
- `docs/qa/artifacts/dashboards/QA_AUTOPILOT.md`:89 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_DEPENDENCY_GRAPH.md (aufgelöst: docs/qa/artifacts/dashboards/QA_DEPENDENCY_GRAPH.md).
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md`:53 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md`:97 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md`:104 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/artifacts/dashboards/QA_CONTROL_CENTER.md`:105 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_INTEGRATION.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_INTEGRATION.md).
- `docs/qa/artifacts/dashboards/QA_EVOLUTION_MAP.md`:91 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
- `docs/qa/artifacts/dashboards/QA_EVOLUTION_MAP.md`:92 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/artifacts/dashboards/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/artifacts/dashboards/QA_HEATMAP.md`:88 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
- `docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.md`:73 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
- `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md`:119 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/artifacts/dashboards/REGRESSION_CATALOG.md).
- `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md`:119 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_SELF_HEALING.md`:120 — **high** / links: Lokaler Link-Ziel existiert nicht: CHAOS_QA_PLAN.md (aufgelöst: docs/qa/artifacts/dashboards/CHAOS_QA_PLAN.md).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md`:95 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_PRIORITY_SCORE.json (aufgelöst: docs/qa/artifacts/dashboards/QA_PRIORITY_SCORE.json).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md`:95 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md`:96 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_HEATMAP.json (aufgelöst: docs/qa/artifacts/dashboards/QA_HEATMAP.json).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md`:97 — **high** / links: Lokaler Link-Ziel existiert nicht: CHAOS_QA_PLAN.md (aufgelöst: docs/qa/artifacts/dashboards/CHAOS_QA_PLAN.md).
- `docs/qa/artifacts/dashboards/QA_STABILITY_INDEX.md`:98 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_STATUS.json (aufgelöst: docs/qa/artifacts/dashboards/QA_STATUS.json).
- `docs/qa/artifacts/dashboards/QA_STATUS.md`:109 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/artifacts/dashboards/QA_STATUS.md`:118 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/governance/CI_TEST_LEVELS.md`:90 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/governance/CI_TEST_LEVELS.md`:150 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/governance/CI_TEST_LEVELS.md`:163 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/governance/REGRESSION_CATALOG.md`:129 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_ARTIFACT_STANDARD.md (aufgelöst: docs/qa/governance/QA_INCIDENT_ARTIFACT_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:130 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:131 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:132 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:133 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md (aufgelöst: docs/qa/governance/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:134 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_INTEGRATION.md (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_INTEGRATION.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:135 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:136 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/REGRESSION_CATALOG.md`:137 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_SCHEMA.json (aufgelöst: docs/qa/governance/QA_INCIDENT_REPLAY_SCHEMA.json).
- `docs/qa/governance/incident_schemas/BINDINGS_JSON_FIELD_STANDARD.md`:383 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 3 Zellen).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:202 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:241 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:247 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:298 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:302 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:337 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/bindings.template.json (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/bindings.template.json).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_ARTIFACT_STANDARD.md`:356 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/notes.template.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/notes.template.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_LIFECYCLE.md`:359 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_LIFECYCLE.md`:362 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md`:337 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md`:345 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md`:347 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/incident.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/incident.template.yaml).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md`:348 — **high** / links: Lokaler Link-Ziel existiert nicht: REGRESSION_CATALOG.md (aufgelöst: docs/qa/governance/incident_schemas/REGRESSION_CATALOG.md).
- `docs/qa/governance/incident_schemas/QA_INCIDENT_SCHEMA.md`:349 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/governance/incident_schemas/QA_RISK_RADAR.md).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md`:357 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md`:365 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_INCIDENT_REPLAY_ARCHITECTURE.md (aufgelöst: docs/qa/governance/incident_schemas/QA_INCIDENT_REPLAY_ARCHITECTURE.md).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md`:367 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/templates/replay.template.yaml (aufgelöst: docs/qa/governance/incident_schemas/incidents/templates/replay.template.yaml).
- `docs/qa/governance/incident_schemas/QA_REPLAY_SCHEMA.md`:368 — **high** / links: Lokaler Link-Ziel existiert nicht: incidents/QA_INCIDENT_PILOT_ITERATION.md (aufgelöst: docs/qa/governance/incident_schemas/incidents/QA_INCIDENT_PILOT_ITERATION.md).
- `docs/qa/history/QA_DOCUMENTATION_STRUCTURE_PROPOSAL.md`:299 — **high** / links: Lokaler Link-Ziel existiert nicht: QA_RISK_RADAR.md (aufgelöst: docs/qa/history/QA_RISK_RADAR.md).
- `docs/qa/history/phase3/PHASE3_CI_INTEGRATION_PLAN.md`:53 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/history/phase3/PHASE3_REPLAY_BINDING_ARCHITECTURE.md`:77 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (3 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/history/phase3/PHASE3_REPLAY_BINDING_ARCHITECTURE.md`:91 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/qa/history/phase3/PHASE3_TECHNICAL_DOCS.md`:108 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/reports/QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md`:65 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/reports/QA_AUTOPILOT_V3_GOVERNANCE_REVIEW.md`:137 — **medium** / headings: Sprung in der Überschriftenhierarchie (H1 → H3).
- `docs/qa/reports/QA_AUTOPILOT_V3_VERIFICATION_REPORT.md`:19 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 3 vs. 4 Zellen).
- `docs/qa/reports/UX_DEFECTS_QA_GAP_ANALYSIS.md`:45 — **high** / tables: Uneinheitliche Spaltenanzahl in der Tabelle (z. B. 2 vs. 4 Zellen).
- `docs/refactoring/KNOWLEDGE_UI_TO_GUI_ANALYSIS.md`:20 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (11 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/refactoring/PROMPTS_UI_TO_GUI_ANALYSIS.md`:20 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (9 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `docs/refactoring/SETTINGS_UI_TO_GUI_ANALYSIS.md`:21 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (7 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `help/getting_started/introduction.md`:36 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (5 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.
- `help/operations/chat_overview.md`:43 — **medium** / ascii_blocks: ASCII-/CLI-ähnlicher Block (4 Zeilen) ohne Fence — kann in der GUI als Fließtext mit falscher Breite laufen.

## Methodik und Grenzen

- **Scan**: `README.md`, alle `*.md` unter `docs/`, `help/`, `docs_manual/`, plus weitere `*.md` im Projektroot.
- **GUI-Bezug**: Regeln orientieren an der Markdown-Pipeline (z. B. nur ```-Fences, keine `~~~`; Normalisierung LF/Tabs im Renderer).
- **help/**: Links ohne Pfad/Suffix wie `(chat_overview)` werden als **Topic-IDs** gegen `help/**/*.md` (Frontmatter-`id` bzw. Dateistamm) aufgelöst — wie im Hilfe-Index.
- **Nicht geprüft**: Reference-Links `[x][ref]`, rohes HTML, benutzerdefinierte Anker außerhalb von `#`-Überschriften-Slugs.
- **Erneut ausführen**: `python3 tools/validate_markdown_docs.py` überschreibt diesen Report deterministisch.
