# Projektbezogene Prompt-Bibliothek – Implementierung

**Status:** Implementiert  
**Datum:** 2026-03-15

## Überblick

Die Prompt-Liste im PromptStudioWorkspace wurde zu einem projektbezogenen Prompt-Explorer ausgebaut. Der Nutzer arbeitet klar im Kontext eines Projekts, sieht Projekt- und globale Prompts getrennt und kann Prompts bearbeiten, speichern und löschen.

---

## Wichtigste Klassen

| Klasse | Datei | Zweck |
|--------|------|-------|
| **PromptLibraryPanel** | `panels/library_panel.py` | Projektbezogener Explorer: Projekt-Header, Neuer Prompt, Suche, gruppierte Liste (Projekt-Prompts / Globale Prompts) |
| **PromptListItemWidget** | `panels/prompt_list_item.py` | Einzelner Prompt-Eintrag mit Name, Scope-Badge (Projekt/Global), Kategorie, letzte Änderung |
| **PromptEditorPanel** | `panels/editor_panel.py` | Vollständiger Editor: Name, Beschreibung, Scope, Kategorie, Inhalt; Speichern, Dirty-State |
| **PromptStudioInspector** | `gui/inspector/prompt_studio_inspector.py` | Inspector mit echten Metadaten: Name, Scope, Kategorie, Tags, Erstellt/Geändert |
| **PromptStudioWorkspace** | `prompt_studio_workspace.py` | Koordinator: Library links, Editor Mitte, Inspector rechts; Signal-Verknüpfung |

---

## UX-Entscheidungen

1. **Projektkontext sichtbar**  
   Header zeigt aktives Projekt oder „Bitte Projekt auswählen“. Ohne Projekt werden nur globale Prompts angezeigt.

2. **Klare Trennung Projekt vs. Global**  
   Zwei Gruppen: „Projekt-Prompts“ und „Globale Prompts“. Jeder Eintrag hat ein Badge (Projekt/Global).

3. **Neuer Prompt**  
   Nur bei aktivem Projekt möglich. Erstellt projektbezogenen Prompt.

4. **Suche**  
   Suchfeld filtert sowohl Projekt- als auch globale Prompts.

5. **Aktive Markierung**  
   Ausgewählter Prompt wird visuell hervorgehoben (blauer Rahmen).

6. **Kontextmenü**  
   Rechtsklick auf Prompt → „Löschen“ (mit Bestätigung).

7. **Editor-Scope**  
   Beim Speichern: Wenn Scope „Projekt“ gewählt, aber kein Projekt aktiv → automatisch „Global“.

---

## Service-Integration

| Methode | Beschreibung |
|---------|--------------|
| `list_project_prompts(project_id, filter_text)` | Nur projektbezogene Prompts |
| `list_global_prompts(filter_text)` | Nur globale Prompts |
| `create(prompt)` | Neuer Prompt |
| `update(prompt)` | Prompt aktualisieren |
| `delete(prompt_id)` | Prompt löschen |

---

## Startanweisung

```bash
# Mit virtuellem Environment
cd Linux-Desktop-Chat
.venv/bin/python main.py

# Oder
.venv/bin/python run_gui_shell.py
```

1. Projekt auswählen (Operations → Projekte)
2. Operations → Prompt Studio öffnen
3. Projekt-Prompts und globale Prompts erscheinen gruppiert
4. Prompt auswählen → Editor füllt sich, Inspector zeigt Metadaten
5. Bearbeiten → Speichern
6. Neuer Prompt → Dialog → Prompt wird im Projekt angelegt

---

## Dateien (neu/geändert)

- `app/prompts/prompt_repository.py` – `list_project_prompts`, `list_global_prompts`
- `app/prompts/prompt_service.py` – `list_project_prompts`, `list_global_prompts`
- `app/prompts/storage_backend.py` – Backend-Anpassungen
- `app/gui/domains/operations/prompt_studio/panels/library_panel.py` – Neugestaltung
- `app/gui/domains/operations/prompt_studio/panels/prompt_list_item.py` – **neu**
- `app/gui/domains/operations/prompt_studio/panels/editor_panel.py` – Vollständiger Editor (ersetzt Placeholder)
- `app/gui/inspector/prompt_studio_inspector.py` – Echte Metadaten
- `app/gui/domains/operations/prompt_studio/prompt_studio_workspace.py` – Layout, Signale
