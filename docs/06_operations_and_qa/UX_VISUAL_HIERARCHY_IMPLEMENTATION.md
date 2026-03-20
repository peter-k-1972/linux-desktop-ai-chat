# Visuelle Hierarchie – UX-Polish Implementierung

## Übersicht

Gezielte, minimalinvasive Verbesserungen der visuellen Hierarchie. Keine Featureentwicklung, keine Layout-Umbrüche. Fokus: Ruhe, Lesbarkeit, konsistente Gewichtung.

---

## 1. Betroffene Dateien

### QSS (zentrale Styles)
| Datei | Änderung |
|-------|----------|
| `app/gui/themes/base/shell.qss` | #workspaceTitle, #workspaceSubtitle, #inspectorHost QGroupBox/QLabel, #inspectorPrimaryValue, domainNavTitle/Subtitle (Tokens) |
| `app/gui/themes/base/base.qss` | #secondaryButton (für zurückhaltende Aktionen) |

### Workspace-Header
| Datei | Änderung |
|-------|----------|
| `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` | Titel: ObjectName workspaceTitle, Margins 20, Spacing 16 |
| `app/gui/domains/operations/agent_tasks/agent_tasks_workspace.py` | Titel: ObjectName workspaceTitle, Margins 20, Spacing 16 |
| `app/gui/domains/operations/knowledge/knowledge_workspace.py` | Titel: ObjectName workspaceTitle, Margins 20, Spacing 16 |

### Inspector
| Datei | Änderung |
|-------|----------|
| `app/gui/inspector/chat_context_inspector.py` | Inline-Styles entfernt, ObjectNames (inspectorPrimaryValue, panelStatus), Topic-Combo vereinfacht |
| `app/gui/inspector/prompt_studio_inspector.py` | Inline-Styles entfernt |
| `app/gui/inspector/inspector_host.py` | Default-Content: Margins 16, Spacing 12 |

---

## 2. Angepasste Header/Layouts

### Workspace-Header (einheitlich)
- **Vorher**: 18px vs 20px, font-weight bold, hardcodierte Farben (#1f2937)
- **Nachher**: #workspaceTitle – font_size_primary_title (18px), font_weight_semibold, color_text (Token)
- **Workspaces**: Prompt Studio, Agent Tasks, Knowledge / RAG

### Spacing
- **Prompt Studio Center**: 24→20px Margins, 20→16px Spacing
- **Agent Tasks**: 24→20px Margins, 20→16px Spacing
- **Knowledge Right**: 24→20px Margins
- **Inspector Host Default**: 20→16px Margins, 16→12px Spacing

### Domain-Nav (Sidebar)
- **domainNavTitle**: font_weight_semibold, font_size_sm (Tokens statt hardcoded 600, 12px)
- **domainNavSubtitle**: font_size_xs (Token statt 11px)

---

## 3. Behobene spacing-/typografiebezogene Probleme

| Problem | Lösung |
|---------|--------|
| Workspace-Titel 18px vs 20px inkonsistent | Einheitlich 18px (#workspaceTitle) |
| Workspace-Titel font-weight bold zu dominant | font_weight_semibold (600) – ruhiger |
| Hardcodierte Farben (#1f2937, #374151, #6b7280) | Theme-Tokens (color_text, color_text_secondary) |
| Inspector konkurriert optisch mit Hauptinhalt | QGroupBox/QLabel in #inspectorHost mit color_text_secondary |
| Inspector-Sektionen zu laut (bold #374151) | font_weight_semibold, color_text_secondary |
| Übergroße Workspace-Margins (24px) | 20px für ruhigeren Rhythmus |
| Domain-Nav ohne Token-Nutzung | font_size_sm, font_size_xs, font_weight_semibold |
| Kein Stil für sekundäre Buttons | #secondaryButton in base.qss (optional nutzbar) |

---

## 4. UX-Begründung

1. **Hierarchie**: Haupttitel klar dominant (18px, semibold), aber nicht übertrieben (kein bold).
2. **Inspector zurückgenommen**: Sekundärinfos (color_text_secondary) – Hauptarbeitsfläche bleibt Fokus.
3. **Konsistenz**: Ein ObjectName (#workspaceTitle) für alle Workspace-Header – einheitliches Erscheinungsbild.
4. **Spacing**: 20px statt 24px reduziert übergroße Leerflächen, 16px Spacing für dichteren Rhythmus.
5. **Token-Nutzung**: Keine neuen Farben – bestehende Theme-Tokens für Dark/Light-Kompatibilität.
6. **Domain-Nav**: Kleiner, zurückhaltender – konkurriert nicht mit Hauptinhalt.

---

## 5. Manuelle Vorher/Nachher-Prüfpunkte

### Workspace-Header
1. **Prompt Studio**: Titel „Prompt Studio“ – vorher 20px bold, nachher 18px semibold.
2. **Agent Tasks**: Titel „Agent Tasks“ – analog.
3. **Knowledge**: Titel „Knowledge / RAG“ – vorher 18px, nachher einheitlich 18px semibold.
4. **Abstände**: Weniger Luft um Titel, dichterer Content-Block.

### Inspector (Chat, Prompt Studio)
1. **Chat-Kontext**: Sektionen (Chat, Projekt, Topic, …) – vorher bold #374151, nachher semibold color_text_secondary.
2. **Chat-Titel**: Bleibt hervorgehoben (#inspectorPrimaryValue – color_text).
3. **Kontextstatus**: Grüner Status (panelStatus) unverändert.
4. **Prompt-Metadaten**: Sekundärtext zurückgenommen.

### Domain-Nav (Operations-Sidebar)
1. **Titel** (z.B. „Knowledge“, „Prompt Studio“): Unverändert sichtbar, Token-basiert.
2. **Untertitel**: font_size_xs für Meta-Infos.

### Spacing
1. **Prompt Studio Center**: Weniger Rand, kompakterer Block.
2. **Agent Tasks**: Analog.
3. **Inspector-Platzhalter**: Leicht reduzierter Innenabstand.
