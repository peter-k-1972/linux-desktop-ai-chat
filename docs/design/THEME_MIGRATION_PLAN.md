# Theme-Migrationsplan — Ist → Soll

**Zielmodell:** [THEME_TARGET_MODEL.md](./THEME_TARGET_MODEL.md)  
**Token-Spec:** [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md)  
**Audit:** [docs/audits/THEME_COLOR_AUDIT.md](../audits/THEME_COLOR_AUDIT.md)  
**Statusbericht (Ist vs. Soll):** [THEME_MIGRATION_FINAL_REPORT.md](../../THEME_MIGRATION_FINAL_REPORT.md) · **QA:** [docs/qa/THEME_QA_REPORT.md](../qa/THEME_QA_REPORT.md)

---

## 1. Migrationsstrategie

### 1.1 Ansatz

- **Kein Big Bang:** Die App bleibt nach jedem abgeschlossenen Teil-PR nutzbar.
- **Single write path:** Sobald Phase 2 beginnt, dürfen neue Farben **nur** noch über Token-Resolver in die UI — keine neuen Hex-Literale in `app/gui/domains/**` und `app/gui/inspector/**` (Lint/Review-Regel).
- **Rückfallkontrolle:**
  - Feature-Flags sind **nicht** vorgesehen; stattdessen **Alias-Layer**: alte QSS-Platzhalter (`color_text`) werden aus neuen Tokens gespeist, bis QSS umgestellt ist.
  - Bei Regression: Revert des Teil-PRs; keine halbfertigen Token-Namen in `main`.
- **Tests:** Bestehende `tests/regression/test_settings_theme_tokens.py` erweitern; pro Phase Abnahme-Tests (unten).

### 1.2 Reihenfolge (Kritikalität)

1. Globale Theme-Quellen und Resolver (ohne das scheitern alle Consumers).  
2. QSS-Basis + Entfernung physischer Duplikate.  
3. Hochfrequente Standard-Patterns (Control Center, Inspector-Helper).  
4. Chat + Hilfe (Legacy `get_theme_colors`).  
5. Markdown/Rich-Text.  
6. Canvas/Charts/Indicators.  
7. Kontrast-QA + neues Theme/Farbprofil.  
8. Legacy-Entfernung und harte Deprecation.

---

## 2. Phasenmodell

### Phase 1 — Zentrale Token-Infrastruktur

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Ein Resolver liefert `ResolvedTokenMap` für `(theme_id, color_profile_id?)`; alle Keys aus [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md) mit definierten Defaults oder Theme-Overrides. |
| **Dateien / Subsysteme** | `app/gui/themes/` (`tokens.py`, neues Modul z. B. `resolved_tokens.py` oder Erweiterung `definition.py`); `manager.py`; Tests unter `tests/unit/` + `tests/regression/`. |
| **Risiken** | Performance (bei jedem Paint irrelevant — nur bei Theme-Wechsel); Key-Typos → CI-Check „alle Spec-Tokens vorhanden“. |
| **Tests / QA** | Unit: jeder `theme_id` liefert vollständige Map; fehlender Token = Fail. Snapshot optional. |
| **Abnahme** | `get_theme_manager().get_tokens()` enthält **alle** Spec-Keys; alte Keys zusätzlich als Alias bis Phase 3 Ende. |

### Phase 2 — Bestehende Theme-Quellen auf Token mappen

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | `SemanticPalette` / `builtin_semantic_profiles` / ehem. `palette_resolve._domain_monitoring_qa` liefern **nur noch** Werte für kanonische Tokens (keine zweite Hex-Tabelle ohne Schema). |
| **Dateien** | `semantic_palette.py` (Felder erweitern falls nötig), `builtin_semantic_profiles.py`, `palette_resolve.py`, `merge_semantic_aliases_for_qss`. |
| **Risiken** | Visuelle Verschiebung bei 1:1-Mapping-Fehlern — Abnahme mit Screenshot-Diff optional oder manuell pro Theme. |
| **Tests** | `test_semantic_theme_profiles`, Kontrast-Paare für light/dark/workbench. |
| **Abnahme** | Kein freistehendes Hex-Dict außerhalb der Profile-Dateien. |

