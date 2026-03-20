# Chat-Härtung – Analyse

**Stand:** 2026-03-17  
**Ziel:** Chatbereich auf produktiv nutzbares Niveau bringen – Rendering, Copy/Paste, Modell-/Agentenkennzeichnung.

---

## 1. Aufbau des Chatbereichs

### 1.1 Architektur

| Komponente | Pfad | Beschreibung |
|------------|------|--------------|
| ChatWorkspace | `app/gui/domains/operations/chat/chat_workspace.py` | Hauptcontainer: Session Explorer + Conversation + Input |
| ChatConversationPanel | `app/gui/domains/operations/chat/panels/conversation_panel.py` | Nachrichtenverlauf, ScrollArea, Message-Bubbles |
| ChatInputPanel | `app/gui/domains/operations/chat/panels/input_panel.py` | QTextEdit-Eingabe, Modell-ComboBox, Senden |
| ChatMessageWidget | `app/gui/domains/operations/chat/panels/chat_message_widget.py` | Legacy: Bubble für ConversationView |
| ConversationView | `app/gui/domains/operations/chat/panels/conversation_view.py` | Legacy: nutzt ChatMessageWidget |

**Aktiver Pfad (Shell):** ChatWorkspace → ChatConversationPanel → `_create_message_bubble()` mit QLabel.

**Legacy-Pfad:** chat_widget.py → ConversationView → ChatMessageWidget (QLabel mit TextSelectableByMouse).

### 1.2 Message-Rendering (ChatConversationPanel)

- **Bubble:** QFrame mit QVBoxLayout
- **Rollen-Label:** QLabel ("Du" / "Assistent")
- **Text-Label:** QLabel mit `setWordWrap(True)`, **ohne** `setTextInteractionFlags`
- **Layout:** QScrollArea → QWidget (_content) → QVBoxLayout mit `addStretch()` am Ende
- **Streaming:** `add_assistant_placeholder()` → `update_last_assistant(text)` → `finalize_streaming()`

### 1.3 Datenmodell

- **load_chat:** `(role, content, timestamp)` – keine Modell-/Agent-Metadaten
- **save_message:** `(chat_id, role, content)` – keine Modell-/Agent-Metadaten
- **DB-Schema:** `messages(chat_id, role, content, timestamp)` – keine `model`/`agent`-Spalte

---

## 2. Ursache(n) für abgeschnittene Antworten

### 2.1 QLabel-Verhalten bei langem Text

- **QLabel** mit `setWordWrap(True)` berechnet die Höhe über `sizeHint()` basierend auf der verfügbaren Breite.
- Bei sehr langen Texten kann die Höhenberechnung in manchen Qt-Versionen/Layouts fehlerhaft sein.
- **Kein** `setSizePolicy` für das Text-Label → Standard ist `Preferred`/`Preferred`.
- **Kein** `setMinimumHeight`/`setMaximumHeight` auf der Bubble – theoretisch sollte das Layout korrekt sein.

### 2.2 Wahrscheinliche Ursachen

1. **QLabel sizeHint-Caching:** Bei Streaming-Updates kann der sizeHint veraltet sein, bis ein Layout-Pass erfolgt.
2. **Layout-Stretch:** `addStretch()` am Ende kann in Kombination mit vielen Bubbles zu unerwarteter Höhenverteilung führen.
3. **ScrollArea-Viewport:** `setWidgetResizable(True)` ist gesetzt – korrekt.
4. **Fehlende SizePolicy:** Text-Label hat keine explizite `MinimumExpanding`-Policy für die vertikale Achse.

### 2.3 Empfohlene Lösung

- **QTextEdit** (read-only) statt QLabel für Nachrichtentext:
  - Robuste Darstellung beliebig langer Texte
  - Native Textselektion und Copy
  - Keine sizeHint-Probleme bei langem Inhalt
  - `setFrameShape(NoFrame)`, `setReadOnly(True)`, `setTextInteractionFlags(TextSelectableByMouse)`

---

## 3. Copy/Paste-Situation

### 3.1 Eingabefeld (ChatInputPanel)

- **QTextEdit** – hat standardmäßig Cut/Copy/Paste/Select All über Tastatur (Strg+X/C/V/A).
- **Rechtsklick:** Plattformabhängig – unter Linux/GTK oft kein natives Kontextmenü.
- **Fehlend:** Explizites `contextMenuEvent` oder `customContextMenuRequested` für Cut/Copy/Paste/Select All.

### 3.2 Chatantworten (ChatConversationPanel)

- **QLabel** ohne `setTextInteractionFlags` → **Text nicht auswählbar**, kein Copy möglich.
- **Kein** Kontextmenü auf Message-Bubbles.
- **ChatMessageWidget** (Legacy): Hat `setTextInteractionFlags(Qt.TextSelectableByMouse)` – Copy per Selektion möglich, aber kein Rechtsklick-Menü.

### 3.3 Empfohlene Lösung

- **Eingabefeld:** Explizites Kontextmenü (Cut, Copy, Paste, Select All) für plattformunabhängige UX.
- **Chatantworten:** QTextEdit (read-only) mit TextSelectableByMouse + Kontextmenü (Copy, Select All).

---

## 4. Modell-/Agent-Metadaten

### 4.1 Aktuelle Verfügbarkeit

- **Beim Senden:** Modell ist bekannt (`_input.get_selected_model()`).
- **Beim Speichern:** `save_message(chat_id, role, content)` – Modell wird **nicht** persistiert.
- **Beim Laden:** `load_chat` liefert nur `(role, content, timestamp)`.
- **Agenten:** Kein Agent-Pfad im aktuellen ChatWorkspace-Flow (nur Modell-Chat).

### 4.2 Empfohlene Erweiterung (minimal-invasiv)

1. **DB-Migration:** `ALTER TABLE messages ADD COLUMN model TEXT` (optional: `agent TEXT`).
2. **save_message:** Optionaler Parameter `model` (und ggf. `agent`).
3. **load_chat:** Erweiterte Rückgabe `(role, content, timestamp, model, agent)` – Fallback `None`.
4. **UI:** Rolle-Label erweitern: "Assistent" → "Assistent (llama3.2)" bzw. "Agent (xyz)".
5. **Fallback:** Bei fehlenden Metadaten: "Assistent", "Agent", "Unbekanntes Modell".

---

## 5. Härtungsstrategie (minimal-invasiv)

| Priorität | Maßnahme | Betroffene Dateien |
|-----------|----------|-------------------|
| 1 | QTextEdit statt QLabel für Nachrichtentext | conversation_panel.py |
| 2 | SizePolicy, WordWrap, Layout für robustes Rendering | conversation_panel.py |
| 3 | Kontextmenü Eingabefeld (Cut/Copy/Paste/Select All) | input_panel.py |
| 4 | Kontextmenü Chatantworten (Copy/Select All) | conversation_panel.py |
| 5 | DB: model-Spalte + save_message/load_chat erweitern | database_manager.py, chat_service.py |
| 6 | Modell-Label pro Assistant-Nachricht | conversation_panel.py, chat_workspace.py |

**Keine Änderungen an:** Agent-Logik, ComfyUI, ConversationView (Legacy) – nur ChatConversationPanel und zugehörige Services.
