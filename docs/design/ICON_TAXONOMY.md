# Icon Taxonomy

Einheitliche Kategorien für Dateipfade unter `resources/icons/<category>/` und für die Dokumentation.

| Kategorie | Zweck | Beispiele |
|-----------|--------|-----------|
| **navigation** | Hauptbereiche, globale Modi | dashboard, chat, control, shield, activity, gear |
| **objects** | Fachobjekte / Screens (ehem. „panels“) | agents, models, providers, knowledge, incidents, projects |
| **actions** | Verben auf Entitäten | add, remove, edit, refresh, search, open, link_out, filter, run, stop, save, deploy, pin |
| **states** | Status / Qualität | success, warning, error, running, idle, paused |
| **ai** | KI-spezifische Metaphern (optional erweiterbar) | sparkles (Prompt/LLM-Dekoration) |
| **workflow** | Graphen, Pipelines, Abläufe | graph, pipeline |
| **data** | Datenhaltung, Dateien | dataset, folder (Registry-IDs; Objekttyp `dataset` in Code mappt weiter auf `data_stores`) |
| **monitoring** | Live-Beobachtung, Runtime | logs, metrics, eventbus, llm_calls, agent_activity, system_graph, qa_runtime |
| **system** | Meta-UI, Transport | help, info, send |

**Abgrenzung:**

- **monitoring** vs **objects:** Monitoring = „Was läuft gerade?“; objects = „Womit arbeite ich?“  
- **workflow** vs **monitoring system_graph:** Workflow-Ordner für zukünftige Workflow-only Varianten; aktuell kann `system_graph` in beiden Kontexten genutzt werden, Registry zeigt auf `monitoring/system_graph.svg`.

---

*Implementierung der Pfad-Zuordnung:* `app/gui/icons/icon_registry.py` → `REGISTRY_TO_RESOURCE`.