### Phase 3 — QSS vereinheitlichen

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | `assets/themes/base/*.qss` nutzt durchgängig neue `{{color_*}}` Keys; Aliase für Legacy-Platzhalter entfernen, sobald Substitution vollständig. |
| **Dateien** | `assets/themes/base/base.qss`, `shell.qss`, `workbench.qss`; `loader.py`. |
| **Risiken** | Versehentliche Bearbeitung von `app/gui/themes/base/` — **Entscheidung:** Duplikat-Ordner in Phase 3 löschen oder durch README „read-only mirror“ ersetzen. |
| **Tests** | Architektur-Test: Loader-Output enthält keine `#rrggbb` (Regex). |
| **Abnahme** | Ein physischer QSS-Pfad; keine Roh-Hex in base-QSS. |

### Phase 4 — Widget-Hardcodings entfernen (Batch 1: Muster)

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Control-Center `_cc_panel_style` → Token-Strings; gemeinsamer Helper `theme_style.panel_card()` o. ä. |
| **Dateien** | `providers_panels.py`, `models_panels.py`, `data_stores_panels.py`, `tools_panels.py`, `model_quota_policy_panel.py`, `local_assets_panel.py` (Audit §3.5). |
| **Risiken** | Merge-Konflikte in großen Dateien — PRs nach Modul splitten. |
| **Tests** | Smoke: Control Center unter allen `theme_id`. |
| **Abnahme** | Kein `white` / fixes Tailwind-Hex in diesen Modulen. |

### Phase 5 — Markdown / Code / Renderer

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | `markdown_renderer.py` bekommt Token-Injection (Kontext: aktuelles Theme) statt fester `rgba`. |
| **Dateien** | `app/gui/shared/markdown/markdown_renderer.py`, ggf. `markdown_ui.py`; `help_window.py` (Inline-HTML `#555`). |
| **Risiken** | HTML-Injection — nur escapte Werte einfügen, keine Roh-Userstrings in `style=`. |
| **Tests** | Golden-File HTML mit ersetzten Farben pro Theme; mindestens light + dark. |
| **Abnahme** | Kein `rgba(` Literal im Renderer außer aus Token-berechneter String-Factory. |

### Phase 6 — Charts / Indicators / SVG / Icon-Farben

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | `workflow_node_item.py`, `workflow_edge_item.py`, `ai_canvas_scene.py`, `canvas_tabs.py`, `agent_performance_tab.py` lesen `QColor` aus Token-Map. |
| **Dateien** | genannte + `icons/manager.py` (Fallback-Hex entfernen). |
| **Risiken** | QtCharts Theme API — ggf. manuelles Setzen pro Serie aus Tokens. |
| **Tests** | Unit: Farbwerte für `theme_id` entsprechen Map-Keys. |
| **Abnahme** | Keine `#` Literale in diesen Modulen (außer Tests). |

### Phase 7 — Kontrastprüfung und Theme-QA

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Automatisierte Paarprüfungen laut [THEME_CONTRAST_RULES.md](./THEME_CONTRAST_RULES.md); manuelle Pass über kritische Screens (Audit §4). |
| **Dateien** | `app/gui/themes/contrast.py` erweitern; neue `tests/unit/test_theme_contrast_*.py`. |
| **Risiken** | Zu strenge Regeln blockieren kreative Dark-Themes — Regeln pro Theme anpassbar dokumentieren. |
| **Tests** | CI gate auf definierte Paare. |
| **Abnahme** | Kontrast-Report grün für `light_default`, `dark_default`, `workbench`. |

### Phase 8 — Neues Theme + Farbprofile + Legacy-Entfernung

