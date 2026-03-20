# Chat Message Rendering – Architekturanalyse

**Stand:** 2026-03-17  
**Ziel:** Einheitliche, robuste Message-Rendering-Architektur für den Chatbereich.

---

## 1. Übersicht der Message-Komponenten

### 1.1 Aktive Komponenten

| Komponente | Datei | Verwendung | Rendering-Pfad |
|------------|-------|------------|----------------|
| **ChatMessageBubbleWidget** | `chat_message_bubble.py` | ChatConversationPanel (neue UI) | Standardpfad |
| **ChatMessageWidget** | `chat_message_widget.py` | ConversationView (Legacy) | Legacy-Pfad |

### 1.2 Container und Kontext

| Container | Datei | Message-Komponente | Kontext |
|-----------|-------|--------------------|---------|
| **ChatConversationPanel** | `conversation_panel.py` | ChatMessageBubbleWidget | ChatWorkspace (Shell) |
| **ConversationView** | `conversation_view.py` | ChatMessageWidget | Legacy ChatWidget |

---

## 2. Detaillierte Komponentenanalyse

### 2.1 ChatMessageBubbleWidget (Neue UI)

**Struktur:**
```
ChatMessageBubbleWidget (QFrame)
└── QVBoxLayout
    ├── QLabel (role_label) – "Du" / "Assistent (model)" / "Agent (name)"
    ├── _MessageContentEdit (QTextEdit, read-only)
    └── QLabel (_status_badge) – Completion-Status optional
```

**Eigenschaften:**
- **Content:** `_MessageContentEdit` – QTextEdit mit PlainText
- **SizePolicy:** Expanding/Minimum (Bubble + Content)
- **Breitenlogik:** `_effective_document_width()` – Fallback bei viewport < 100 auf 400, Obergrenze 700
- **Höhenlogik:** `sizeHint()` aus `document.size().height() + 8`, min 24
- **updateGeometry:** In `setPlainText()` und `set_content()` – Layout wird neu berechnet
- **Metadaten:** Rolle, Modell, Agent, Completion-Status
- **Interaktion:** TextSelectableByMouse, Kontextmenü (Copy, Select All)
- **Streaming:** `set_content()` für Updates

**Stärken:**
- Robuste Breitenberechnung mit Fallbacks
- Korrekter updateGeometry-Pfad
- Metadatenzeile (Rolle, Modell, Agent, Status)
- Copy/Selection/Kontextmenü
- Keine festen Höhen

### 2.2 ChatMessageWidget (Legacy)

**Struktur:**
```
ChatMessageWidget (QWidget)
└── QHBoxLayout
    ├── Avatar (QLabel, 32x32)
    ├── QVBoxLayout (bubble_container)
    │   ├── QLabel (bubble) – Text
    │   └── QLabel (timestamp)
    └── [Stretch je nach Rolle]
```

**Eigenschaften:**
- **Content:** QLabel mit setWordWrap(True)
- **SizePolicy:** Preferred/Minimum (bubble)
- **Breitenlogik:** `setMaximumWidth(1160)` – feste Obergrenze
- **Höhenlogik:** QLabel – kein sizeHint aus Inhalt, Layout bestimmt Höhe
- **Metadaten:** Keine Rolle/Modell/Agent; Timestamp, Avatar
- **Interaktion:** TextSelectableByMouse, **kein Kontextmenü**
- **Streaming:** `set_content()` – unterstützt PlainText und RichText

**Schwächen:**
- Keine stabile Höhenberechnung aus Inhalt
- Keine Metadatenzeile (Modell, Agent)
- Kein Kontextmenü
- Feste Max-Breite 1160
- Theme-abhängig (get_theme_colors)

### 2.3 _MessageContentEdit (intern)

**Rolle:** Read-only QTextEdit für ChatMessageBubbleWidget.

**Kernlogik:**
- `setPlainText()` → `updateGeometry()` nach Textänderung
- `_effective_document_width()`: viewport ≥ 100 → min(viewport, 700); sonst parent oder 400
- `sizeHint()`: doc.setTextWidth(effective_width), h = doc.size().height() + 8
- `resizeEvent`: document.setTextWidth(viewport().width())

---

## 3. Unterschiede Alt vs. Neu

