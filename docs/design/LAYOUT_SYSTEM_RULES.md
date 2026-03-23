# Kanonische Layout-Regeln (Zielmodell)

**Kontext:** Desktop-Workbench — ruhig, kompakt, produktiv.  
**Bezug:** `app/gui/theme/design_metrics.py`, `docs/design/DESIGN_TOKEN_DEFAULTS.md`, `app/gui/shared/layout_constants.py` (soll langfristig an Metriken andocken).

**Code-Hooks (Pilot):** `apply_dialog_scroll_content_layout`, `apply_dialog_button_bar_layout`, `apply_form_layout_policy`, `apply_card_inner_layout` — alle in `layout_constants.py`, Zahlen aus `design_metrics`.

Alle Werte in **px**, Raster **4px**; Ausnahmen explizit benennen.

---

## 1. Panel- und Karten-Padding

| Regel | Wert | Anwendung |
|-------|------|-----------|
| **Standard-Panel-Padding** | **20** | Haupt-Content-Spalte (entspricht `PANEL_PADDING` / `space.panel.padding`) |
| **Standard-Card-Padding** | **16** | Eingebettete Karten, CC-Innenpanels (`space.card.padding`) |
| **Kompaktes Panel** | **12** | Tool-Spalten, sekundäre Inspector-Bereiche |
| **Ultra-kompakt** | **8** | Workflow-Editor-Zellen, dichte Listen-Host |

**Verboten:** neue willkürliche Werte **14** oder **10** als Panel-Rand ohne Ausnahme-Eintrag.

---

## 2. Dialog-Padding

| Regel | Wert |
|-------|------|
| **Standard-Dialog-Innen** | **24** (`space.dialog.padding`) |
| **Kompakter Dialog** | **20** |
| **Button-Leiste** | horizontal **24**, vertikal **0** — bündig mit Form-Breite |

---

## 3. Form-Abstände

| Regel | Wert |
|-------|------|
| **Form-Zeilen-Abstand (vertical)** | **12** (`space.form.row_gap`) |
| **Label↔Feld (horizontal)** | **8** mindestens (`space.form.label_gap`) |
| **QFormLayout row spacing** | **12** (ersetzt ad-hoc 6/14) |

**Alignment:** Label-Spalte rechtsbündig oder feste Mindestbreite **120px** für Haupt-Desktop.

**Implementierte Policy (Referenz):** `apply_form_layout_policy` — `verticalSpacing = 12`, `horizontalSpacing = 8`, `AlignRight | AlignVCenter` für Labels, `AllNonFixedFieldsGrow`. Mindestlabelbreite: Konstante `FORM_LABEL_MIN_WIDTH_DESKTOP_PX` in `design_metrics` (manuell an QLabel bei Bedarf).

---

## 4. Toolbar- und Inline-Gaps

| Regel | Wert |
|-------|------|
| **Toolbar-Element-Abstand** | **12** (`space.toolbar.gap`) |
| **Inline-Gap (Icon+Text)** | **8** (`space.inline.gap.sm`) bzw. **12** für lockere Gruppen |

---

## 5. Sidebar / Listen

| Regel | Wert |
|-------|------|
| **Sidebar-Item vertikaler Abstand (layout spacing)** | **4** (`space.sidebar.item_gap`) oder **0** wenn QSS-Margin übernimmt — **eine Strategie pro Liste** |
| **Listen-Zeilenhöhe (min)** | **32px** Standard; **28px** nur „dense explorer“ |
| **Nav-Item Touch-Padding (QSS)** | beibehalten **12×16** bis Token-Migration |

---

## 6. Button-Höhen

| Regel | Wert |
|-------|------|
| **Standard-Button / Input-Höhe** | **32px** |
| **Prominente Aktion (z. B. Send)** | **36–40px** max |
| **Legacy 48px** | abzubauen außer UX-Studie sagt nötig |

---

## 7. Input-Höhen

| Regel | Wert |
|-------|------|
| **LineEdit / Combo** | **32px** min (QSS + Python konsistent) |
| **Mehrzeilig Composer** | min **60**, max **120** — als Named Constants |

