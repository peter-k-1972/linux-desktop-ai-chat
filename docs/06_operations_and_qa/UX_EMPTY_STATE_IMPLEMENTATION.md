# Empty-State-/Info-State-System – Implementierung

## Übersicht

Wiederverwendbares Empty-State-System für leere, unkonfigurierte oder noch nicht ausgebaute Zustände. Alle betroffenen Bereiche nutzen nun ein konsistentes, produktartiges Erscheinungsbild.

---

## 1. Betroffene Dateien

### Neue Komponente
| Datei | Beschreibung |
|------|--------------|
| `app/gui/widgets/__init__.py` | Widget-Paket-Export |
| `app/gui/widgets/empty_state_widget.py` | **EmptyStateWidget** – wiederverwendbare Komponente (kanonisch) |

### QSS-Anpassungen
| Datei | Änderung |
|------|----------|
| `app/gui/themes/base/shell.qss` | Styles für `#emptyStateWidget`, `#emptyStateTitle`, `#emptyStateDescription`, `#emptyStateHint` |

### Ersetzte Placeholder / Empty States
| Datei | Bereich | Vorher | Nachher |
|------|---------|--------|---------|
| `app/ui/settings/categories/project_category.py` | Settings → Project | QFrame + QLabels | EmptyStateWidget (Icon: PROJECTS) |
| `app/ui/settings/categories/workspace_category.py` | Settings → Workspace | QFrame + QLabels | EmptyStateWidget (Icon: GEAR) |
| `app/ui/knowledge/knowledge_workspace.py` | KnowledgeContentPlaceholder | Technischer Hinweis | EmptyStateWidget (Icon: KNOWLEDGE) |
| `app/ui/knowledge/source_details_panel.py` | Quelldetails (keine Auswahl) | "Select a source to view details." | EmptyStateWidget (compact) |
| `app/ui/knowledge/index_status_page.py` | Index Status (kein Projekt) | "No project selected..." | EmptyStateWidget (Icon: PROJECTS) |
| `app/gui/domains/operations/knowledge/panels/knowledge_source_explorer_panel.py` | Quellenliste | QLabel | EmptyStateWidget (compact) |
| `app/gui/domains/operations/prompt_studio/panels/library_panel.py` | Prompt-Liste | QLabel | EmptyStateWidget (compact) |
| `app/gui/domains/operations/chat/panels/session_explorer_panel.py` | Chat-Liste | QLabel | EmptyStateWidget (compact) |
| `app/ui/chat/chat_navigation_panel.py` | Chat-Navigation | QLabel | EmptyStateWidget (compact) |

---

## 2. EmptyStateWidget – API

```python
from app.gui.widgets import EmptyStateWidget

# Vollständige Karte (Settings, Index Status, etc.)
EmptyStateWidget(
    title="Projektspezifische Einstellungen",
    description="Dieser Bereich wird in einer zukünftigen Version erweitert.",
    icon=IconRegistry.PROJECTS,
    hint="Optionaler Zusatzhinweis",
    parent=self,
)

# Kompakte Variante (Listen-Bereiche)
EmptyStateWidget(
    title="Kein Projekt ausgewählt",
    description="Wähle ein Projekt, um Chats anzuzeigen.",
    compact=True,
    parent=self,
)

# Dynamische Inhalte (z.B. wechselnde Empty-States)
widget.set_content("Neue Titel", "Neue Beschreibung")
```

### Parameter
| Parameter | Typ | Beschreibung |
|----------|-----|--------------|
| `title` | str | Hauptüberschrift |
| `description` | str | Kurze Erklärung |
| `icon` | str \| None | Icon-Name aus IconRegistry (nur bei `compact=False`) |
| `hint` | str \| None | Optionaler Zusatzhinweis (nur bei `compact=False`) |
| `compact` | bool | Kompakte Darstellung für Listen (transparent, zentriert) |

---

## 3. Ersetzte Texte