| Aspekt | Inhalt |
|--------|--------|
| **Ziel** | Viertes built-in `theme_id` **oder** erstes `color_profile_id` produktiv; vollständige Token-Sets. Entfernen: `get_theme_colors`, `get_stylesheet` (oder nur Shims), `theme_id_to_legacy_light_dark` für Styling-Zwecke, unbenutzte QSS (`app/resources/*.qss`, `assets/themes/legacy/` falls weiter nutzlos). |
| **Dateien** | `registry.py`, `settings.py`, alle verbliebenen Consumer von `app/resources/styles.py`, `app/main.py` (Legacy-Pfad). |
| **Risiken** | Externe Nutzer von `main.py` — Release-Note / Deprecation eine Version vorher. |
| **Tests** | Vollregression GUI-Smoke; keine Importe von `get_theme_colors` (Grep-Test). |
| **Abnahme** | Audit-Metrik: Hex-Literale in `app/gui/**` unter definierter Schwelle (nur Token-Quellen + Allowlist). |

---

## 3. Migrationsreihenfolge nach Subsystem (Referenz)

| Priorität | Subsystem | Begründung (Audit) |
|-----------|-----------|---------------------|
| P0 | `ThemeManager` + Resolver + QSS-Pfad | Fundament |
| P0 | `palette_resolve` / Semantic merge | Doppelte Definition beseitigen |
| P1 | Command Center + `get_theme_colors` Consumer | Breite Kopplung |
| P1 | Control Center Panels | Light-only Bruch |
| P2 | Inspector-Cluster | Wiederholtes Muster — ein Helper |
| P2 | Chat (`chat_message_widget`, Header, Side) | Nutzer sichtbar |
| P3 | Hilfe / Tour | Legacy colors |
| P3 | `doc_search_panel` | Hard light break |
| P4 | Knowledge / Prompt / QA Panels | Hohe Hex-Dichte |
| P4 | Runtime Debug / Monitoring | Domain-Tokens |
| P5 | Workflow-Canvas, Charts, Tabs | Painter |
| P6 | Legacy `main.py`, `styles.py`, tote QSS | Aufräumen |

---

## 4. Explizite Non-Goals

- **Kein visuelles Redesign** „weil schöner“ — Farben bleiben möglichst werte-identisch zum Ist, bis Token-Migration steht; anschließend gezielte Anpassung nur mit Kontrast-Check.
- **Kein Layout-Refactoring** in derselben PR-Serie (Margins, Umstrukturierung) — trennen, um Diff lesbar zu halten.
- **Keine funktionalen GUI-Änderungen** (keine neuen Buttons/Flows) innerhalb der Theme-Migrations-PRs, außer Bugfix der direkt durch falschen Kontrast verursacht wurde.

---

## 5. Review-Checkliste (pro PR)

- [ ] Jede neue Farbe: Token-Name aus Spec oder Spec-PR gemerged.  
- [ ] Kein `get_theme_colors` in neuem Code.  
- [ ] Kein Hex in `app/gui/domains` / `inspector` (außer Allowlist).  
- [ ] QSS-Änderungen nur unter `assets/themes/base/`.  
- [ ] Tests aktualisiert oder neu für Theme-Wechsel.

---

## 6. Erfolgskriterien (Gesamtprojekt)

1. Ein `theme_id` + optionales Profil steuert **alle** genannten UI-Bereiche aus dem Audit ohne zweites Farbsystem.  
2. `workbench` und `dark_default` sind **visuell und technisch** unterscheidbar (kein Legacy-Bucket für Inline-Styles).  
3. Markdown-Rendering ist in hell/dunkel/workbench **lesbar** (Kontrast-Tests grün).  
4. Metrik: `setStyleSheet` mit eingebetteten Farbliteralen < Schwelle (Projekt setzt Ziel z. B. < 50 nach Migration, exakt im letzten Phase-8 PR festlegen).
