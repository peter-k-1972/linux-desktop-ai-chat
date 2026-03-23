# QSS vs. Python — Ownership-Regeln

Verbindliche Zuordnung **pro Eigenschaft**. Ziel: keine zwei Schichten setzen dieselbe Sache mit konkurrierenden Pixelwerten.

---

## 1. QSS besitzt (Owner: Theme / `assets/themes/base/*.qss` + Loader-Tokens)

| Eigenschaft | Gilt für |
|-------------|----------|
| Standard-**min-height** von `QPushButton`, `QComboBox`, `QLineEdit` (generisch, ohne spezielle Ausnahme-ID) | Alle Widgets, die nur generische Selektoren nutzen |
| **Padding**, **border**, **border-radius**, **Farbe**, **Schrift** für generische Typ-Selektoren | `QPushButton`, `QLineEdit`, `QComboBox`, `QTabBar::tab`, `QScrollBar`, … |
| **icon-size** (wo in QSS gesetzt) für Toolbars / spezifische IDs | Z. B. `#workbenchToolbar` |
| **Listen-/Tree-Item**-Darstellung (`::item` padding, min-height pro Liste-ID) | z. B. `#workbenchPaletteList`, `#workbenchNodeLibrary` |
| **Tab-Höhe** (über Padding/Border in QSS) | Shell-/Workbench-Tabs, sofern nicht Dialog-local |

**Konsequenz für Python:** Kein `setMinimumHeight` / `setFixedHeight` auf generischen `QComboBox`/`QLineEdit`, wenn `base.qss` bereits `min-height` setzt — außer **registrierte Ausnahme** (siehe unten).

---

## 2. Python besitzt (Owner: Widget-Code + `design_metrics` / `layout_constants`)

| Eigenschaft | Gilt für |
|-------------|----------|
| **QLayout**: `setContentsMargins`, `setSpacing`, Stretch, Alignment | Immer Python |
| **Splitter-, Dock-, Dialog-Mindestgrößen** (`setMinimumWidth/Height` auf Fenster/Panels) | Strukturentscheidung |
| **Inhaltsabhängige** Min/Max (mehrzeiliger Editor, Vorschau, Beschreibungsfeld) | z. B. `QTextEdit` 60–120, `setMaximumHeight` auf Beschreibung |
| **Responsive max-width** (Chat-Spalte, Composer) | `CHAT_CONTENT_MAX_WIDTH_PX` etc. |
| **Spezielle Button-Höhen** für definierte Domänen-Regeln | z. B. Chat **Send** `CHAT_PRIMARY_SEND_HEIGHT_PX`, Prompt-Zeile `INPUT_MD` — dokumentiert in CHAT_LAYOUT_POLICY |
| **objectName-spezifische** Größen nur wenn QSS für diese ID **keine** Höhe vorgibt | Sonst QSS anpassen und Python entfernen |

**Konsequenz für QSS:** Keine zusätzliche `min-height` auf derselben Widget-Instanz, wenn Python bereits die finale Höhe erzwingt — oder umgekehrt QSS lockern (`min-height: 0` für ID).

---

## 3. Verboten

1. **Dieselbe konkrete Größe zweimal** für dieselbe Property auf demselben Widget-Typ ohne dokumentierte Ausnahme (z. B. Combo: QSS 32px + Python 32px redundant; QSS 32px + Python 48px widersprüchlich).  
2. **Generische** `setFixedHeight` auf `QComboBox` / `QLineEdit`, nur um „32px“ zu erzwingen, wenn `base.qss` das bereits regelt.  
3. **Ad-hoc** `setStyleSheet("… padding: Npx; min-height: Mpx …")** in Python für Standard-Controls, wenn globales QSS dieselbe Rolle hat — Ausnahmen nur mit Eintrag in `QSS_PYTHON_CANONICAL_CASES.md`.  
4. **Neue Magic Numbers** (48, 14, 10, 28 …) ohne Raster/`design_metrics`-Bezug, wenn ein Token oder eine bestehende Konstante existiert.

---

## 4. Ausnahmen (explizit)

| Fall | Regel |
|------|--------|
| Zwei **App-Pfade** (Legacy `styles.py` vs. ThemeManager `base.qss`) | Doppelquelle möglich bis Migration; Legacy-Widgets priorisieren dokumentierte Konstanten. |
| **Chat Send** | Python-Owner Höhe 40px; Legacy-QSS `#sendButton` kann anderen Pfad haben — getrennte Apps/Pfade. |
| **Bubble/Chat-Message** | Vorübergehend Python-`setStyleSheet` für Bubble — Ausnahme bis Tokenisierung. |

---

## 5. Priorität bei Konflikt (Runtime)

1. **Spezifischere QSS-Selektor** (`#objectName`) schlägt generischen Typ — Qt-Kaskade.  
2. **Inline-Stylesheet** am Widget schlägt App-Stylesheet — deshalb Inline-Layout-Pixel vermeiden.  
3. **Python** `setFixedSize` setzt harte geometrische Grenzen unabhängig von QSS — darf nicht „heimlich“ QSS überschreiben ohne Ownership-Klarheit.

---

*Verwandt:* [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md), [CHAT_LAYOUT_POLICY.md](./CHAT_LAYOUT_POLICY.md).
