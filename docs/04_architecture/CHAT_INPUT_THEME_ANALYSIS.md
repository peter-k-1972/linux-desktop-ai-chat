# Chat Input Panel – Theme-Analyse

**Stand:** 2026-03-17  
**Ziel:** Vollständige Theme-Integration des ChatInputPanel.

---

## 1. Hardcoded Farben

| Widget | Farbe | Verwendung |
|--------|-------|------------|
| model_label | #6b7280 | Textfarbe |
| status_label | #6b7280 | Textfarbe (set_status) |
| status_label | #dc2626 | Fehlerfarbe (set_error) |
| #modelCombo | white, #e5e7eb | Hintergrund, Rahmen |
| #promptButton | #f3f4f6, #374151, #e5e7eb, #d1d5db | BG, Text, Border, Hover |
| #chatInput | white, #e5e7eb, #2563eb | BG, Border, Focus |
| #sendButton | #2563eb, white, #1d4ed8, #1e40af, #9ca3af | BG, Text, Hover, Pressed, Disabled |
| Kontextmenü (input) | #374151, #4b5563, #f3f4f6, #9ca3af | Menu BG, Hover, Text, Disabled |
| chatPromptMenu | #374151, #4b5563, #f3f4f6, #9ca3af | Gleich |

---

## 2. Aktuelle Stylesheets

- **model_label:** `color: #6b7280; font-size: 11px;`
- **#modelCombo:** background white, border #e5e7eb, radius 8px
- **status_label:** dynamisch (set_status/set_error)
- **#promptButton:** hellgrau, Hover/Pressed
- **#chatInput:** weiß, Fokus blau
- **#sendButton:** blau, Hover/Pressed/Disabled
- **QMenu:** dark-only

---

## 3. Abweichungen zum Theme-System

- Keine Nutzung von ThemeManager / get_tokens()
- Keine QSS-Token-Substitution
- Keine ObjectNames für QSS-Selektoren (modelCombo, chatInput, sendButton, promptButton vorhanden)
- model_label und status_label ohne ObjectNames

---

## 4. Risiken

| Risiko | Beschreibung |
|--------|--------------|
| Dark Mode | Weiße Felder auf dunklem Hintergrund |
| Kontrast | #6b7280 auf #f8fafc evtl. zu gering |
| Fokus | #2563eb grell in Dark Mode |
| Disabled | #9ca3af passt nicht zu Dark Theme |
