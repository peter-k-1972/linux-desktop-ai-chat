# Icon Cutover Plan

**Ziel:** Kontrollierte Migration des UI auf das kanonische Set unter `resources/icons/` — **ohne** sofortige Vollständigung aller Legacy-Screens.

---

## 1. Kanonische Quelle (jetzt)

| Ebene | Pfad |
|-------|------|
| Primär | `resources/icons/<taxonomy>/*.svg` |
| Auflösung | `app/gui/icons/icon_registry.py` → `REGISTRY_TO_RESOURCE` |
| Darstellung | `IconManager` (lädt resources zuerst) |

---

## 2. Legacy-Pfade (später ersetzen / entfernen)

| Bestand | Risiko | Cutover-Schritt |
|---------|--------|-----------------|
| `app/resources/icons/` + QRC | Doppelte Semantik, alter Stroke | Pro Screen: auf `IconManager` + Registry-ID umstellen; QRC-Einträge streichen |
| `assets/icons/*.svg` (flach) | Stilbruch | Nicht erweitern; Inhalte nach `resources/icons` migrieren oder löschen |
| `assets/icons/svg/` | Fallback bis Cutover | Wird mit Generator/Spiegel aktuell an `resources/icons` angeglichen; langfristig nur noch Build-Fallback oder entfallen |

---

## 3. UI-Stellen (Priorität für Migration)

1. **Navigation & Sidebars** — `nav_mapping`, Domain-Navs; **Sidebar** nutzt Fallback `get_icon_for_nav(nav_key)`.
2. **Command Palette / Breadcrumbs** — Registry-Namen + `IconManager`.
3. **Operations / Knowledge** — `open`, `pin`, Chunks weiter **search** (Semantik Suche).
4. **Legacy** — `sidebar_widget`, `project_chat_list_widget`, `main.py` (Toolbar), **ChatComposer** Send → **IconManager** (erledigt in Cutover-Phase).

Weitere Stellen: `ICON_BINDING_AUDIT.md`, Guard `tools/icon_usage_guard.py`.

---

## 4. Registry-Erweiterungen (erledigt / vorbereitet)

- `link_out`, `graph`, `pipeline`, `dataset`, `folder` als Registry-IDs registriert.
- `get_icon_for_object("folder")` → `folder`.
- Objekttyp `dataset` bleibt bewusst auf **`data_stores`** (Semantik Datenhaltung im Produktmodell).

---

## 5. Risiken

- **Visuelle Regression:** dichtere Glyphen (1.5 pt) wirken auf manchen Hintergründen leichter → Theme-`state` testen.
- **Cache:** nach Theme-Wechsel `IconManager.clear_cache()` (bereits etabliert).
- **Doppelte Dateinamen:** keine `create.svg`/`delete.svg` mehr im Kanon — alte Links brechen, falls noch vorhanden.

---

## 6. Abnahme Cutover (Meilenstein)

- [ ] Kein produktiver Code mehr, der flache `assets/icons/*.svg` ohne Manager lädt (Composer/Main-Legacy-Pfade entfernt; `settings.icons_path` existiert noch für Alt-Konfiguration).
- [x] QRC-Icons in **genannten** Legacy-Widgets (`sidebar_widget`, `project_chat_list_widget`) entfallen zugunsten `IconManager`.
- [ ] `assets/icons/svg` langfristig nur generierter Fallback oder entfallen.

---

## 7. API-Schicht (Cutover)

- `get_icon_for_nav(nav_id)` — Workspace- oder Bereichs-ID → Icon
- `get_icon_for_status(status)` — Status-Glyphen
- Siehe `ICON_RUNTIME_USAGE.md`

---

*Siehe:* `ICON_SET_GENERATION_REPORT.md`, `ICON_MIGRATION_PLAN.md`, `ICON_CUTOVER_FINAL_REPORT.md`.
