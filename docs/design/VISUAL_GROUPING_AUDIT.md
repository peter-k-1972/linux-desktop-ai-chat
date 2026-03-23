# Visuelle Gruppierung & Hierarchie

**Fragestellungen:** Zusammengehörige Controls gruppiert? Zu viele gleichartige Panels? Header/Sections gestaffelt? Secondary zu dominant? Primary klar? Optische Löcher vs. gedrängte Inseln?

**Methode:** Strukturanalyse der Layout-Bäume (Spacing, Margins, Cards, QGroupBox, SectionCard) + QSS-Flächen.

---

## 1. Zusammengehörige Controls

| Bereich | Bewertung | Evidenz |
|---------|-----------|---------|
| **Settings-Kategorien** | gut | QSS `#settingsPanel` mit Border+Radius+Padding — Karten lesen sich als Blöcke. |
| **Control Center Panels** | gemischt | `cc_panel_frame_style()` rahmt Karten; nicht alle CC-Dateien nutzen dieselbe Hülle (`_cc_panel_style` Duplikate). |
| **Chat Composer** | gut | Zeilen mit `spacing 12`; Model-Row getrennt von Input — logische Gruppe. |
| **Workflow Editor** | gut | Toolbar-Zeilen + `addStretch` trennen Primär/ Sekundäraktionen. |
| **Inspector (Shell)** | gut | `QGroupBox` + 12px Layout — klassische Form-Gruppierung. |
| **Inspector (Workbench)** | schwächer | `SectionCard` vorhanden, aber inner margin 10px — weniger „Luft“ zwischen inhaltlichen Gruppen als Shell. |

**Lücke:** Viele **Formulare ohne umrahmte Gruppe** — nur `QFormLayout` auf weißer Fläche; Hierarchie entsteht nur über Abstand (12/16), nicht über Container.

---

## 2. Zu viele ähnliche Panels

| Muster | Risiko |
|--------|--------|
| Mehrspaltige CC-/Runtime-Workspaces mit **jeweils gleichem 16px-Padding** | Nutzer erkennt Bereichsgrenzen nur über Titel, nicht über Flächenstufe — **monoton**. |
| **KPI-Karten** (`project_stats_panel`) neben **Standard-Panels** | unterschiedliche Padding-Werte (14/12) ohne klare semantische Bedeutung — wirkt „zusammengebastelt“. |

---

## 3. Header, Sektionen, Inhalt

| Muster | Bewertung |
|--------|-----------|
| **Zwei Header-Ebenen** (z. B. Workspace-Titel + Panel-Titel) | In Shell via QSS `#workspaceTitle` klar; in manchen Domains fehlt konsistente zweite Ebene. |
| **Uppercase-Section-Labels** (Workbench SectionCard) | Starke visuelle Staffelung; gut — sollte nicht in jedem Panel gemischt mit normaler Caption vorkommen. |
| **Runtime-Nav** mit eigener Typo (QSS hardcoded px) | Bricht Hierarchie zur restlichen App (siehe früheres Theme-Audit). |

---

## 4. Secondary vs. Primary

| Bereich | Befund |
|---------|--------|
| **Chat** | Primary Send 48px, Secondary Prompt — Send dominiert **stark** (Höhe + Farbe) — beabsichtigt, aber Layout-Höhe bricht Raster. |
| **Command Center** | `addStretch` in Header — Primary Links links, Secondary rechts — idiomatisch. |
| **TopBar** | Icons gleich gewichtet — kein visueller „Primary“ außer Project Switcher — **akzeptabel** für globale Leiste. |

---

## 5. Optische Löcher und gedrängte Inseln

| Phänomen | Ort | Ursache |
|----------|-----|---------|
| **Loch** | Zentrum bei `ConversationView` mit 1200px Spalte auf breitem Monitor | Starke Ränder durch `addStretch` + fixe Breite — Inhalt wirkt „schmal schwimmend“. |
| **Loch** | Dashboard `32px` Außenrand | Viel Weißraum bei wenig Kacheln. |
| **Gedrängt** | `context_action_bar` 6px vertikal + viele Icons | Hohe Informationsdichte auf wenig Höhe. |
| **Gedrängt** | Listen `spacing(2)` | Zeilen fast zusammen — ok für Power-User, anstrengend bei viel Text. |

---

## 6. Empfehlungen (gruppierungsbezogen)

1. **Zwei Container-Typen** durchziehen: **„Card“** (16–20px Padding, Border) für fachliche Gruppen; **„Plain“** (12px) für Tool-Spalten.  
2. **Workbench Inspector:** inner margin von **10 → 12** um mit Shell-Inspector zu matchen.  
3. **Chat:** fixe 1200px aufheben — Gruppierung über max-width + zentrierten Inhalt ohne horizontales Scrollen auf typischen Fenstern.  
4. **CC-Panels:** einheitliche Panel-Hülle (ein Style-Helper) statt mehrerer `_cc_panel_style`-Kopien.

---

*Alignment:* [ALIGNMENT_AUDIT.md](./ALIGNMENT_AUDIT.md)
