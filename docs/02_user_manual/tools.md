# Tools und Integrationen

## FileSystemTools

Workspace-sichere Dateisystem-Operationen. Nur innerhalb der dem Chat hinzugefügten Verzeichnisse/Dateien.

### Verfügbare Tools

| Tool | Beschreibung |
|------|--------------|
| list_dir | Listet Verzeichnisinhalt |
| read_file | Liest Dateiinhalt |
| write_file | Schreibt in Datei |
| execute_command | Führt Befehl aus (Bestätigung erforderlich) |

### Nutzung durch LLM

Das LLM kann `<tool_call name="list_dir"/>` etc. im Text ausgeben. Die Chat-Logik parst diese Tags und führt die Tools aus. Ergebnisse werden in die Antwort eingefügt.

## Slash-Commands

| Command | Wirkung |
|---------|---------|
| /fast | Modus: Schnell |
| /smart | Modus: Standard |
| /chat | Modus: Chat |
| /think | Modus: Denken |
| /code | Modus: Code |
| /vision | Modus: Vision |
| /overkill | Modus: Overkill (Cloud) |
| /research | Modus: Research Agent |
| /auto on \| off | Auto-Routing ein/aus |
| /cloud on \| off | Cloud-Eskalation ein/aus |
| /delegate &lt;Anfrage&gt; | Agenten-Orchestrierung |

### Beispiele

- `/think Erkläre Quantencomputing` – Sendet mit THINK-Rolle
- `/delegate Erstelle ein Video über KI` – Startet Delegation
- `/auto off` – Deaktiviert Auto-Routing

## Web-Suche

Checkbox **Websuche** im Header: Aktuelle Suchergebnisse werden als Kontext genutzt (wenn implementiert).

## Media-Pipelines (design_system.json)

Externe Tools für Medien:

- **text_to_image**: `~/ai/pipeline/run_pipeline.py --module image`
- **image_to_animation**: `~/ai/pipeline/run_pipeline.py --module animation`
- **video_production**: `~/ai/pipeline/run_pipeline.py --module video`
