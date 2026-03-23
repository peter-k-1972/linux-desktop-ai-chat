# Theme-Zielmodell — verbindliche technische Spezifikation

**Status:** Zielzustand (Soll), abgeleitet aus [docs/audits/THEME_COLOR_AUDIT.md](../audits/THEME_COLOR_AUDIT.md).  
**Gültigkeit:** Alle neuen und migrierten GUI-Implementierungen müssen diesem Modell folgen.  
**Fortschritt / Ist:** siehe [THEME_MIGRATION_FINAL_REPORT.md](../../THEME_MIGRATION_FINAL_REPORT.md) (Repo-Root) und [docs/qa/THEME_QA_REPORT.md](../qa/THEME_QA_REPORT.md).

---

## 1. Executive Summary

### 1.1 Warum das bisherige Modell nicht ausreicht

Der Audit dokumentiert:

- **Zwei parallele Systeme:** `ThemeManager` mit `theme_id` (`light_default`, `dark_default`, `workbench`) und token-substituiertem QSS vs. `app/resources/styles.py` mit `get_stylesheet` / `get_theme_colors` und nur **`light` | `dark`** (siehe Audit §2.2, §5.1).
- **Kollabierung von Themes:** `theme_id_to_legacy_light_dark` mappt `dark_default` und `workbench` auf denselben Legacy-Bucket `"dark"` — Inline-Styles können Workbench nicht von Dark unterscheiden, während globales QSS schon workbench-spezifisch ist (Audit §2.3, §5.2).
- **Massenhafte Direktfarben:** ~1199 Hex-Vorkommen in `app/**/*.py`, ~722 `setStyleSheet`-Aufrufe; viele Panels sind **light-assumptiv** (`white`, `#e2e8f0`) und brechen Dark/Workbench (Audit §1, §5.3).
- **Markdown/HTML ohne Theme:** `markdown_renderer.py` nutzt feste `rgba(...)` — nicht an aktuelle Tokens gebunden (Audit §3.7, §5.4).
- **Zweite Farbdefinition:** `palette_resolve._domain_monitoring_qa` ergänzt Hex neben `SemanticPalette` (Audit §3.1, §5.9).
- **Pfad-Drift:** Aktiver Loader liest nur `assets/themes/base/*.qss`; Kopien unter `app/gui/themes/base/` weichen bei `shell.qss` / `workbench.qss` ab (Audit §2.6).

Damit ist **vollständige zentrale Steuerung**, **Konsistenz über alle Themes** und **Erweiterbarkeit** (viertes Theme, Farbprofile) **nicht** garantiert.

### 1.2 Leitprinzipien (verbindlich)

1. **Eine Laufzeit-Wahrheit:** Sichtbare Farben stammen aus **einem** aufgelösten Token-Dictionary pro aktivem `theme_id` (und optionalem Farbprofil).
2. **Semantik vor Literal:** Komponenten und Renderer referenzieren **semantische Tokens**, keine freien Hex-/RGB-Werte.
3. **Kein paralleles Farbsystem in QSS:** Produktives QSS enthält **keine** Roh-Hex/RGB; nur Platzhalter `{{flat_token_key}}`, die aus derselben Auflösung gespeist werden wie Python.
4. **Theme-ID ist vollständig:** Jedes registrierte Theme (`light_default`, `dark_default`, `workbench`, künftige IDs) liefert **vollständige** Token-Sets — kein stilles Umbiegen auf einen anderen Bucket für Styling.
5. **Ausnahmen sind dokumentiert und minimal:** Abweichungen nur in einer **Allowlist** (Datei + Begründung + Review-Regel).

### 1.3 Architekturentscheidung (nicht verhandelbar)

**Kanonical stack:**

```
ThemePackage (theme_id + optional color_profile_id)
  → SemanticColorModel (alle semantischen Rollen als Daten)
  → ResolvedTokenMap (flache String-Werte, inkl. abgeleiteter Komponenten-Tokens)
  → ├─ QSS (Substitution {{key}})
  → └─ Python (QColor.fromString, Stylesheet-Strings, Rich-Text-HTML, Painter)
```

- **Farbprofil** (z. B. „Kontrast+“, „Farbschwäche“, OEM-Branding) ist eine **optionale Schicht**, die **denselben Token-Namen** mit anderen Werten befüllt oder nur Untergruppen überschreibt — **keine** zweite Namenskonvention.

Legacy: `get_theme_colors` und `get_stylesheet` werden **abgeschafft** oder zu dünnen **Deprecated-Shims** reduziert, die **ausschließlich** aus `ResolvedTokenMap` lesen, bis Entfernung (siehe [THEME_MIGRATION_PLAN.md](./THEME_MIGRATION_PLAN.md)).

---

## 2. Architektur des Zielsystems

