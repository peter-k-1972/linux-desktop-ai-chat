# Chat Input Panel – Theme Hardening Report

**Stand:** 2026-03-17  
**Task:** Vollständige Theme-Integration des ChatInputPanel.

---

## 1. Entfernte Hardcoded Styles

| Widget | Entfernt |
|--------|----------|
| model_label | setStyleSheet("color: #6b7280; font-size: 11px;") |
| status_label | setStyleSheet (dynamisch in set_status/set_error) |
| #modelCombo | setStyleSheet (white, #e5e7eb) |
| #promptButton | setStyleSheet (#f3f4f6, #374151, #e5e7eb, #d1d5db) |
| #chatInput | setStyleSheet (white, #e5e7eb, #2563eb) |
| #sendButton | setStyleSheet (#2563eb, white, #1d4ed8, #1e40af, #9ca3af) |
| Kontextmenü (input) | setStyleSheet → _get_chat_menu_style() |
| chatPromptMenu | setStyleSheet → _get_chat_menu_style() |

---

## 2. Neue QSS-Integration

**Datei:** assets/themes/base/shell.qss

### #chatInputPanel

- Container: `background: transparent`

### Labels

- `#modelLabel`, `#statusLabel`: `color: {{color_text_secondary}}`, `font-size: {{font_size_xs}}`
- `#statusLabel[error="true"]`: `color: {{color_error}}`, `font-weight: {{font_weight_semibold}}`

### #modelCombo

- `background: {{color_bg_surface}}`, `color: {{color_text}}`, `border: {{color_border}}`
- `:focus`: `border-color: {{color_accent}}`

### #promptButton

- `background: {{color_bg_hover}}`, `color: {{color_text}}`, `border: {{color_border}}`
- `:hover`: `background: {{color_border_medium}}`
- `:pressed`: `background: {{color_border}}`

### #chatInput

- `background: {{color_bg_surface}}`, `color: {{color_text}}`, `border: {{color_border}}`
- `:focus`: `border-color: {{color_accent}}`

### #sendButton

- `background: {{color_accent}}`, `color: {{color_text_inverse}}`
- `:hover`: `background: {{color_accent_hover}}`
- `:pressed`: `background: {{color_accent_hover}}`
- `:disabled`: `background: {{color_border_medium}}`, `color: {{color_text_muted}}`

---

## 3. Verwendete Tokens

| Token | Verwendung |
|-------|------------|
| color_bg_surface | modelCombo, chatInput, sendButton (via QSS) |
| color_text | modelCombo, promptButton, chatInput |
| color_text_secondary | modelLabel, statusLabel |
| color_text_muted | sendButton:disabled |
| color_text_inverse | sendButton |
| color_border | modelCombo, promptButton, chatInput |
| color_border_medium | promptButton:hover, sendButton:disabled |
| color_accent | modelCombo:focus, chatInput:focus, sendButton |
| color_accent_hover | sendButton:hover, sendButton:pressed |
| color_bg_hover | promptButton |
| color_error | statusLabel[error="true"] |
| font_size_xs, font_size_sm, font_size_base, font_size_md | Typografie |
| font_weight_semibold | statusLabel error |
| radius_md, radius_xl, spacing_* | Abstände, Radien |

---

## 4. Code-Änderungen

- **ChatInputPanel:** Alle setStyleSheet entfernt; ObjectNames modelLabel, statusLabel
- **set_status/set_error:** setProperty("error", "true"/"false"); _refresh_status_style()
- **Kontextmenüs:** _get_chat_menu_style() aus chat_message_bubble importiert
- **ThemeRegistry:** color_text_inverse explizit in light_default und dark_default

---

## 5. Tests

**Datei:** tests/ui/test_chat_input_theme.py

| Test | Prüfung |
|------|---------|
| test_input_panel_no_hardcoded_colors | Keine hardcoded Hex-Farben |
| test_input_field_readable | Input lesbar und nutzbar |
| test_send_button_visible_and_clickable | Senden-Button funktioniert |
| test_model_combo_has_object_name | modelCombo ObjectName |
| test_labels_have_object_names | statusLabel ObjectName |
| test_theme_switch_does_not_break_input_panel | Theme-Wechsel robust |

---

## 6. Verbleibende Einschränkungen

- **Placeholder-Text:** QTextEdit-Placeholder-Farbe kann plattformabhängig sein
- **QComboBox-Dropdown:** Dropdown-Styling kommt vom globalen Theme; ggf. spezifisch in shell.qss ergänzen