| Aspekt | ChatMessageBubbleWidget | ChatMessageWidget |
|--------|-------------------------|-------------------|
| Content-Widget | QTextEdit | QLabel |
| SizePolicy (vertikal) | Minimum | Minimum |
| Breite | _effective_document_width, max 700 | setMaximumWidth(1160) |
| Höhe | sizeHint aus Dokument | Layout/QLabel |
| updateGeometry | Ja, bei Textänderung | Nein |
| Rolle/Modell/Agent | Ja (role_label) | Nein |
| Completion-Status | Ja (_status_badge) | Nein |
| Kontextmenü | Copy, Select All | Kein |
| Timestamp | Nein | Ja |
| Avatar | Nein | Ja |
| Theme | Hardcoded (hell) | get_theme_colors |
| Streaming | set_content | set_content |

---

## 4. Welche Komponente ist zukunftsfähig?

**ChatMessageBubbleWidget** ist die zukunftsfähige Komponente:

1. Robuste Höhen-/Breitenlogik
2. Korrekter updateGeometry-Pfad
3. Metadaten (Rolle, Modell, Agent, Status)
4. Copy/Selection/Kontextmenü
5. Bereits in ChatConversationPanel (aktiver Pfad) integriert

**ChatMessageWidget** bleibt für Legacy (ConversationView) erforderlich, bis eine Migration erfolgt. Es sollte:
- Keine neuen Features erhalten
- Als Übergang behandelt werden
- Keine doppelte Rendering-Logik verursachen

---

## 5. Empfohlene Zielarchitektur

### 5.1 Primäre Message-Komponente

**ChatMessageBubbleWidget** als einzige Standard-Komponente für den Chatbereich.

### 5.2 Vereinheitlichungsstrategie

1. **ChatConversationPanel:** Nutzt bereits ChatMessageBubbleWidget – Standardpfad.
2. **ConversationView:** Nutzt weiterhin ChatMessageWidget – Legacy, keine Änderung im Scope.
3. **Keine Doppelwahrheit:** Keine parallele Implementierung gleicher Logik in beiden Komponenten.
4. **ChatMessageBubbleWidget:** Klar dokumentiert als Standard; alle neuen Chat-Features hier.

### 5.3 Zu vereinheitlichende Prinzipien

- **SizePolicy:** Expanding/Minimum (horizontal/vertikal) für Message-Container
- **Breitenlogik:** Stabile effective_width mit Fallback (kein viewport() allein)
- **Höhenlogik:** sizeHint aus Inhalt, updateGeometry bei Textänderung
- **Metadaten:** Einheitliche Struktur (Rolle, Modell, Agent, Status)
- **Interaktion:** Copy, Selection, Kontextmenü als Basis

### 5.4 Metadatenzeile / Badge-Struktur

ChatMessageBubbleWidget unterstützt bereits:
- **role_label:** "Du" / "Assistent (model)" / "Agent (name)"
- **_status_badge:** "möglicherweise unvollständig", "Antwort unterbrochen", "Generierung beendet mit Fehler"

Erweiterbar für: Debug-Hinweise, weitere Status-Labels.

---

## 6. Copy-/Selection-Verhalten

| Komponente | TextSelectableByMouse | Kontextmenü | Copy |
|------------|-----------------------|-------------|------|
| ChatMessageBubbleWidget | Ja | Copy, Select All | Ja |
| ChatMessageWidget | Ja | Nein | Nur per Selektion |

---

## 7. Markdown-/Text-/RichText-Darstellung

| Komponente | Format | Anmerkung |
|------------|--------|-----------|
| ChatMessageBubbleWidget | PlainText | QTextEdit, setPlainText |
| ChatMessageWidget | PlainText oder RichText | QLabel, setTextFormat je nach Inhalt |

**Hinweis:** Markdown-Rendering ist nicht Teil dieses Tasks. Beide nutzen aktuell PlainText als Basis.

---

## 8. Zusammenfassung

| Empfehlung | Details |
|------------|---------|
| **Zielkomponente** | ChatMessageBubbleWidget |
| **Legacy** | ChatMessageWidget nur für ConversationView, als Übergang |
| **Vereinheitlichung** | SizePolicy, Breiten-/Höhenlogik, Metadaten, Interaktion in ChatMessageBubbleWidget |
| **Keine Änderung** | ConversationView behält ChatMessageWidget |
| **Nächste Schritte** | Tests für ChatMessageBubbleWidget, Dokumentation der Zielarchitektur |