| Kontext | Vorher | Nachher |
|---------|--------|---------|
| Settings Project | Projektspezifische Einstellungen / Dieser Bereich wird... | Unverändert (bereits produktartig) |
| Settings Workspace | Workspace-spezifische Einstellungen / Dieser Bereich wird... | Unverändert |
| Source Details | "Select a source to view details." | "Quelldetails" / "Wähle eine Quelle in der Liste, um Details anzuzeigen." |
| Index Status | "No project selected. Select a project to view index status." | "Kein Projekt ausgewählt" / "Wähle ein Projekt, um den Index-Status anzuzeigen." |
| Knowledge Quellen (kein Projekt) | "Bitte Projekt auswählen." | "Kein Projekt ausgewählt" / "Wähle ein Projekt, um Quellen anzuzeigen." |
| Knowledge Quellen (leer) | "Keine Quellen. Datei oder Ordner hinzufügen." | "Keine Quellen" / "Datei oder Ordner hinzufügen." |
| Prompt Library (kein Projekt) | "Bitte Projekt auswählen." | "Kein Projekt ausgewählt" / "Wähle ein Projekt, um Prompts anzuzeigen." |
| Prompt Library (leer) | "Keine Prompts. Neuen Prompt anlegen." | "Keine Prompts" / "Lege einen neuen Prompt an." |
| Chat-Liste (kein Projekt) | "Bitte Projekt auswählen." | "Kein Projekt ausgewählt" / "Wähle ein Projekt, um Chats anzuzeigen." |
| Chat-Liste (leer) | "Keine Chats. Neuen Chat anlegen." | "Keine Chats" / "Lege einen neuen Chat an." |
| KnowledgeContentPlaceholder | "Content panel – implement section-specific UI here." | "Dieser Bereich wird in einer zukünftigen Version erweitert." |

---

## 4. UX-Begründung

1. **Konsistenz**: Ein einheitliches Muster für alle leeren/Info-Zustände – Nutzer erkennen sofort den Zustandstyp.
2. **Nicht fehlerhaft**: Neutrale, freundliche Darstellung; keine Warnfarben oder Fehlersemantik.
3. **Produktartig**: Klare, knappe Texte statt technischer Placeholder.
4. **Theme-verträglich**: QSS nutzt Design-Tokens (`{{color_text}}`, `{{color_text_secondary}}` etc.) – Dark/Light Mode bleiben lesbar.
5. **Zwei Modi**: Vollständige Karte für Settings/Seiten, kompakte Variante für Listen – jeweils passend zum Kontext.

---

## 5. Manuelle Prüfschritte

1. **Settings → Project**
   - Leere Karte mit Icon, Titel "Projektspezifische Einstellungen", Beschreibung.
   - Kein roher Platzhalter-Look.

2. **Settings → Workspace**
   - Analog zu Project, Titel "Workspace-spezifische Einstellungen".

3. **Knowledge – Quellen**
   - Ohne Projekt: "Kein Projekt ausgewählt" / "Wähle ein Projekt, um Quellen anzuzeigen."
   - Mit Projekt, keine Quellen: "Keine Quellen" / "Datei oder Ordner hinzufügen."

4. **Knowledge – Quelldetails (rechts)**
   - Ohne Auswahl: "Quelldetails" / "Wähle eine Quelle in der Liste, um Details anzuzeigen."

5. **Knowledge – Index**
   - Ohne Projekt: "Kein Projekt ausgewählt" / "Wähle ein Projekt, um den Index-Status anzuzeigen."

6. **Prompt Studio – Bibliothek**
   - Ohne Projekt: "Kein Projekt ausgewählt" / "Wähle ein Projekt, um Prompts anzuzeigen."
   - Mit Projekt, keine Prompts: "Keine Prompts" / "Lege einen neuen Prompt an."

7. **Chat – Session Explorer**
   - Ohne Projekt: "Kein Projekt ausgewählt" / "Wähle ein Projekt, um Chats anzuzeigen."
   - Mit Projekt, keine Chats: "Keine Chats" / "Lege einen neuen Chat an."

8. **Theme-Wechsel**
   - Light/Dark Mode: Texte und Hintergründe bleiben lesbar, keine harten Farben.
