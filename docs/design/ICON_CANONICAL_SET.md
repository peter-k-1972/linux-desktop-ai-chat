# Kanonisches Icon-Set (Registry)

**Quelle:** `ICON_MAPPING.md`, `ICON_TAXONOMY.md`  
**Dateien:** `resources/icons/<category>/<registry_id>.svg`  
**Generator:** `tools/generate_canonical_icon_set.py` (Reproduktion des gesamten Satzes)  
**QA:** `tools/icon_svg_guard.py`

Legende **Herkunft:** *neu* = mit Generator als einheitliches Set erzeugt; *ersetzt* = frühere Datei durch neues Set ersetzt.

---

## Navigation

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| dashboard | navigation | Raster, Übersicht | Kommandozentrale, Start | neu | — |
| chat | navigation | Konversation | Operations, Chat-Modus | neu | — |
| control | navigation | Steuerung, Schieberegler | Control Center | neu | — |
| shield | navigation | Schutz, Governance | QA & Governance (Hauptnav) | neu | Runtime-QA nutzt **nicht** shield (siehe `qa_runtime`) |
| activity | navigation | Aktivitätslinie | Runtime / Debug (Hauptnav) | neu | Nicht als Ersatz für Workflow-Metriken (siehe `system_graph`) |
| gear | navigation | Einstellungen | Settings-Bereich | neu | — |

---

## Objects

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| agents | objects | Personen / Akteure | Agents, Agent Tasks | neu | — |
| models | objects | Modell-Block | Modelle, Katalog | neu | — |
| providers | objects | Anbieter / Stack | Provider-Workspace | neu | — |
| tools | objects | Werkzeug | Tools-Workspace | neu | — |
| data_stores | objects | Datenschicht | Data Stores (Control Center) | neu | **Nicht** für Deployment (→ `deploy`) |
| knowledge | objects | Buch, Wissen | Knowledge-Workspace | neu | — |
| prompt_studio | objects | Prompt-Editor | Prompt Studio | neu | — |
| projects | objects | Projektordner | Projects, Default-Objekticon | neu | — |
| test_inventory | objects | Checkliste | Test Inventory | neu | — |
| coverage_map | objects | Karte / Layer | Coverage Map | neu | — |
| gap_analysis | objects | Balken / Lücken | Gap Analysis | neu | — |
| incidents | objects | Warn-Dreieck | Incidents, Audit | neu | — |
| replay_lab | objects | Wiedergabe + Rewind | Replay Lab | neu | — |
| appearance | objects | Sonne/Strahlen | Theme Visualizer, Look & Feel | neu | — |
| system | objects | CPU-Chip | Introspection, System-Settings | neu | — |
| advanced | objects | Schieberegler-Spalten | Advanced Settings | neu | — |

---

## Actions

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| add | actions | Plus | Neu anlegen | neu | — |
| remove | actions | Minus | Entfernen | neu | Kein Duplikat `delete.svg` im Kanon |
| edit | actions | Stift | Bearbeiten | neu | — |
| refresh | actions | Pfeil-Kreis | Neu laden | neu | — |
| search | actions | Lupe | Suche | neu | **Nicht** für „Quelle öffnen“ (→ `open` / `link_out`) |
| filter | actions | Trichter | Filter | neu | — |
| run | actions | Play | Ausführen | neu | — |
| stop | actions | Stop-Quadrat | Abbrechen | neu | — |
| save | actions | Diskette | Speichern | neu | — |
| deploy | actions | Upload/Pfeil | Deployment, Release | neu | Immer `deploy`, nie `data_stores` |
| pin | actions | Stecknadel | Chat pin, Favorit | neu | Nicht mehr `add` |
| open | actions | Dokument mit Zeilen | Datei öffnen, intern | neu | — |
| link_out | actions | Kasten + Pfeil extern | URL, externer Link | neu | Synonyme: `external_link`, `open_external` |

*Hinweis:* `help` und `send` sind taxonomisch **system** (Abschnitt unten), nicht unter `actions/`.

---

## States

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| success | states | Kreis + Haken | OK | neu | — |
| warning | states | Dreieck + Ausruf | Warnung | neu | — |
| error | states | Kreis + Kreuz | Fehler | neu | — |
| running | states | Kreis + Fortschrittspfeil | Läuft | neu | — |
| idle | states | Uhr | Wartend | neu | — |
| paused | states | Zwei Balken | Pausiert | neu | — |

---

## Monitoring

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| eventbus | monitoring | Knoten + Kanten | Event Bus | neu | — |
| logs | monitoring | Zeilen + Rand | Logs | neu | Markdown-Demo nutzt **sparkles**, nicht logs |
| metrics | monitoring | Balkendiagramm | Metrics | neu | — |
| llm_calls | monitoring | Kreuz + Kern | LLM-Aufrufe | neu | — |
| agent_activity | monitoring | Aktivitätslinie | Agent Activity | neu | — |
| system_graph | monitoring | Graph-Knoten | Workflows, Systemgraph | neu | Nur bei echter Graph-/Workflow-Semantik |
| qa_runtime | monitoring | Fadenkreuz | QA Cockpit, Observability | neu | Trennung von Governance-`shield` |

---

## System

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| help | system | Hilfe | TopBar, Kommandos | neu | Doppelt in Tabelle Actions (semantisch Aktion) |
| info | system | Info-i | Hinweise | neu | — |
| send | system | Senden | Chat Send | neu | — |

---

## AI / Workflow / Data (Erweiterung)

| registry_id | category | Semantik | Hauptverwendung | Herkunft | Konflikt / Hinweis |
|-------------|----------|----------|-----------------|----------|-------------------|
| sparkles | ai | Sterne | Markdown-Demo, LLM-Deko | neu | — |
| graph | workflow | Rechteck-Netz | Workflow-Graphen (alternativ) | neu | Zusatz zu `system_graph` |
| pipeline | workflow | drei Stufen | Pipeline-Metapher | neu | — |
| dataset | data | Zylinder-Scheiben | Datensatz-Visual | neu | Objekttyp `dataset` bleibt in Code → `data_stores` |
| folder | data | Ordner | Ordnerwahl, Dateibaum | neu | `get_icon_for_object("folder")` |

---

## Nicht mehr kanonisch (entfernt)

| Pfad | Grund |
|------|--------|
| `resources/icons/actions/create.svg` | Alias von `add`; nur `add.svg` |
| `resources/icons/actions/delete.svg` | Alias von `remove`; nur `remove.svg` |

---

*Implementierung:* `app/gui/icons/icon_registry.py` (`REGISTRY_TO_RESOURCE`).
