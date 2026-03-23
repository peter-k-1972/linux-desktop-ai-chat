# Icon Migration Plan

**Ziel:** Ein Baum symbolischer SVGs unter `resources/icons/` (Taxonomie), zentrale Auflösung über `icon_registry` + `IconManager`, Weg von fragmentierten Legacy-Pfaden.

---

## 1. Soll-Architektur

| Schicht | Rolle |
|---------|--------|
| `resources/icons/<taxonomy>/*.svg` | Kanonische, `currentColor`-basierte Quellen |
| `app/gui/icons/icon_registry.py` | Registry-ID → Taxonomie-Pfad |
| `app/gui/icons/registry.py` (`IconRegistry`) | Konstanten + Fallback-Pfade unter `assets/icons/svg/` |
| `app/gui/icons/manager.py` | Laden, Token/State → Farbe, `QIcon`-Cache |

Ladereihenfolge im Manager: zuerst `get_resource_svg_path`, sonst `assets/icons/svg/…`.

---

## 2. Legacy-Bestände und Cutover

### 2.1 `app/resources/icons/` (QRC / alt)

- **Status:** Legacy für ältere Einstiege (`app.main` o. Ä.), nicht Teil der neuen Taxonomie.
- **Schritte:** Neue UI nur noch über `IconManager`; bestehende QRC-Referenzen bei Refactor von Legacy-Screens ersetzen oder QRC nach `resources/icons` spiegeln und aus QRC entfernen (physisch eine Quelle).

### 2.2 `assets/icons/*.svg` (flach)

- **Status:** Duplikate / Sonderfälle, nicht über den Manager angesprochen.
- **Schritte:** Inhalt prüfen; Duplikate löschen oder nach `resources/icons` verschieben und Referenzen bereinigen.

### 2.3 Doppelte Bäume `assets/icons/actions/` vs `assets/icons/svg/actions/`

- **Status:** Teilweise parallele Dateien; Manager nutzt primär `resources/icons` und `assets/icons/svg/`.
- **Schritte:** `assets/icons/actions/` (ohne `svg/`) als deprecated markieren; keine neuen Dateien dort. Konsolidierung in `resources/icons/actions/` + optionaler Spiegel nur unter `assets/icons/svg/actions/` für den Fallback.

### 2.4 `app/gui/icons/svg/` (entfernt)

- **Status:** laut Projekt-Historie entfernt zugunsten `assets/icons/svg`.
- **Schritte:** nicht wiederbeleben; kanonisch `resources/icons`.

---

## 3. API-Migration (Call-Sites)

- Standard: `IconManager.get(name, size=…, state="default")` statt impliziter „voller“ Primärfarbe — bei Bedarf `state="primary"` für stärkere Glyphe.
- Explizite Sonderfarben: `color_token="color.domain.monitoring.accent"` o. Ä. unverändert möglich (überschreibt State).
- `get_icon` / `get_icon_for_object` / `get_icon_for_action`: `state`-Parameter nutzen, `color_token` nur bei Abweichung vom State-Modell.

---

## 4. Reihenfolge (empfohlen)

1. Neue Icons nur unter `resources/icons` anlegen und in `REGISTRY_TO_RESOURCE` + `IconRegistry` registrieren.
2. Navigations- und Panel-Mappings (`nav_mapping.py`, betroffene Widgets) auf Registry-IDs umstellen.
3. Legacy-QRC und flache `assets/icons` nur noch lesend migrieren; schreibende Änderungen nur in `resources/icons`.
4. Nach Cutover: unbenutzte Legacy-Dateien archivieren oder löschen (mit visuellem Regression-Check).

---

## 5. Theme-Wechsel

Nach Theme-Wechsel weiterhin `IconManager.clear_cache()` aufrufen (bereits z. B. in Appearance-Workspace / Bootstrap), damit Cache-Keys mit neuer Theme-ID/Token-Auflösung nicht veralten.

---

*Verwandt: `ICON_STATE_MODEL.md`, `ICON_COLOR_RULES.md`, `ICON_CONFLICT_REPORT.md`.*
