# Projektbezogene Knowledge-/Quellen-Listen-UX

**Version:** 1.0  
**Datum:** 2026-03-15  
**Status:** Implementiert

---

## 1. Überblick

Die Knowledge-/Dateiliste im KnowledgeWorkspace ist nun ein **projektbezogener Wissens-Explorer**:

- Zeigt nur Quellen des aktiven Projekts
- Projektkontext sichtbar im Header
- Collection = project_{id}
- Status pro Quelle (indexiert, registriert, etc.)
- Typ pro Quelle (Datei, Ordner)

---

## 2. Mentales Modell

```
Aktives Projekt
 └── Wissensquellen dieses Projekts
      ├── Collection: project_{id}
      ├── Datei A (indexiert)
      ├── Ordner B (indexiert)
      └── ...
```

---

## 3. Komponenten

### KnowledgeSourceExplorerPanel

- **Projekt-Header:** Zeigt aktives Projekt oder „Bitte Projekt auswählen“
- **Collection-Info:** project_{id} · Chunk-Anzahl
- **+ Datei / + Ordner:** Hinzufügen (nur bei aktivem Projekt)
- **Quellenliste:** Name, Typ, Status pro Quelle

### SourceListItemWidget

- Name (max. 50 Zeichen)
- Typ (Datei, Ordner, Quelle)
- Status (indexiert, registriert, etc.)
- Aktive Markierung (blauer Rahmen)

### KnowledgeInspector

- Projekt
- Collection
- Ausgewählte Quelle: Name, Typ, Status, Pfad
- Letzter Retrieval: Query, Treffer

---

## 4. Service-Integration

### KnowledgeService – neue Methoden

```python
get_space_for_project(project_id) -> str
# project_{id}

list_sources_for_project(project_id) -> list
# Quellen mit type, status

get_project_chunk_count(project_id) -> int
# Chunk-Anzahl des Projekt-Spaces
```

### Quellen-Enrichment

- `list_sources()` liefert Quellen mit `type` und `status`
- Bei `_add_source_to_registry`: type (datei/ordner), status (indexiert)
- Bei bestehenden Quellen: type/status aus Pfad abgeleitet, Default „indexiert“

---

## 5. Projektintegration

- **Ohne Projekt:** Leere Liste, „Bitte Projekt auswählen“, Add deaktiviert
- **Projektwechsel:** Quellenliste wird neu geladen
- **Neue Quelle:** Nur mit aktivem Projekt möglich
- **Retrieval:** Nur mit aktivem Projekt möglich

---

## 6. UX-Entscheidungen

1. **Keine globale Quellenliste** – Ohne Projekt keine Quellen sichtbar
2. **Collection = Projekt** – Ein Space pro Projekt (project_{id})
3. **Status pro Quelle** – indexiert, registriert, etc.
4. **Typ pro Quelle** – Datei, Ordner für schnelle Orientierung

---

## 7. Dateien

| Datei | Zweck |
|-------|-------|
| `knowledge_source_explorer_panel.py` | Projektbezogener Quellen-Explorer |
| `source_list_item.py` | Quellen-Eintrag mit Name, Typ, Status |
| `knowledge_workspace.py` | Umstrukturiert, projektbezogen |
| `knowledge_inspector.py` | Titel, Typ, Status, Pfad |
| `knowledge_service.py` | list_sources_for_project, get_space_for_project |

---

## 8. Start

```bash
.venv/bin/python run_gui_shell.py
```

1. Projekt in der TopBar auswählen
2. Operations → Knowledge / RAG
3. Quellenliste zeigt nur Quellen des Projekts
4. „+ Datei“ / „+ Ordner“ hinzufügen
5. Retrieval-Test im Projekt-Space
