# Icon Review Board

Übersicht des kanonischen Sets unter `resources/icons/`.  
**Status:** nach Style Guide (`ICON_STYLE_GUIDE.md`) und `tools/icon_svg_guard.py` geprüft.

Legende: **approved** = im Set enthalten und QA grün; **revise** = bewusst noch offen (derzeit keine).

| registry_id | Kategorie | Kurzbeschreibung | Verwendungsbeispiele | Status |
|-------------|-----------|------------------|----------------------|--------|
| dashboard | navigation | Vier-Kacheln-Dashboard | Kommandozentrale | approved |
| chat | navigation | Sprechblase | Operations, Chat | approved |
| control | navigation | Regler / Schalter | Control Center | approved |
| shield | navigation | Schild | QA & Governance (Nav) | approved |
| activity | navigation | Aktivitätskurve | Runtime / Debug (Nav) | approved |
| gear | navigation | Zahnrad | Settings | approved |
| agents | objects | Zwei Nutzer | Agents, Tasks | approved |
| models | objects | Package/Würfel | Modelle | approved |
| providers | objects | Stack/Anbieter | Providers | approved |
| tools | objects | Schraubenschlüssel | Tools | approved |
| data_stores | objects | Datenbank-Zylinder | Data Stores | approved |
| knowledge | objects | Buch | Knowledge | approved |
| prompt_studio | objects | Nachricht + Zeilen | Prompt Studio | approved |
| projects | objects | Ordner | Projects | approved |
| test_inventory | objects | Clipboard | Test Inventory | approved |
| coverage_map | objects | Polygon-Karte | Coverage | approved |
| gap_analysis | objects | Balken mit Brücke | Gap Analysis | approved |
| incidents | objects | Warn-Dreieck | Incidents | approved |
| replay_lab | objects | Play + Rewind | Replay | approved |
| appearance | objects | Sonne | Theme / Look | approved |
| system | objects | Chip | Introspection, System | approved |
| advanced | objects | Drei Schieber | Advanced Settings | approved |
| add | actions | Plus | Neu | approved |
| remove | actions | Minus | Löschen | approved |
| edit | actions | Stift | Bearbeiten | approved |
| refresh | actions | Pfeil-Kreis | Reload | approved |
| search | actions | Lupe | Suche | approved |
| filter | actions | Trichter | Filter | approved |
| run | actions | Play | Run | approved |
| stop | actions | Quadrat | Stop | approved |
| save | actions | Diskette | Save | approved |
| deploy | actions | Upload-Bogen | Deploy | approved |
| pin | actions | Nadel | Pin Chat | approved |
| open | actions | Dokument | Datei öffnen | approved |
| link_out | actions | Fenster + Pfeil | Externer Link | approved |
| success | states | Haken im Kreis | OK | approved |
| warning | states | Dreieck | Warnung | approved |
| error | states | Kreuz | Fehler | approved |
| running | states | Kreis Pfeil | Läuft | approved |
| idle | states | Uhr | Idle | approved |
| paused | states | Pause | Pause | approved |
| eventbus | monitoring | Netz | Event Bus | approved |
| logs | monitoring | Log-Zeilen | Logs | approved |
| metrics | monitoring | Säulen | Metrics | approved |
| llm_calls | monitoring | Ziel/LLM | LLM Trace | approved |
| agent_activity | monitoring | Puls | Agent Activity | approved |
| system_graph | monitoring | Graph | Workflows, Map | approved |
| qa_runtime | monitoring | Fadenkreuz | QA Cockpit | approved |
| help | system | ? im Kreis | Hilfe | approved |
| info | system | i im Kreis | Info | approved |
| send | system | Papierflieger | Senden | approved |
| sparkles | ai | Sterne | Markdown-Demo | approved |
| graph | workflow | Gitter-Graph | Workflow-Alt. | approved |
| pipeline | workflow | Stufen | Pipeline | approved |
| dataset | data | Tabellen-Daten | Datensatz-Icon | approved |
| folder | data | Ordner | Ordner | approved |

---

## Review-Hinweise

- Visuelle Review: alle Dateien in `resources/icons/` in einem Viewer bei **24 px** prüfen.
- Regeneration: `python3 tools/generate_canonical_icon_set.py` überschreibt das komplette Set — danach erneut `icon_svg_guard.py` und diese Tabelle bestätigen.

---

*QA-Automatisierung:* `tests/tools/test_icon_svg_guard.py`