---

## 8. Tab-Höhe

| Regel | Ziel |
|-------|------|
| **Document Tab** | visuelle Höhe **34–36px** aus Padding `8×16` ± Border |
| **Bottom Panel Tab** | gleiche Familie wie Shell-Tabs (QSS `#bottomPanelTabs`) |

---

## 9. Header-Abstände

| Profil | Margins (L,T,R,B) | Verwendung |
|--------|-------------------|------------|
| **header.standard** | **12, 10, 12, 10** | PanelHeader, Chat-Nav-Header |
| **header.compact** | **12, 8, 12, 8** | Workflow-Leisten |
| **header.ultracompact** | **8, 6, 8, 6** | Workbench Context Action Bar |

---

## 10. Icon- und Text-Abstände

| Regel | Wert |
|-------|------|
| **Toolbar-Icon-Größe** | **20px** (Harmonisierung mit Design-Token-Defaults) |
| **Nav-Icon** | **16px** |
| **Abstand Icon→Text in Listen** | durch **einheitliches Item-Padding** (12×16), nicht extra Spacer |

---

## 11. Sektionstrennungen

| Mittel | Wann |
|--------|------|
| **16px vertikaler Zwischenraum** | Zwischen logischen Blöcken im selben Panel |
| **24px** | Zwischen Hauptsektionen im Dialog |
| **QFrame HLine / border-top** | Nur wenn inhaltlich „neues Thema“ — sparsam |
| **SectionCard / #settingsPanel** | Für fachliche Gruppierung mit Titel |

---

## 12. Chat (Operations + Legacy)

Zentrale Policy: [CHAT_LAYOUT_POLICY.md](./CHAT_LAYOUT_POLICY.md). Kurzfassung:

| Regel | Wert |
|-------|------|
| **Content-Spalte max.** | **800px** (`CHAT_CONTENT_MAX_WIDTH_PX`), elastisch darunter |
| **Legacy-Bubble max.** | **720px** (`CHAT_BUBBLE_MAX_WIDTH_PX`) |
| **Workspace-Verlauf-Padding** | **20px** (`PANEL_PADDING_PX`), Bubble-Abstand **16px** |
| **Send (prominent)** | **40px**; sekundäre Chat-Buttons **32px** |

---

## 13. Workbench-spezifisch

| Regel | Wert |
|-------|------|
| **Inspector inner margin** | **12px** (Anhebung von 10 auf 12 für Shell-Parität) |
| **Explorer Tree** | randlos; Zeilenhöhe **32** nach Harmonisierung |
| **Canvas äußerer Rand** | **24px** beibehalten oder auf **20** angleichen an Shell-Workspace-Soll |

---

## 14. Shell-Docks (unverändert bis Architektur-Entscheid)

| Konstante | Wert |
|-----------|------|
| Nav default width | **240** |
| Inspector default | **280** |
| Bottom height | **200** |

---

## 15. QSS ↔ Python (Doppelquellen)

**Ownership:** [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md)  
**Audit:** [QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md](./QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md)  
**Kanonische Fälle:** [QSS_PYTHON_CANONICAL_CASES.md](./QSS_PYTHON_CANONICAL_CASES.md)  
**Cleanup-Bericht:** [QSS_PYTHON_DOUBLE_SOURCE_CLEANUP_REPORT.md](./QSS_PYTHON_DOUBLE_SOURCE_CLEANUP_REPORT.md)  
**Heuristik:** `tools/layout_double_source_guard.py` (optional `--strict`, `--include-qss`)

---

## 16. UI Governance (übergeordnet)

Neue Screens, Panels, Dialoge: [UI_GOVERNANCE_RULES.md](./UI_GOVERNANCE_RULES.md) · PR-Checks: [UI_REVIEW_CHECKLIST.md](./UI_REVIEW_CHECKLIST.md) · Kurz: [UI_GOVERNANCE_SHORT.md](./UI_GOVERNANCE_SHORT.md)

---

*Migration:* [LAYOUT_SPACING_MIGRATION_PLAN.md](./LAYOUT_SPACING_MIGRATION_PLAN.md)
