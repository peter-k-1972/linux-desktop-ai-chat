# Cursor-light Tools (`cl.*`)

Technische Einordnung: Die sieben Werkzeuge werden über die **Pipeline-Executor-Registry** als `executor_type: **cursor_light**` bereitgestellt und vom Workflow-Knoten **`tool_call`** synchron aufgerufen. Implementierung: Paket `linux-desktop-chat-pipelines`, Modulbaum `app.pipelines.executors.cursor_light`.

## Sicherheit (Kurz)

- Nur Pfade unter `workspace_root` (kein `..`, keine Symlink-Escapes).
- Keine Netzwerkzugriffe in den Tools.
- Git: nur `status` / `diff`; Unified-Patches via `git apply` (Schreiben der Arbeitskopie) oder `replace_block` für Dateien im Workspace — **kein** `commit`, `push`, `checkout`, `reset`.
- `cl.test.run`: feste **Allowlist** von `command_key`-Werten, keine freie Shell.

## Tool-IDs

| `tool_id` | Kurzbeschreibung |
|-----------|------------------|
| `cl.file.read` | Textdatei lesen; `max_bytes`, `max_lines`, `line_start`/`line_end`, `max_chars` |
| `cl.file.write` | Datei vollständig schreiben; optional `create_dirs` |
| `cl.file.patch` | `mode: unified_diff` (Standard) oder `replace_block` mit eindeutigem `old_text` |
| `cl.repo.search` | Regex oder Literal; `include_glob` / `exclude_glob`; `max_matches` |
| `cl.test.run` | z. B. `command_key: pytest` → `python -m pytest` |
| `cl.git.status` | Porcelain-Status, strukturierte Felder |
| `cl.git.diff` | `scope: working` \| `staged`; optional `path`; `max_chars` |

## `tool_call`-Knoten

```text
executor_type: cursor_light
executor_config:
  workspace_root: /abs/pfad/projekt   # oder über Workflow-Input-Payload workspace_root
  tool_id: cl.file.read
  input:
    path: README.md
    max_lines: 100
```

## Ergebnisformat

Der Knoten liefert unter `tool_result` ein Objekt:

- `success` (bool, fachlicher Erfolg)
- `data` (Nutzlast oder `null`)
- `error` (strukturiertes Fehlerobjekt oder `null`)
- `metadata`: u. a. `tool_id`, `duration_ms`, `cwd`; je nach Tool `target_path`, `truncated`, `exit_code`

Die Pipeline liefert auf `StepResult`-Ebene immer `success: true`, damit der Workflow bei Tool-Fehlern nicht abbricht; Auswertung über `tool_result.success`.

## Weitere Doku

Spezifikation (Architektur): `docs/04_architecture/CURSOR_LIGHT_MINIMAL_TOOL_LAYER.md`
