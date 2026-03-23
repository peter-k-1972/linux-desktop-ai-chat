# Icon Set Generation Report

Erzeugung eines **vollständigen kanonischen** symbolischen SVG-Satzes für Linux Desktop Chat / Obsidian Core.

---

## Neue / geänderte Artefakte

### Dokumentation

| Datei | Zweck |
|-------|--------|
| `docs/design/ICON_CANONICAL_SET.md` | Vollständige Registry-Liste mit Semantik |
| `docs/design/ICON_CONFLICT_RESOLUTION.md` | Verbindliche Konfliktentscheidungen |
| `docs/design/ICON_REVIEW_BOARD.md` | Review-Tabelle (Status approved) |
| `docs/design/ICON_CUTOVER_PLAN.md` | Migration ohne Big-Bang |
| `docs/design/ICON_MAPPING.md` | Ergänzt: `link_out` / Synonyme |
| `docs/design/ICON_TAXONOMY.md` | Ergänzt: `link_out`, Klarstellung `data` |

### Tools

| Datei | Zweck |
|-------|--------|
| `tools/generate_canonical_icon_set.py` | Schreibt **56** SVGs nach `resources/icons/` |
| `tools/icon_svg_guard.py` | Automatisierte Style-QA |

### Tests

| Datei | Zweck |
|-------|--------|
| `tests/tools/test_icon_svg_guard.py` | Guard CLI + Negative Tests |

### Code

| Datei | Änderung |
|-------|----------|
| `app/gui/icons/icon_registry.py` | `link_out`, `graph`, `pipeline`, `dataset`, `folder`; Aktionen `external_link` / `open_external`; `folder` in `OBJECT_TYPE_TO_REGISTRY` |
| `app/gui/icons/registry.py` | Konstanten + `IconEntry` für `LINK_OUT`, `GRAPH`, `PIPELINE`, `DATASET`, `FOLDER` |

### SVG-Bestand `resources/icons/`

- **56** Dateien, einheitlich: `viewBox="0 0 24 24"`, `stroke-width="1.5"`, `stroke="currentColor"`, `fill="none"` auf Root, keine Hex-Farben.
- **Entfernt:** `actions/create.svg`, `actions/delete.svg` (Alias-Brüche im Kanon).

### Fallback-Spiegel

- `assets/icons/svg/` teilweise mit Kopien aus `resources/icons/` (navigation, panels←objects, actions, status←states, runtime←monitoring, system, ai, workflow, data, `link_out`).

---

## Übernommen vs. neu gezeichnet

- **Sämtliche** unter `resources/icons/` gelisteten Registry-Dateien wurden durch **`generate_canonical_icon_set.py`** neu geschrieben (ein visuelles Set, keine blinden Kopien aus Altbeständen).
- Frühere Einzeldateien galten nur als Referenz für Semantik, nicht als 1:1-Kopie.

---

## Bereinigte Konflikte (siehe `ICON_CONFLICT_RESOLUTION.md`)

- Deployment → `deploy` (nicht `data_stores`).
- Pin → eigenes Icon.
- Open / Link extern → `open` + `link_out` (nicht `search`).
- Markdown-Demo → `sparkles` (nicht `logs`).
- Shield vs. Runtime-QA → `shield` vs. `qa_runtime`.
- `system_graph` / `activity` — dokumentierte Verwendungsregeln.

---

## Offene Sonderfälle

- **QRC / `app/resources/icons`:** weiterhin Legacy; nicht in diesem Schritt entfernt.
- **`assets/icons/svg` vs. Taxonomie `objects` vs. `panels`:** Fallback nutzt historisch `panels/`; Manager bevorzugt `resources/icons/objects/`.
- **UI:** nicht jeder Button auf `link_out` umgestellt — nur Registry vorbereitet; schrittweise Cutover.

---

## QA-Status

| Prüfung | Ergebnis |
|---------|----------|
| `python3 tools/icon_svg_guard.py` | OK (56 SVGs) |
| `pytest tests/tools/test_icon_svg_guard.py` | auszuführen im CI |
| `pytest tests/unit/gui/test_icon_registry.py` | Registry inkl. neuer IDs |

---

## Empfohlene nächste Schritte

1. Externe Links in UI konsequent `IconManager.get(IconRegistry.LINK_OUT)` (oder `get_icon_for_action("link_out")`) zuweisen.
2. Legacy-QRC und `app/resources/icons` inventarisieren und pro Modul entfernen.
3. Optional: `generate_canonical_icon_set.py` in CI nur **validieren** (Guard), nicht überschreiben — oder bei Design-Änderungen bewusst ausführen.

---

*Style:* `docs/design/ICON_STYLE_GUIDE.md`.
