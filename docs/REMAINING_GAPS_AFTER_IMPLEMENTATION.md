# REMAINING_GAPS_AFTER_IMPLEMENTATION

**Stand:** 2026-03-20 · Nach Umsetzung der Remediation (siehe `docs/CHANGELOG_REMEDIATION.md`).

Nur **tatsächlich verbleibende** Lücken, mit kurzer Begründung und Priorität.

| Priorität | Thema | Begründung | Empfehlung |
|-----------|--------|------------|------------|
| **P1** | Vollständige **pytest-Collection** in CI/Entwickler-venv | Auf PEP-668-System-Python schlägt `pip install` fehl; ohne venv mit `requirements.txt` fehlt `qasync` → 30+ Collection-Errors. | In CI und Doku: immer **`python -m venv`** + `pip install -r requirements.txt`; optional Job `pytest --collect-only`. |
| **P2** | **Settings Project / Workspace** | Bewusst nur Empty State; keine persistierten projekt-/workspace-spezifischen Keys implementiert. | Produktentscheid: Keys definieren oder Nav-Einträge bis zur Implementierung ausblenden. |
| **P2** | **Critic-Modus** | `review_response` führt bei `enabled=True` **keinen** zweiten LLM-Lauf aus; nur Warn-Log. | Feature aktivieren (Implementierung) oder UI/Settings so führen, dass `enabled` nicht produktiv wählbar ist. |
| **P2** | **Pipeline ComfyUI / Media** | Executors bleiben bewusste Placeholder (`not yet implemented`). | Doku/UI für Nutzer, die Pipelines erwarten; keine Änderung in dieser Remediation. |
| **P3** | **Generierte / veraltete Karten** | `docs/TRACE_MAP.md`, `app-tree.md`, diverse UX-/Archiv-Reports erwähnen noch `agents_panels` oder alte CC-Texte. | `tools/generate_*` bzw. manuelle Bereinigung in separatem Doku-Pass. |
| **P3** | **Deployment-Dokumentation** | `DOC_GAP_ANALYSIS` listet Packaging weiterhin dünn. | Eigenes kurzes `DEPLOYMENT.md` oder expliziter „nicht unterstützt“-Abschnitt. |
| **P3** | **Live-Ollama E2E** | Dashboard/CC prüfen Erreichbarkeit per HTTP; keine Modell- oder Streaming-E2E-Tests hinzugefügt. | Optional nightly mit echter Ollama-Instanz. |
| **P3** | **Agent Tasks „Queue“-UI** | Entfernte ungenutzte Panels `status_panel`/`queue_panel`; der **AgentTasksWorkspace** nutzt weiterhin `ActiveAgentsPanel` / `AgentResultPanel` ohne neue Queue-Ansicht. | Bei Bedarf echte Task-Queue an `DebugStore`/Runner anbinden. |

---

## Nicht als Lücke gewertet

- **Zwei Klassen namens `AgentRegistryPanel`:** nur noch unter **Operations → Agent Tasks** (Listen-Panel); die CC-Demo-Variante wurde entfernt. Verwechslungsrisiko deutlich reduziert.
- **Markdown-Demo / Runtime Debug:** weiterhin bewusst intern.

---

*Ende REMAINING_GAPS_AFTER_IMPLEMENTATION*
