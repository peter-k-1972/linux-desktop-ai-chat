# Theme-/Farb-Refactoring — Phasenplan (Entwurf)

Dieses Dokument ist bewusst kurz gehalten; die Begründungen und Fundstellen stehen in `THEME_COLOR_AUDIT.md`.

## Phase A — Inventar absichern

- `THEME_COLOR_INVENTORY.csv` und diesen Audit bei größeren Theme-Änderungen per Skript neu erzeugen (Hex-Scan `app/**/*.py`).
- Ein CI- oder Pre-Commit-Gate: „keine neuen Roh-Hex in neuen GUI-Modulen“ (optional, nach Kanon).

## Phase B — Zentrale Theme-Tokens definieren

- Kanonisches API: `get_theme_manager().get_tokens()` für alle Laufzeit-Farben; Legacy `get_theme_colors` durch Token-Ableitung oder Entfernung ersetzen.
- `theme_id_to_legacy_light_dark` nur noch an Randstellen (externe APIs) oder eliminieren.

## Phase C — Harte Direktfarben eliminieren

- Zuerst hohe Sichtbarkeit: Control-Center-Panels (`_cc_panel_style`, Tabellen), Chat-Details, Command-Center, Markdown-Kontextmenü-Fallback.
- Dann Inspector-Cluster (gemeinsame Hilfsfunktion `inspector_group_style(tokens)`).

## Phase D — QSS vereinheitlichen

- Single source für aktive QSS: `assets/themes/base/` (Duplikat unter `app/gui/themes/base/` bereinigen oder auf Symlink/Build-Kopie festlegen).
- Legacy- und Ressourcen-QSS (`app/resources/*.qss`, `assets/themes/legacy/`) entweder löschen oder dokumentiert an einen Generator anbinden.

## Phase E — Sonderrenderer angleichen

- `markdown_renderer.py`: Inline-HTML-Styles an Token-Injection oder CSS-Klassen + globales Stylesheet.
- Grafik: `workflow_node_item`, `canvas_tabs`, `agent_performance_tab`, `ai_canvas_scene` — Farben aus Tokens oder semantischen Status-Paaren.

## Phase F — Kontrast-/Lesbarkeit

- `app/gui/themes/contrast.py` auf alle semantischen Paare ausweiten (Tests in CI).
- Manuelle Prüfung von `workbench` und Monitoring-Panels (dunkle Inseln auf hellem Chrome).
