# Icon State Model

**Ziel:** Einheitliche, semantische Zustände für symbolische SVG-Icons (IDE-ähnlich). Farbe kommt aus Theme-Tokens, nicht aus der SVG-Datei (`currentColor`).

---

## 1. Zustände (kanonische Namen)

| State | Bedeutung | Typische UI-Situation |
|-------|-----------|------------------------|
| **default** | Standard-Glyphe auf normaler Fläche | Toolbar, Listenzeile, inaktiver Tab |
| **primary** | Betonte Standard-Glyphe | Überschriften-Leiste, primärer Kontext |
| **active** | Interaktiv aktiv / Fokus auf Aktion | Gedrückter Toggle, laufende Aktion |
| **selected** | Auswahl in Navigation oder Liste | Aktiver Nav-Eintrag, selektierte Zeile |
| **disabled** | Nicht verfügbar | Deaktivierter Button, gesperrte Aktion |
| **success** | Erfolg / OK | Status-Badge, Erfolgs-Hinweis |
| **warning** | Warnung | Hinweis, Risiko |
| **error** | Fehler / kritisch | Validierung, Fehlerzustand |

Alle States sind **lowercase**-Strings. API-Default: `state="default"`.

---

## 2. Abgrenzungen

- **active** vs **selected:** *active* = kurzfristige Interaktion oder „läuft gerade“; *selected* = persistente Auswahl im UI-Modell.
- **primary** vs **default:** *primary* hebt die Glyphe auf gleicher Fläche hervor; *default* ist die diskretere Variante (siehe `ICON_COLOR_RULES.md`).
- Status-Icons (**success** / **warning** / **error**) können entweder dedizierte Status-Glyphen (Registry `success`, `warning`, `error`) oder beliebige Icons mit entsprechendem `state` verwenden.

---

## 3. API-Mapping

- `IconManager.get(name, state="default", …)`  
- `get_icon(name, state="default", …)` in `icon_registry`  
- `get_icon_for_object(type, state="default", …)`  
- `get_icon_for_action(action, state="default", …)`  

Optional: `color_token` überschreibt die aus `state` abgeleitete Token-Zuordnung; `color` (Hex) überschreibt beides.

---

## 4. Erweiterung

Neue States nur mit Eintrag in:

- diesem Dokument (Semantik),
- `ICON_COLOR_RULES.md` (Token-Zuordnung),
- `app/gui/icons/icon_states.py` (Implementierung).

---

*Siehe auch: `ICON_COLOR_RULES.md`, `ICON_STYLE_GUIDE.md`, `THEME_TOKEN_SPEC.md`.*
