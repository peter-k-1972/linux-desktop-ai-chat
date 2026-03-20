# Knowledge-Subsystem: UI → GUI Migration – Ist-Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** 1 – Ist-Analyse

---

## 1. Ausgangslage

### 1.1 Legacy-Bereich

| Pfad | Typ | Inhalt |
|------|-----|--------|
| `app/ui/knowledge/` | Verzeichnis | Nur `__init__.py` – Re-Exports aus `app.gui.domains.operations.knowledge` |

### 1.2 Bereits migriert (kanonisch unter gui)

- **app/gui/domains/operations/knowledge/** – vollständige Implementierung:
  - `knowledge_workspace.py` – KnowledgeWorkspace (RAG, projektbezogener Quellen-Explorer)
  - `panels/knowledge_source_explorer_panel.py` – KnowledgeSourceExplorerPanel
  - `panels/knowledge_overview_panel.py` – KnowledgeOverviewPanel
  - `panels/retrieval_test_panel.py` – RetrievalTestPanel
  - `panels/source_list_item.py` – SourceListItemWidget
  - `panels/source_details_panel.py` – SourceDetailsPanel
  - `panels/collection_panel.py` – CollectionPanel
  - `panels/collection_dialog.py` – CreateCollectionDialog, RenameCollectionDialog, AssignSourcesDialog
  - `panels/index_status_page.py` – IndexStatusPage
  - `panels/chunk_viewer_panel.py` – ChunkViewerPanel
  - `panels/knowledge_navigation_panel.py` – KnowledgeNavigationPanel, KNOWLEDGE_SECTIONS

---

## 2. Analyse `app/ui/knowledge/`

### 2.1 Enthaltene Dateien

| Datei | Inhalt | Klassifikation |
|-------|--------|----------------|
| `__init__.py` | Re-Export aller Komponenten aus gui | REMOVE_DEAD |

### 2.2 Externe Konsumenten

**Keine.** Kein produktiver Code importiert `app.ui.knowledge` oder Untermodule.

- `app.gui.domains.operations.operations_screen` importiert `from app.gui.domains.operations.knowledge import KnowledgeWorkspace`
- `tests/behavior/ux_regression_tests` importiert aus `app.gui.domains.operations.knowledge.knowledge_workspace`

### 2.3 Abhängigkeiten / Kontext

- Knowledge-Funktionalität baut auf RAG, ChromaDB, Dokumentenansicht und Workspace-Navigation auf
- Keine Überschneidungen mit Prompts, Project oder Command Center
- Knowledge ist Teil der Operations-Domain (wie Chat, Prompt Studio)

---

## 3. Zielstruktur

### 3.1 Gewählte Struktur

Die kanonische Struktur existiert bereits unter:

```
app/gui/domains/operations/knowledge/
├── __init__.py
├── knowledge_workspace.py
└── panels/
    ├── __init__.py
    ├── knowledge_source_explorer_panel.py
    ├── knowledge_overview_panel.py
    ├── retrieval_test_panel.py
    ├── source_list_item.py
    ├── source_details_panel.py
    ├── collection_panel.py
    ├── collection_dialog.py
    ├── index_status_page.py
    ├── chunk_viewer_panel.py
    └── knowledge_navigation_panel.py
```

**Keine neue Struktur unter `app/gui/domains/knowledge/`.**  
Das Knowledge-Subsystem ist Teil der Operations-Domain und liegt korrekt unter `operations/knowledge`.

### 3.2 Aktion

- **app/ui/knowledge/** → **vollständig entfernen** (nur Re-Exports, keine Konsumenten)
- Keine physische Migration nötig – Implementierung bereits in gui

---

## 4. Zusammenfassung

| Komponente | Aktion |
|------------|--------|
| `app/ui/knowledge/` (komplett) | Entfernen (tote Re-Exports) |
| `app/gui/domains/operations/knowledge/` | Unverändert – kanonische Implementierung |
| Übergangsbrücken | Keine nötig – direkte Entfernung möglich |
