# Chat-Layout-Refactor — Abschlussbericht

## 1. Executive Summary

Der Chat-Layoutpfad wurde an das kanonische Spacing- und Größenraster angebunden: die feste **1200px**- bzw. **1000px**-Breitenlogik ist entfernt, Lesespalte und Legacy-Composer wachsen elastisch bis **800px** (`CHAT_CONTENT_MAX_WIDTH_PX`). Vertikale Abstände im Legacy-`ConversationView` nutzen **20px** Padding und **16px** Nachrichtenabstand (4px-Raster). Workspace-**ChatInputPanel**-Buttons sind von **48px** auf **32px** (Prompt) bzw. **40px** (Senden) reduziert. Tests unter `tests/unit/gui/test_chat_layout_refactor.py` sichern Metriken und Resize-Stabilität ab.

## 2. Betroffene Dateien

- `app/gui/theme/design_metrics.py` — neue `CHAT_*` und Composer-Margin-Tupel  
- `app/gui/domains/operations/chat/panels/conversation_view.py`  
- `app/gui/domains/operations/chat/panels/chat_composer_widget.py`  
- `app/gui/domains/operations/chat/panels/chat_message_widget.py`  
- `app/gui/domains/operations/chat/panels/conversation_panel.py`  
- `app/gui/domains/operations/chat/panels/input_panel.py`  
- `app/gui/domains/operations/chat/panels/chat_message_bubble.py`  
- `app/resources/styles.py` — `#chatContainer` max-width  
- `docs/design/CHAT_LAYOUT_REFACTOR_NOTES.md` (Phase-0-Audit)  
- `docs/design/CHAT_LAYOUT_POLICY.md` (Policy)  
- `docs/design/CHAT_LAYOUT_REFACTOR_REPORT.md` (dieses Dokument)  
- `docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md` — Chat-Zeilen aktualisiert  
- `docs/design/LAYOUT_SYSTEM_RULES.md` — Abschnitt Chat  
- `tests/unit/gui/test_chat_layout_refactor.py`  

## 3. Alte Werte → neue Werte

| Bereich | Alt | Neu |
|---------|-----|-----|
| Conversation-Spalte | min/max **1200** | min **0**, max **800** |
| Message layout | margins **32,40,32,40**, spacing **28** | **20** (`PANEL_PADDING_PX`), spacing **16** (`SPACE_LG_PX`) |
| Composer-Container | **1000** min/max | elastisch, max **800** |
| Composer-Wrapper | **24,16,24,24** | `CHAT_COMPOSER_WRAPPER_MARGINS_LTRB` (20,16,20,20) |
| Composer-Innen | **16,12,12,12** | `CHAT_COMPOSER_INNER_MARGINS_LTRB` (16,12,12,12) |
| Send (Legacy Composer) | **44×44** | **40×40** |
| ChatInput Min-Höhe (1 Zeile) | effektiv **52** | **40** (`INPUT_MD_HEIGHT_PX` + 8px Puffer) |
| Legacy-Bubble max | **1160** | **720** (`CHAT_BUBBLE_MAX_WIDTH_PX`) |
| Workspace-Verlauf | 20/16 (hart) | gleiche Zahlen aus `design_metrics` |
| InputPanel margins | 16,12,16,16 / spacing 8 | `CARD_PADDING` / `SPACE_MD` / `SPACE_SM` |
| InputPanel Prompt/Send | **48** / **48** | **32** / **40** |
| QSS `#chatContainer` | max-width **1200px** → **800px** Literal | **Interpolation** aus `CHAT_CONTENT_MAX_WIDTH_PX` in `styles.py` (siehe Tokenization-Report) |

## 4. Entfernte harte Breiten

- `conversation_view.py`: **1200** min/max auf der Nachrichtenspalte.  
- `chat_composer_widget.py`: **1000** min/max auf dem Composer-Container.  
- QSS: zunächst **800px** Literal — **nachgebessert:** nur noch `CHAT_CONTENT_MAX_WIDTH_PX` (siehe `CHAT_WIDTH_TOKENIZATION_REPORT.md`).