### 2.1 Theme (`theme_id`)

- Identifiziert ein **vollständiges** visuelles Paket: Shell, Workbench, Standard-Widgets, Domain-spezifische Mindesttokens (Monitoring, QA-Nav, Chat).
- Registrierung bleibt zentral (heute: `ThemeRegistry`); Erweiterung um weitere built-in oder geladene Themes **ohne** Codepfad-Branching nach `light`/`dark` allein.

### 2.2 Farbprofil (`color_profile_id`, optional)

- **Kein** Ersatz für `theme_id`; es modifiziert **Werte**, nicht **Struktur**.
- Anwendungsfälle: höherer Kontrast, reduzierte Sättigung, High-Visibility-Statusfarben.
- Auflösung: `ResolvedTokenMap = base_theme_tokens ⊕ profile_overrides` (letzte Wins nach definierter Priorität).

### 2.3 Semantische Tokens

- Benannte **Bedeutung** („Text primär“, „Fehler“, „Codeblock-Hintergrund“).
- Werden in **Python-Daten** (z. B. erweitertes `SemanticPalette` oder generiertes Schema) **authoriert** — nicht in Widget-Code zerstreut.
- Kontrast-relevante Paare werden in CI gegen Regeln geprüft ([THEME_CONTRAST_RULES.md](./THEME_CONTRAST_RULES.md)).

### 2.4 Strukturelle Tokens

- Nicht-farbige Designwerte: Abstände, Radien, Schriftgrößen/-gewichte (bereits teils `ThemeTokens`).
- **Regel:** Struktur und Farbe **trennen** in der Spezifikation; Kombination nur in QSS oder Helpern.

### 2.5 Komponentenspezifische Ableitungen

- Tokens wie `color.button.primary.bg` sind **abgeleitet** aus Basis+Interaktion+Accent, dürfen aber **explizit** pro Theme überschrieben werden, wenn die Ableitung visuell unzureichend ist.
- **Default:** Ableitung aus Regeln dokumentiert in [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md) (`Ableitbar: ja`).

### 2.6 Laufzeit-Anwendung (PySide6)

1. Beim Theme-Wechsel: `ThemeManager.set_theme(theme_id, color_profile_id=None)` berechnet `ResolvedTokenMap`.
2. `load_stylesheet`: ersetzt alle `{{flat_key}}` in `assets/themes/base/*.qss`.
3. `QApplication.setStyleSheet(combined)`.
4. Widgets, die dynamische Strings brauchen, rufen **`theme_tokens()`** (oder `get_theme_manager().get_tokens()`) auf — **keine** parallelen Dicts.
5. `QColor`-Nutzung: `QColor(tokens["color_chart_series_1"])` o. ä. — Literale nur in Token-Quelldateien und Tests (erwartete Werte).

---

## 3. Verbindliche Ebenen des Theme-Systems

Die folgenden Ebenen **müssen** durch benannte Tokens aus [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md) abgedeckt sein. fehlende Tokens = Spezifikationslücke, keine Implementierung ohne Ergänzung der Spec.

### A. Foundation / Base

| Ebene | Token-Zweck (logisch) |
|-------|------------------------|
| App-Hintergrund | Gesamte Fläche hinter Fenstern / Workspaces |
| Fenster / Hauptfläche | `QMainWindow`, zentrale Hosts |
| Panel-Hintergrund | Seitenleisten, Inspectors, feste Bereiche |
| Elevated surface | Karten, erhöhte Flächen innerhalb eines Panels |
| Overlay surface | Modale Überlagerungen, Popover-Hintergrund (ggf. mit Transparenz über separate Opacity-Tokens oder feste Mischfarben als Tokens) |

### B. Text / Foreground

Primär, sekundär, muted, disabled, inverse (auf dunklem Accent), **Link** (explizit; nicht mit Accent gleichsetzen, außer dokumentiert identisch).

### C. Borders / Separation

Default, subtle, strong, **focus border** (sichtbare Fokusbegrenzung — kann mit `focus_ring` kombiniert werden).

### D. Interaction

Hover, pressed, selected, active (z. B. gedrückter Toggle), **focus ring** (Outline), **selection bg/fg** (Textauswahl, nicht nur Listenauswahl).

### E. State / Semantic

success, warning, error/danger, info, accent / primary action (kann mit Button-Primär zusammenfallen, muss aber adressierbar bleiben).

### F. Content-Spezialisierung

- Markdown: Body, Überschrift, Link, Zitat, Inline-Code, Codeblock FG/BG.
- Syntax (optional gruppiert): keyword, string, comment, number, function — mindestens als **Konsolen/Markdown-Code**-Nähe; Umsetzung kann phasenweise erfolgen.
- Tabelle: Header BG/FG, Zelle, alternierende Zeile, Gitter, Selection.
- Badges / Status-Chips: success, warning, error, info (je bg+fg).
- Charts: Hintergrund, Achse, Gitter, mindestens **N Serienfarben** + „other“.
- Chat: user / assistant / system Blasen (BG mindestens; FG wenn von Body abweicht).

