# Chat Theme Hardening – Abschlussreport

**Stand:** 2026-03-17  
**Task:** Visuelle und thematische Konsistenz im Chatbereich (Dark/Light Mode).

---

## 1. Identifizierte Probleme

| Problem | Ort | Beschreibung |
|---------|-----|--------------|
| Hardcoded Bubble-Farben | ChatMessageBubbleWidget | #dbeafe, white, #93c5fd, #e5e7eb |
| Hardcoded Label-Farben | role_label, _content, _status_badge | #1e40af, #374151, #1f2937, #6b7280 |
| Hardcoded ScrollArea | ChatConversationPanel | #f8fafc |
| Dark-only Kontextmenü | _MessageContentEdit | #374151, #4b5563, #f3f4f6 |
| Keine Theme-Integration | ChatMessageBubbleWidget | Nutzte kein Theme-System |

---

## 2. Entfernte hardcoded Farben

| Komponente | Entfernt |
|------------|----------|
| ChatMessageBubbleWidget | setStyleSheet für Bubble, role_label, _content, _status_badge |
| ChatConversationPanel | setStyleSheet für QScrollArea |
| _MessageContentEdit | Kontextmenü-Farben (ersetzt durch Theme-Tokens) |

---

## 3. Eingeführte Theme-Nutzung

### 3.1 shell.qss (assets/themes/base/shell.qss)

Neue Chat-Styles mit Token-Substitution:

- **#chatConversationPanel** – Transparenter Container
- **#chatConversationPanel QScrollArea** – Hintergrund {{color_bg_muted}}
- **#messageBubble** – Basis (radius, padding, margin)
- **#messageBubble[role="user"]** – {{color_accent_bg}}, {{color_accent_hover}}
- **#messageBubble[role="assistant"]** – {{color_bg_surface}}, {{color_border}}
- **#messageBubble #messageRoleLabel** – Typografie
- **#messageBubble[role="user"] #messageRoleLabel** – {{color_accent}}
- **#messageBubble[role="assistant"] #messageRoleLabel** – {{color_text_secondary}}
- **#messageBubble #messageContent** – {{color_text}}
- **#messageBubble #messageStatusBadge** – {{color_text_muted}}

### 3.2 ChatMessageBubbleWidget

- **setProperty("role", "user"|"assistant")** – für QSS-Selektor
- **objectName "messageRoleLabel"** – für role_label
- **objectName "messageContent"** – für _MessageContentEdit
- **objectName "messageStatusBadge"** – für _status_badge

### 3.3 Kontextmenü

- **_get_chat_menu_style()** – liest get_theme_manager().get_tokens()
- Verwendet color_bg_surface, color_text, color_bg_hover
- Fallback bei fehlendem ThemeManager

---

## 4. Bubble-Farblogik

| Rolle | Hintergrund | Rahmen | Label-Farbe |
|-------|-------------|--------|-------------|
| User | color_accent_bg | color_accent_hover | color_accent |
| Assistant | color_bg_surface | color_border | color_text_secondary |

**Light Mode:** User blau getönt, Assistant weiß.  
**Dark Mode:** User dunkelblau, Assistant dunkle Fläche.

---

## 5. Tests

**Datei:** `tests/ui/test_chat_theme.py`

| Test | Prüfung |
|------|---------|
| test_bubble_has_role_property | role-Property gesetzt |
| test_bubble_user_and_assistant_differ | User ≠ Assistant |
| test_bubble_metadata_labels_have_object_names | messageRoleLabel, messageStatusBadge |
| test_content_has_object_name | messageContent |
| test_conversation_panel_no_hardcoded_scroll_style | Kein #f8fafc |
| test_theme_switch_does_not_break_chat | Theme-Wechsel robust |

**Bestehende Tests:** test_chat_hardening, test_chat_message_rendering, test_chat_ux_hardening – alle bestanden.

---

## 6. Verbleibende Einschränkungen

| Bereich | Status |
|---------|--------|
| ChatInputPanel | Noch hardcoded (white, #e5e7eb, etc.) – außerhalb des Scopes |
| Agent-Bubble | Nutzt gleiche Logik wie Assistant (role="assistant") |
| Kontextmenü Fallback | Bei fehlendem ThemeManager: Dark-Fallback |

---

## 7. Empfohlene nächste Schritte

1. **ChatInputPanel:** Theme-Tokens für Modell-Combo, Input, Buttons
2. **Theme-Wechsel-Live-Update:** Bubbles bei theme_changed neu stylen (falls nötig – QSS wird global neu geladen)
3. **Kontrast-Check:** WCAG-Kontrast für color_text auf color_bg_surface prüfen