## 5. Neue Width-Policy

Siehe **CHAT_LAYOUT_POLICY.md**: zentrierte Spalte mit **max 800px**, **min 0**, horizontales Scrollen der ScrollArea weiterhin aus; Lesekorridor bewusst unter 960px für ruhigere Zeilenlänge.

## 6. Neue Composer- und Button-Höhen

- Legacy `ChatComposerWidget`: Send **40px**; Eingabezeile mindestens **40px** Höhe, wächst mit Text bis 200px.  
- `ChatInputPanel`: Modell-Combo **32px** min; Prompt **32px**; Senden **40px**; unten ausgerichtet zur mehrzeiligen Eingabe.

## 7. Bubble-Policy

- **Legacy** (`ChatMessageWidget`): `CHAT_BUBBLE_MAX_WIDTH_PX` = **720**.  
- **Workspace**: Markdown-Bubbles ohne festes `maximumWidth`; begrenzend wirken Panel-Padding und Viewport.

## 8. Teststatus

- Neu: `tests/unit/gui/test_chat_layout_refactor.py` — Instanziierung, keine 1200/1000-Zwänge, Resize, Bubble-Max, Button-Höhen nach Layout.  
- Bestehende UI-Tests (`tests/ui/test_chat_ui.py`, Smoke/Regression) sollten unverändert lauffähig bleiben (gleiche öffentliche API).

## 9. Restrisiken

- Sehr schmale Center-Spalte: lange ungebrochene Strings können Layout stressen (wie zuvor; WordWrap wo aktiv).  
- Legacy-QSS (`light.qss` / `dark.qss` für altes `#chatWidget`) unangetastet — nur `styles.py`-Theme-Strings für `#chatContainer`.  
- Visuelle Feinjustierung auf HiDPI: nicht Gegenstand dieses Schritts.

## 10. Empfohlene Folgearbeiten

- ~~Optional: Theme-Platzhalter für `#chatContainer`~~ — erledigt über `design_metrics`-Interpolation in `styles.py` (`CHAT_WIDTH_TOKENIZATION_REPORT.md`).  
- Chat-Navigation vs. Content: bei Bedarf einheitliches horizontales **20px**-Padding am `ChatWorkspace`-Center prüfen (derzeit 0 am Host, Padding im Scroll-Content).  
- Multiline-Composer **60–120** aus LAYOUT_SYSTEM_RULES als benannte Konstanten für `QTextEdit` in `input_panel` evaluieren.

---

## Pflichtfragen

**A. Ist der Chat jetzt in das globale Layoutsystem integriert?**  
Ja: Abstände und Höhen beziehen sich auf `design_metrics` / bestehende Rasterkonstanten; Policy in `CHAT_LAYOUT_POLICY.md` und `LAYOUT_SYSTEM_RULES.md` Abschnitt Chat.

**B. Wurden horizontale Layout-Zwänge aufgelöst?**  
Ja: keine erzwungenen 1200/1000px mehr auf den Kern-Widgets; obere Grenze nur noch als **max-width** 800px.

**C. Ist die neue Lesebreite für typische Desktopfenster stimmig?**  
800px max gilt als Kompromiss im Korridor 720–960; auf gängigen Fenstern (~1000–1400px nutzbare Breite) bleibt die Spalte lesbar ohne Ultrawide-Zeilen.

**D. Welche Chat-spezifischen Sonderregeln bleiben bewusst bestehen?**  
Send-Aktion **40px** (statt 32px); Legacy-Bubble-QSS-Padding im Python-String in `chat_message_widget.py` unverändert; zwei parallele Chat-UI-Pfade (Workspace vs. Legacy) mit gemeinsamen Metriken nur wo sinnvoll.