---

## 4. Theme-Prinzipien (Durchsetzung)

| # | Prinzip |
|---|---------|
| P1 | **Keine harten Farben in Produktiv-Widget-Code** — Ausnahme nur Allowlist (siehe §6). |
| P2 | **Keine Semantik ohne Token** — jede sichtbare Farbe hat einen Namen in der Spec. |
| P3 | **Kein paralleles QSS-Farbsystem** — keine Hex/RGB in `assets/themes/base/*.qss`. |
| P4 | **Keine lokale Sonderlogik** ohne Eintrag in `docs/design/THEME_COMPONENT_MAPPING.md` oder Migrationsticket mit Architektur-Freigabe. |
| P5 | **Rückführbarkeit** — Code-Review: „Welcher Token?“ muss in einer Zeile beantwortbar sein. |

---

## 5. Verantwortlichkeiten

| Artefakt | Inhalt | Besitzer (fachlich) |
|----------|--------|---------------------|
| **Theme-/Palette-Dateien** (Python) | Semantische + abgeleitete Werte pro `theme_id` / Profil | Design-System / Tech-Lead |
| **QSS** (`assets/themes/base/`) | Selektoren, Pseudo-States, ObjectNames, **nur** `{{tokens}}` | Design-System + UI-Implementierung |
| **Python-Widgets** | Layout, Logik, **keine** Farbliterale; ggf. `setProperty` + QSS | Feature-Teams |
| **Renderer/Helpers** | Markdown-HTML, Konsolen-Format, Painter-Palette aus `ResolvedTokenMap` | Plattform-GUI |
| **Tests** | Kontrast-Snapshots, Token-Vollständigkeit, Regression auf `theme_id` | QA / CI |

**Ausnahmen zulässig nur:**

- Generierte Assets (externe Tools), die nicht zur Laufzeit editiert werden.
- Drittanbieter-Widgets ohne QSS-Hook — dann **Umrandungs-Container** mit Token-Hintergrund oder Fork/Wrapper, dokumentiert.

---

## 6. Verbotene Muster

| Verbot | Beispiel aus Audit |
|--------|---------------------|
| Direkte Hex/RGB in Domain-GUI | `_cc_panel_style` mit `white` / `#e2e8f0` (Audit §3.5) |
| `QColor("#…")` in Standard-Widgets | `workflow_node_item.py`, `workflow_edge_item.py` (§3.6) |
| Ad-hoc `setStyleSheet` mit Farbwerten | Hunderte Vorkommen (§1 Metrik) |
| QSS mit undokumentierten Sonderfarben | Legacy-Dateien `app/resources/*.qss` (§2.6) |
| Überschreiben zentraler Token-QSS ohne Token | Widget-lokale Styles, die Basis konterkarieren (§5.10) |
| Theme-Erkennung nur über `light`/`dark` String für UI-Farben | `get_theme_colors` / `theme_id_to_legacy_light_dark` (§2.3) |

**Allowlist-Pflege:** Datei `docs/design/THEME_EXCEPTIONS.md` (anzulegen bei erster Ausnahme) mit: Pfad, Zeile/Patch-Referenz, Begründung, Auslauf-Datum oder „Drittanbieter permanent“.

---

## 7. Bezug Audit → Ziel

| Audit-Issue | Zielmaßnahme |
|-------------|--------------|
| Zwei Systeme | Ein `ResolvedTokenMap`; Legacy entfernen (Migration) |
| Workbench = dark in Legacy | Volle `theme_id`-Treue in allen APIs |
| Light-only Panels | Tokens `color.bg.surface` etc. |
| Markdown rgba | Tokens aus Spec, Renderer injiziert Werte |
| Doppel-QSS-Pfad | **Single source:** `assets/themes/base/`; Duplikat unter `app/gui/themes/base/` entfernen oder Build-Symlink |
| palette_resolve vs SemanticPalette | Monitoring/QA-Rollen in Semantic-Modell integrieren oder Profile-Overrides |
| Icon-Fallback-Hex | Fallback = letzter Token-Layer, nicht hardcoded in `IconManager` |

---

## 8. Offene Punkte (objektiv spezifikationsbedürftig)

- **Overlay-Transparenz:** Qt/QSS limitiert — ob Overlay als **solide** `color.bg.overlay` Token oder plattformspezifisch; Entscheidung bei Implementierung Phase 1, dokumentiert in Token-Spec.
- **Syntax-Highlighting-Umfang:** Mindestumfang in Spec festgelegt; volle Pygments-Zuordnung optional später.
