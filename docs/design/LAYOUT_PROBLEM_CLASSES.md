# Layout-Problemklassen (Taxonomie)

Jede Klasse: **Symptom** → **typische Ursache** → **Fundort-Beispiele** → **Sanierung**.

---

## P1 — Padding-Vielfalt (Magic Numbers)

**Symptom:** Gleiche Rolle (äußerer Panel-Rand) mit 8, 12, 14, 16, 20, 24, 32px.  
**Ursache:** Keine zentrale Konstante / kein Token-Import in Python-Layouts.  
**Beispiele:** `dashboard_screen.py` 32; `providers_panels.py` 16; `project_stats_panel.py` 14; `conversation_view.py` 32/40.  
**Sanierung:** `design_metrics` / `space.panel.padding` etc.; `apply_panel_layout` konsequent nutzen.

---

## P2 — Button-Höhen-Mischbetrieb

**Symptom:** 32px (QSS) vs. 48px (Chat) vs. 44px (Legacy).  
**Ursache:** Feature-spezifische `setFixedHeight` ohne globale Size-Tokens.  
**Beispiele:** `input_panel.py` 48; `base.qss` implizit 32 für Standard-Buttons.  
**Sanierung:** `size.button.md` / `size.button.lg` dokumentieren; Chat auf `lg` max 40 begrenzen.

---

## P3 — Header-Dichte springt

**Symptom:** Panel-Header 10px vertikal vs. Context-Leiste 6px vs. Workflow 8px.  
**Ursache:** Unabhängig gewachsene Komponenten.  
**Beispiele:** `panel_header.py` 12,10; `context_action_bar.py` 8,6; `workflow_header.py` 12,8.  
**Sanierung:** Drei benannte Profile: `header.standard`, `header.compact`, `header.ultracompact`.

---

## P4 — Dialoge zu luftig oder zu eng

**Symptom:** Settings 24+20 spacing wirkt weit; kleine Topic-Dialoge 280px wirkt gequetscht bei langen Labels.  
**Ursache:** Ein Dialog-Layout für alle Kategorien; `QFormLayout` ohne Mindestbreite für Felder.  
**Beispiele:** `settings_dialog.py`; `topic_editor_dialog.py`.  
**Sanierung:** Dialog-Padding-Tokens; minimale Feld-Breiten-Regel.

---

## P5 — Sidebar kompakt, Workspace weit

**Symptom:** Nav 8–12px dicht, CC-Workspace 24px — Kontrast kann **gewollt** sein, wirkt aber **unruhig** beim Wechsel.  
**Ursache:** Keine „Übergangszone“ oder einheitlicher erster Content-Margin.  
**Sanierung:** Workspace äußerer Rand auf **20px** standardisieren (außer Dashboard).

---

## P6 — Form-Layouts uneinheitlich

**Symptom:** Labels springen, unterschiedliche vertikale Abstände (6 vs. 8 vs. 12 vs. 14).  
**Ursache:** Viele `QFormLayout` ohne globale Spacing/Alignment-Policy.  
**Beispiele:** `settings_dialog.py` spacing 14; `editor_panel.py` form 12.  
**Sanierung:** Helper `apply_form_layout(form, density="standard"|"compact")`.

---

## P7 — Card-Struktur unklar

**Symptom:** Manche Inhalte in QSS-`#basePanel`/Settings-Karten, andere nur mit Layout-Margin.  
**Ursache:** Keine verpflichtende „Card vs. Plain“-Regel pro Screen-Typ.  
**Sanierung:** Regelwerk [LAYOUT_SYSTEM_RULES.md](./LAYOUT_SYSTEM_RULES.md) durchsetzen.

---

## P8 — Fehlendes Größenraster

**Symptom:** 6px, 10px, 14px, 28px Spacing.  
**Ursache:** Ad-hoc Feintuning.  
**Sanierung:** 4px-Raster; Ausnahmen in Allowlist.

---

## P9 — Panel-Header visuell uneinheitlich

**Symptom:** Workbench `PanelHeader` vs. Shell-Panel-Titel vs. Chat-Nav-Header — ähnliche Rolle, leicht andere Maße.  
**Ursache:** Kopie mit Anpassung statt einer Komponente.  
**Sanierung:** Wo möglich dieselbe Header-Komponente oder identische Margin-Konstanten.

---

## P10 — QSS und Python konkurrieren

**Symptom:** Control-Höhe in QSS `min-height: 32` aber Python `setFixedHeight(48)`.  
**Ursache:** Zwei Schichten ohne Prioritätsregel.  
**Beispiele:** Chat Input; Combos.  
**Sanierung:** Ownership-Regeln: [QSS_PYTHON_OWNERSHIP_RULES.md](./QSS_PYTHON_OWNERSHIP_RULES.md); Audit: [QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md](./QSS_PYTHON_DOUBLE_SOURCE_AUDIT.md); Guard: `tools/layout_double_source_guard.py`.

---

## P11 — Fixe Content-Breiten (Layout-Bruch)

**Symptom:** Horizontaler Scroll oder abgeschnittene UI bei kleinen Fenstern.  
**Ursache:** `setMinimumWidth(1200)`, `1000` Composer.  
**Beispiele:** `conversation_view.py`, `chat_composer_widget.py`.  
**Sanierung:** `maxWidth` + elastische Mindestbreite; `QScrollArea` nur für echte breite Inhalte.

---

## P12 — Zwei `layout_constants`-Module

**Symptom:** `shared/layout_constants.py` vs. `shell/layout_constants.py` — mentale Last für Entwickler.  
**Ursache:** historische Trennung Shell vs. Shared.  
**Sanierung:** Umbenennung/merge oder klare README-Regel „Dock-Maße nur shell/*“.

---

*Priorisierte Migration:* [LAYOUT_SPACING_MIGRATION_PLAN.md](./LAYOUT_SPACING_MIGRATION_PLAN.md)
