# QSS ↔ Python — Doppelquellen-Cleanup — Abschlussbericht

## 1. Executive Summary

Es wurde ein **referenzierbarer Rahmen** geschaffen: Audit, **verbindliche Ownership-Regeln**, kanonische Falltypen, sowie ein **heuristisches Guard-Tool** (`tools/layout_double_source_guard.py`). Im Code wurden **konkrete Hochnutzen-/Niedrigrisiko-Bereinigungen** umgesetzt: die Modell-**QComboBox** im Chat-Input setzt ihre Mindesthöhe nicht mehr in Python (QSS-Owner `base.qss`); die Legacy-**Sidebar** nutzt `design_metrics` statt freier Pixel-Literale für dieselben Größenklassen. Viele weitere Stellen (Inline-`setStyleSheet` mit Padding, 28-vs-32-Listen) sind **auditiert** und über den Guard **sichtbar**, aber nicht in einem Rutsch refaktoriert.

## 2. Wichtigste Konfliktarten

1. **Standard-Control-Höhe** doppelt (QSS `min-height` + Python `setMinimumHeight`).  
2. **Legacy `styles.py`** vs. **Theme-`base.qss`** — zwei Pfade.  
3. **Inline-Python-QSS** mit `padding`/`min-width` parallel zu globalem Theme.  
4. **Spezial-Buttons** (#newChatBtn): QSS-Padding und Python-Mindesthöhe (teilweise entschärft durch Metriken).  
5. **Listen-Dichte** 28px vs 32px — nur QSS, aber inkonsistent zwischen Widgets.

## 3. Neue / geänderte Dateien

| Datei |
|-------|
| `docs/design/QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md` |
| `docs/design/QSS_PYTHON_OWNERSHIP_RULES.md` |
| `docs/design/QSS_PYTHON_CANONICAL_CASES.md` |
| `docs/design/QSS_PYTHON_DOUBLE_SOURCE_CLEANUP_REPORT.md` (dieses Dokument) |
| `tools/layout_double_source_guard.py` |
| `tests/tools/test_layout_double_source_guard.py` |
| `tests/unit/gui/test_qss_python_ownership_rules.py` |
| `tests/unit/gui/test_layout_double_source_cleanup.py` |
| `app/gui/domains/operations/chat/panels/input_panel.py` |
| `app/gui/legacy/sidebar_widget.py` |
| `docs/design/LAYOUT_SYSTEM_RULES.md` (Verweis) |
| `docs/design/LAYOUT_SPACING_MIGRATION_PLAN.md` (Eintrag) |
| `docs/design/CHAT_LAYOUT_POLICY.md` (Ownership-Zeile) |

## 4. Fälle mit QSS-Owner (nach Regelwerk)

- **Generische `QComboBox` min-height 32px** — `assets/themes/base/base.qss`; Chat `modelCombo` ohne Python-Mindesthöhe.  
- **Workbench-Listenzeilen** (`#workbenchPaletteList`, `#workbenchNodeLibrary`) — min-height in `workbench.qss`.  
- **Toolbar icon-size** (aktuell noch Literal in `workbench.qss`) — Owner QSS, Tokenisierung Folgeschritt.

## 5. Fälle mit Python-Owner

- **Chat `QTextEdit`** min/max 60–120, **Send/Prompt**-Zeilenhöhen — `input_panel.py` + `design_metrics`.  
- **Chat max-width Spalte** — `CHAT_CONTENT_MAX_WIDTH_PX` (+ Legacy-QSS interpoliert).  
- **Panel-/Dialog-Padding** — `layout_constants` / `apply_*`.  
- **Header-Margins** — `apply_header_profile_margins`.  
- **Sidebar** feste quadratische Größen — jetzt über **benannte Metriken** (`PANEL_HEADER_HEIGHT_PX`, `CHAT_PRIMARY_SEND_*`, `INPUT_MD`, `ICON_LG+SPACE_XS`), Owner bleibt Python für Legacy-Pfad bis QSS vereinheitlicht.

## 6. Entfernte / ersetzte Magic Numbers (Auszug)

- `input_panel.py`: `_model_combo.setMinimumHeight(dm.INPUT_MD_HEIGHT_PX)` entfernt.  
- `sidebar_widget.py`: 44, 44×44, 40, 40×40, 34, 34×34, 28×28 → Ausdrücke aus `design_metrics`.

## 7. Bewusst verbleibende Doppelquellen / Hybride

- **Legacy `#newChatBtn` / `#searchEdit`:** weiterhin QSS in `styles.py` **und** Python-Mindestmaße (Sidebar) — weniger Literale, aber zwei Schichten.  
- **`chat_message_widget.py`:** Bubble-Styles weiterhin per Python-String.  
- **Zahlreiche Empty-State-Labels:** `padding: 24px` in Inline-Stylesheets (Guard listet sie).  
- **`base.qss`:** `min-height: 32px` / Scrollbar-`48px` noch ohne `{{size_*}}`-Token.

## 8. Teststatus

- `tests/unit/gui/test_qss_python_ownership_rules.py` — Docs vorhanden, `input_panel` ohne `_model_combo.setMinimumHeight`.  
- `tests/unit/gui/test_layout_double_source_cleanup.py` — ChatInputPanel, ConversationView, PanelHeader; Sidebar per **Quelltext** (kein `legacy`-Package-Import wegen optional `qasync`).  
- `tests/tools/test_layout_double_source_guard.py` — keine Combo-Hints in `input_panel`, `main()` exit 0, `--strict` bei synthetischen Hints exit 1.  
- **Hinweis:** `layout_double_source_guard.py` ohne `--strict` liefert weiterhin viele **inline_stylesheet**-Treffer — erwartet, kein CI-Fail ohne explizite Policy.

## 9. Restrisiken

- Chat-Combo auf einem Build **ohne** `base.qss`-Regel könnte optisch niedriger wirken (nicht der Workbench-Standardpfad).  
- Sidebar-Metrik-Tausch (44→40) leichte visuelle Verschiebung gegenüber altem Literal.

## 10. Empfohlene nächste Schritte

1. Inline-Empty-State-Styles auf **ThemeTokens** oder `#emptyState*` in QSS migrieren.  
2. `workbenchToolbar` **icon-size** als Token.  
3. `base.qss` **QComboBox min-height** als `{{control_height_md}}` o. ä.  
4. CI-Job optional: `python tools/layout_double_source_guard.py --strict` nur für Allowlist-Pfade oder nach Reduktion der Treffer.

---

## Zusatzfragen

### A. Welche 10 Doppelquellen wurden endgültig beseitigt?

1. Chat `modelCombo`: Python `setMinimumHeight(32)` vs. QSS `min-height: 32` — **Python-Arm entfernt**.  
2–4. Sidebar `newChatBtn` / `saveChatBtn` / `searchBtn` / `searchEdit`: freie Literale — **auf Metriken gemappt** (keine neuen Konstanten).  
5–7. Sidebar Projekt-Icon-Buttons 28px — **ICON_LG + SPACE_XS** (eine Formel).  
8. Projekt-Suche Button/Field 34 — **INPUT_MD** für Quadrat/Feld.  
9–10. **Dokumentierte** vorherige Fälle: Chat-Container max-width (früherer Schritt), Composer-Breite — weiterhin nur Metrik-Quelle.

*(„10“ im Sinne von dokumentierten, adressierten Konfliktzeilen; nicht alle waren vorher harte Widersprüche.)*

### B. Welche 10 Restfälle bleiben offen?

1. Legacy `#newChatBtn` QSS-Padding vs. Python `PANEL_HEADER_HEIGHT_PX`.  
2. `chat_message_widget` Bubble-QSS in Python.  
3. `settings_dialog` `setFixedWidth(36)` auf Hilfsbutton.  
4–8. Empty-State / CC-Panels Inline-`padding` (Guard-Liste).  
9. `workbench` Toolbar `icon-size: 18px` Literal.  
10. `QScrollBar::handle` min-height 48px in `base.qss` ohne Token.  
*(Weitere siehe Guard-Ausgabe und Audit-Tabelle.)*

### C. Konkurrierende Größen in produktiv wichtigen Widgets?

**Reduziert** für Chat-Combo und Sidebar-Metriken; **verbleibend** vor allem **Hybrid Legacy-QSS + Python** an Sidebar-Spezial-IDs und **Chat Legacy** `#sendButton` vs. Operations-Chat Python — unterschiedliche App-Pfade, dokumentiert.

### D. Guard sinnvoll eingeführt?

**Ja**, als **Hinweis-Scanner** (`tools/layout_double_source_guard.py`); **`--strict`** für gezielte CI-Nutzung nach Allowlist-Tuning. Voll-Repo-strict ist aktuell **nicht** empfohlen wegen Inline-Style-Noise.

---

*Siehe auch:* [QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md](./QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md), [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md).
