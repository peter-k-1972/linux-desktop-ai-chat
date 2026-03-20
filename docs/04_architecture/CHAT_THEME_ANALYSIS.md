# Chat Theme – Analyse

**Stand:** 2026-03-17  
**Ziel:** Visuelle und thematische Konsistenz im Chatbereich (Dark/Light Mode).

---

## 1. Hardcoded Farben im Chat

### 1.1 ChatMessageBubbleWidget

| Stelle | Farbe | Verwendung |
|--------|-------|------------|
| #messageBubble (user) | #dbeafe | Hintergrund User-Bubble |
| #messageBubble (user) | #93c5fd | Rahmen User-Bubble |
| #messageBubble (assistant) | white | Hintergrund Assistant-Bubble |
| #messageBubble (assistant) | #e5e7eb | Rahmen Assistant-Bubble |
| role_label (user) | #1e40af | Textfarbe |
| role_label (assistant) | #374151 | Textfarbe |
| _content | #1f2937 | Textfarbe Content |
| _status_badge | #6b7280 | Textfarbe Status |

### 1.2 _MessageContentEdit

| Stelle | Farbe | Verwendung |
|--------|-------|------------|
| contextMenuEvent QMenu | #374151, #4b5563, #f3f4f6 | Kontextmenü (dark-only) |

### 1.3 ChatConversationPanel

| Stelle | Farbe | Verwendung |
|--------|-------|------------|
| QScrollArea | #f8fafc | Hintergrund Scroll-Bereich |

### 1.4 ChatInputPanel

| Stelle | Farbe | Verwendung |
|--------|-------|------------|
| model_label, status_label | #6b7280 | Text |
| #modelCombo | white, #e5e7eb | Hintergrund, Rahmen |
| #promptButton | #f3f4f6, #374151, #e5e7eb | Hintergrund, Text, Rahmen |
| #chatInput | white, #e5e7eb, #2563eb | Hintergrund, Rahmen, Focus |
| #sendButton | #2563eb, #1d4ed8, #1e40af | Hintergrund, Hover, Pressed |

---

## 2. Wo Theme bereits genutzt wird

| Komponente | Theme-System |
|------------|--------------|
| ChatMessageWidget (Legacy) | get_theme_colors(theme) |
| ConversationView (Legacy) | theme-Prop, get_theme_colors |
| ModelSettingsPanel | get_theme_colors |
| ThemeManager | get_theme_manager(), get_tokens() |
| Shell (QSS) | {{token}}-Substitution |

**ChatConversationPanel / ChatMessageBubbleWidget:** Nutzen **kein** Theme-System.

---

## 3. Inkonsistenzen

- **ChatMessageBubbleWidget:** Immer hell (weiß, #dbeafe) – bei Dark Mode: weiß auf dunklem Hintergrund
- **ChatConversationPanel:** #f8fafc – hell, passt nicht zu Dark Mode
- **Kontextmenü:** Dark-only (#374151) – bei Light Mode schlecht lesbar
- **ChatInputPanel:** Komplett hell – bei Dark Mode inkonsistent

---

## 4. Dark/Light Risiken

| Szenario | Risiko |
|----------|--------|
| Dark Mode + weiße Bubbles | Blendend, inkonsistent |
| Light Mode + dunkles Kontextmenü | Ungewöhnlich, aber lesbar |
| Dark Mode + #f8fafc ScrollArea | Heller Fleck in dunkler UI |
| Dark Mode + ChatInputPanel | Weiße Eingabefelder stechen heraus |

---

## 5. Empfohlene Lösung

1. **Chat-Styles in shell.qss:** #chatConversationPanel, #messageBubble[role="user"], #messageBubble[role="assistant"] mit Theme-Tokens
2. **ChatMessageBubbleWidget:** setProperty("role", ...), keine setStyleSheet für Bubble/Labels
3. **Kontextmenü:** Farben aus get_theme_manager().get_tokens()
4. **ChatInputPanel:** Theme-Tokens (separater Task oder gleicher Scope)

**Scope dieses Tasks:** ChatMessageBubbleWidget, ChatConversationPanel, _MessageContentEdit (Kontextmenü). ChatInputPanel optional.
