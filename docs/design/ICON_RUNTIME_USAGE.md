# Icon Runtime Usage (Soll für UI-Code)

**Bindungsschicht:** `app/gui/icons/manager.py` (`IconManager`) und `app/gui/icons/icon_registry.py`.

---

## 1. Erlaubte Einstiegspunkte

```python
from app.gui.icons import IconManager, get_icon, get_icon_for_nav, get_icon_for_status
from app.gui.icons import get_icon_for_object, get_icon_for_action
from app.gui.icons.registry import IconRegistry
```

| API | Verwendung |
|-----|------------|
| `IconManager.get(name, size=24, *, state="default", color_token=…)` | Registry-ID als String oder `IconRegistry.X` |
| `get_icon(name, …)` | Gleich wie Manager, Modulfunktion |
| `get_icon_for_nav(nav_id, …)` | `workspace_id` oder `NavArea`-ID (`command_center`, …) |
| `get_icon_for_object(type, …)` | Domänen-Objekttyp (`project`, `deployment`, …) |
| `get_icon_for_action(action, …)` | Verb (`open`, `link_out`, `add`, …) |
| `get_icon_for_status(status, …)` | `success`, `warning`, `error`, `running`, `idle`, `paused` (unbekannt → `info`) |

**States:** `default`, `primary`, `active`, `selected`, `disabled`, `success`, `warning`, `error` (siehe `ICON_STATE_MODEL.md`).  
Optional: `color_token="color.domain.monitoring.accent"` überschreibt die State-Token-Zuordnung.

---

## 2. Verboten in Produktiv-UI

- `QIcon(":/icons/…")` (QRC-Direktpfad)
- `QIcon(os.path.join(…, "foo.svg"))` oder beliebige Dateipfade zu UI-Icons
- Neue direkte `Path(...).read_text()` + manuelles Pixmap ohne Manager
- Semantisch falsches Icon wiederverwenden ohne Eintrag in `ICON_CONFLICT_RESOLUTION.md`

**Ausnahmen:** Nutzer-Avatare (`QIcon(pfad_zur_userdatei)`), System-Standardpixmaps (`QStyle`), zusammengesetzte Tab-Icons — dokumentiert im `ICON_BINDING_AUDIT.md`.

---

## 3. Neue Icons ergänzen

1. SVG unter `resources/icons/<taxonomy>/` ablegen (`ICON_STYLE_GUIDE.md`).
2. Eintrag in `REGISTRY_TO_RESOURCE` (`icon_registry.py`).
3. Optional Konstante in `IconRegistry` (`registry.py`).
4. `python3 tools/icon_svg_guard.py`
5. `ICON_MAPPING.md` / `ICON_CANONICAL_SET.md` aktualisieren.

---

## 4. Tests & Guard

| Kommando | Zweck |
|----------|--------|
| `python3 tools/icon_usage_guard.py` | Direkte QIcon/QPixmap/Pfad-Literale in `app/` |
| `python3 tools/icon_svg_guard.py` | SVG-Style unter `resources/icons/` |
| `python3 tools/icon_registry_guard.py` | Registry ↔ Dateien, Nav-Konflikte, Orphans (Warnung) |
| `python3 tools/run_icon_guards.py` | Alle drei + **`ICON_GUARD_REPORT.md`** |
| `python3 tools/icon_guard_report.py` | Nur Report (gleiche Logik wie run) |

**CI / pre-push:** `run_icon_guards.py` (siehe `.pre-commit-config.yaml`).

- `pytest tests/tools/test_icon_*.py tests/unit/gui/test_icon_*.py`

---

*Verwandt:* `ICON_CUTOVER_PLAN.md`, `ICON_BINDING_AUDIT.md`.
