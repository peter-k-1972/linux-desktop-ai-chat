# Chat-Breite — Tokenisierung / Abschlussbericht

## 1. Alte Quelle → neue Quelle

| Vorher | Nachher |
|--------|---------|
| `CHAT_CONTENT_MAX_WIDTH_PX` in Python-Widgets **und** Literal `max-width: 800px` in `app/resources/styles.py` (zwei Quellen) | **Eine Quelle:** `design_metrics.CHAT_CONTENT_MAX_WIDTH_PX`; `styles.py` interpoliert denselben Wert in die QSS-f-Strings (`_dm.CHAT_CONTENT_MAX_WIDTH_PX`). |

## 2. Geänderte / neue Dateien

- `app/resources/styles.py` — Import `design_metrics` als `_dm`; `#chatContainer` nutzt `{_dm.CHAT_CONTENT_MAX_WIDTH_PX}px`
- `docs/design/CHAT_WIDTH_TOKENIZATION_NOTES.md` — IST-Analyse
- `docs/design/CHAT_WIDTH_TOKENIZATION_REPORT.md` — dieser Bericht
- `docs/design/CHAT_LAYOUT_POLICY.md` — QSS-Abschnitt aktualisiert
- `docs/design/CHAT_LAYOUT_REFACTOR_REPORT.md` — Tabellenzeile + Folgearbeiten
- `tests/unit/gui/test_chat_width_tokenization.py` — neue Tests

## 3. Gewählte technische Strategie

`app/resources/styles.py` wird von `app/main.py` als **Python-Generator** aufgerufen, **nicht** durch `app/gui/themes/loader.py` (der nur `assets/themes/base/*.qss` mit `{{token}}` ersetzt). Daher:

- **Kein** neues `{{chat_content_max_width_px}}` in separater QSS ohne Umbau des Legacy-Pfads.
- **Stattdessen:** zur Build-Zeit des Strings dieselbe Metrik wie in `conversation_view` / `chat_composer_widget` einbinden.

Damit ist die Architektur minimal-invasiv und ohne zweite Konstante.

## 4. Teststatus

- `tests/unit/gui/test_chat_width_tokenization.py` — prüft Abwesenheit von `max-width: 800px` in `styles.py`, Vorkommen der Interpolation, und Übereinstimmung des erzeugten QSS mit `dm.CHAT_CONTENT_MAX_WIDTH_PX` sowie `ConversationView.message_container.maximumWidth()`.

## 5. Verbleibende Restrisiken

- **Zwei App-Pfade:** Shell/Workbench nutzt ThemeManager-QSS ohne diesen `#chatContainer`-Block — nur betroffen, wer `get_stylesheet` aus `app.resources.styles` lädt.
- **Änderung der Konstante:** Wirkt sofort auf Python und auf neu generiertes Legacy-QSS; kein verstecktes drittes Chat-Max-Width mehr in `styles.py`.

---

## Zusatzfragen

**A. Gibt es jetzt nur noch eine kanonische Quelle?**  
Ja für den numerischen Wert: `design_metrics.CHAT_CONTENT_MAX_WIDTH_PX`. `styles.py` enthält keine eigene Zahl mehr.

**B. Ist `styles.py` frei von Chat-Breiten-Magic-Numbers?**  
Ja — kein Literal `800` / `800px` für `#chatContainer`; nur Verweis auf `_dm.CHAT_CONTENT_MAX_WIDTH_PX`.

**C. Welche weiteren QSS/Python-Doppelquellen ähnlicher Art gibt es noch?**  
- Viele **Farben** in `styles.py` vs. Theme-Tokens im Loader-Pfad — bewusst Legacy.  
- **Chat-Bubble-Padding** in `chat_message_widget.py` (Inline-Stylesheet-String) ist weiterhin layout-/farbgebunden, nicht über `CHAT_BUBBLE_MAX_WIDTH` hinaus zentralisiert.  
- Sonstige feste **px** in `styles.py` (Radii, Padding) sind nicht Teil dieses Schritts.
