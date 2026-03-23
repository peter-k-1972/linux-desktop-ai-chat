# Kontrast- und Lesbarkeitsregeln (verbindlich, praxisnah)

**Kontext:** Desktop-Qt-App, keine Web-WCAG-Zertifizierungspflicht; Regeln dienen **messbarer** Qualität.  
**Hilfsmittel:** `app/gui/themes/contrast.py` (`contrast_ratio`, `relative_luminance`).  
**Audit:** Unzureichende Markdown-Kontraste auf dunklem UI [THEME_COLOR_AUDIT.md](../audits/THEME_COLOR_AUDIT.md) §4.5, §5.4.

---

## 1. Zielgrößen (WCAG-orientiert, abgeschwächt für UI-Chrome)

| Kategorie | Mindest-Kontrastverhältnis | Gilt für |
|-----------|----------------------------|----------|
| **A — Primärtext** | **4.5 : 1** | `color.fg.primary` auf `color.bg.surface`, `color.bg.app`, `color.bg.panel` |
| **B — Sekundärtext** | **4.5 : 1** | `color.fg.secondary` auf gleichen Flächen wie A (kein bewusstes 3:1 für kleine Schrift in der App) |
| **C — Muted / Caption** | **4.5 : 1** | `color.fg.muted` — *kein* Sonderfall 3:1; Captions müssen lesbar bleiben |
| **D — Disabled** | **kein WCAG-AAA-Zwang**; mindestens **3 : 1** gegenüber zugehörigem disabled-Hintergrund | `color.fg.disabled` auf `color.input.disabled_bg` / `color.button.disabled.bg` |
| **E — Links** | **4.5 : 1** | `color.fg.link` auf Textfläche; zusätzlich Unterscheidung zu Body durch Farbe oder Unterstreichung in Renderer |
| **F — Primärbutton** | **4.5 : 1** | `color.button.primary.fg` auf `color.button.primary.bg` |
| **G — Sekundärbutton** | **4.5 : 1** | `color.button.secondary.fg` auf `color.button.secondary.bg` |
| **H — Input-Text** | **4.5 : 1** | `color.input.fg` auf `color.input.bg` |
| **I — Placeholder** | **4.5 : 1** | `color.input.placeholder` auf `color.input.bg` |
| **J — Tabellen** | **4.5 : 1** | Zelltext auf Zellenhintergrund; Header-Text auf `color.table.header_bg` |
| **K — Selection** | **4.5 : 1** | `color.selection.fg` auf `color.selection.bg` (Textwidgets) |
| **L — Listen-Auswahl** | **4.5 : 1** | `color.fg.on_selected` auf `color.interaction.selected` |
| **M — Fokus** | Sichtbarkeit qualitativ: Rand oder Ring mindestens **2px** wahrnehmbar; wenn nur Farbe: **3 : 1** zum Hintergrund | `color.border.focus`, `color.interaction.focus_ring` |
| **N — Statusflächen** | **4.5 : 1** für Text auf Badge/Fläche | `color.badge.*.fg` auf `color.badge.*.bg` |
| **O — Codeblöcke Markdown** | **4.5 : 1** | `color.markdown.codeblock_fg` auf `color.markdown.codeblock_bg` |
| **P — Inline-Code** | **4.5 : 1** | `color.markdown.inline_code_fg` auf `color.markdown.inline_code_bg` |

**Ausnahme:** Dekorative Graphikelemente (Kanten ohne Text, reine Indikatoren < 3px) — **kein** Textkontrast nötig; Indikatoren sollen dennoch auf `color.bg.app` erkennbar sein (subjektiv im QA-Check).

---

## 2. Pflicht-Paare pro Theme (CI)

Für jedes built-in `theme_id` (`light_default`, `dark_default`, `workbench`, später viertes Theme) müssen folgende Paare die zugehörige Mindestregel erfüllen:

1. `fg.primary` × `bg.surface`  
2. `fg.primary` × `bg.app`  
3. `fg.secondary` × `bg.surface`  
4. `fg.muted` × `bg.surface`  
5. `fg.link` × `bg.surface`  
6. `button.primary.fg` × `button.primary.bg`  
7. `input.fg` × `input.bg`  
8. `input.placeholder` × `input.bg`  
9. `selection.fg` × `selection.bg`  
10. `markdown.codeblock_fg` × `markdown.codeblock_bg`  
11. `markdown.body` × `bg.surface` (wenn Body direkt auf Surface liegt)  
12. `nav.active_fg` × `nav.active_bg`  
13. `table.fg` × `table.bg`  
14. `table.header_fg` × `table.header_bg`  
15. `badge.success.fg` × `badge.success.bg` (analog warning, error, info)

Erweiterung bei Einführung von `color_profile_id`: dieselben Paare gegen Profil-Werte.

---

## 3. Light- vs. Dark-spezifisch

- **Light:** Hintergründe tenden hell — Risiko zu blasser `border.subtle`; sicherstellen, dass `border.default` Tabellen/Inputs noch sichtbar trennt (subjektiver QA-Check, kein fixer Kontrast für Linien).  
- **Dark:** Risiko zu dunklem `fg.muted` — Regel C verschärft gegenüber klassischem 3:1 für kleine Schrift.  
- **Workbench (kühl/teal):** `color.state.accent` und `color.domain.monitoring.*` dürfen nicht `fg.primary` unlesbar machen, wenn sie großflächig neben Text vorkommen.

---

## 4. Markdown / Chat-spezifisch

- Chat-Blasen: **`assistant_fg` × `assistant_bg`** und **`user_fg` × `user_bg`** jeweils ≥ 4.5 : 1.  
- Blockquote: `markdown.quote` auf Bubble-Hintergrund: wenn Quote **innerhalb** Assistant-Bubble, ist Hintergrund die Bubble — dann Quote-Text gegen **Bubble-BG** prüfen, nicht nur gegen global surface. *Implementierungsregel:* Renderer wählt Token-Kontext `inside_assistant_bubble` oder vereinheitlicht Hintergrund für Quote auf `markdown.quote` eigene BG-Fläche.

---

## 5. Fehler- und Warnzustände

- `color.state.error` als reine **Akzentfarbe** (Ränder, Icons) ohne große Fläche: Kontrast zu Hintergrund **3 : 1** ausreichend.  
- Sobald `color.badge.error.bg` als **Vollfläche** mit Text: Paar **N** (4.5 : 1).

---

## 6. Durchführung in CI

- Neues Testmodul: lädt `ResolvedTokenMap` pro Theme, prüft Paare aus §2.  
- Verstoß: Build fail.  
- Temporäre Abweichung: nur mit `pytest.mark.xfail` + Ticket-Link + Frist (max. 1 Release).

---

## 7. Manuelles Theme-QA (Release-Checkliste)

- [ ] Shell: Nav selected, Breadcrumb, TopBar lesbar.  
- [ ] Control Center: Tabellen unter dark + workbench.  
- [ ] Chat: lange Nachricht, Codeblock, Tabelle im Markdown.  
- [ ] Hilfe-Browser: Links, Code, Blockquote.  
- [ ] Monitoring: Runtime-Debug dunkle Panels + Text.  
- [ ] Workflow-Editor: Knoten selected + Statusfarben.  
- [ ] Settings: API-Key-Feedback (success/error).
