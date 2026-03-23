# Icon Color Rules

**Ziel:** Pro Icon-State festlegen, welches **Theme-Token** die Laufzeit-Farbe liefert (ersetzt `currentColor` im SVG).

Token-Namen sind **kanonisch** (`color.fg.primary`); zur Laufzeit existieren parallel **flache** Keys (`color_fg_primary`) im Theme-Dict — `ThemeManager.color()` akzeptiert beides.

---

## 1. Standard-Zuordnung (UI-Chrome)

| Icon-State | Token (kanonisch) | Kurzbeschreibung |
|------------|-------------------|------------------|
| **default** | `color.fg.secondary` | Zurückhaltende Glyphe auf Oberflächen |
| **primary** | `color.fg.primary` | Haupttext / Standard-Betonung |
| **active** | `color.state.accent` | Aktive Interaktion, Fokus auf Aktion |
| **selected** | `color.nav.active_fg` | Ausgewählter Nav-/Listen-Eintrag |
| **disabled** | `color.fg.disabled` | Deaktivierte Kontrolle |
| **success** | `color.state.success` | Erfolg |
| **warning** | `color.state.warning` | Warnung |
| **error** | `color.state.error` | Fehler |

---

## 2. Überschreibungen

| Parameter | Priorität |
|-----------|-----------|
| `color` (explizite Farbe) | höchste |
| `color_token` | mittel — beliebiges Theme-Token |
| `state` | Standard, wenn nichts gesetzt |

Beispiele:

- Runtime-Monitor mit Monitoring-Palette: `color_token="color.domain.monitoring.accent"` (wie bisher in `runtime_debug_nav`).
- Einheitliche Chrome-Farbe trotz State: `color` oder `color_token` setzen.

---

## 3. Konsistenz Light / Dark / Custom

Alle genannten Tokens werden aus der **aktiven ThemeDefinition** aufgelöst (`ThemeManager.get_tokens()` / `color()`). Custom-Themes müssen dieselben Spec-Keys setzen oder von einem Basis-Theme erben, damit Icons nicht ausfallen.

Leere Auflösung: Fallback-Kette wie in `IconManager` (aktives Theme → `light_default`-Defaults → leeres Icon bei fehlendem SVG).

---

## 4. Bezug zum State Model

Die Tabelle in Abschnitt 1 ist die autoritative Zuordnung für `ICON_STATE_TO_TOKEN` in `app/gui/icons/icon_states.py`.

---

*Siehe: `ICON_STATE_MODEL.md`, `THEME_TOKEN_SPEC.md`, `resolved_spec_tokens.py`.*
