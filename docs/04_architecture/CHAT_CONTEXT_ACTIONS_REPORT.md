# Chat-Kontext-Aktionen – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Chat von passivem Interface zu aktivem Arbeitswerkzeug erweitern.

---

## 1. Ausgangslage

Der Chat war kontextbewusst (Projekt, Chat, Topic sichtbar in der ContextBar), aber der Kontext war nur Anzeige – keine Aktionen direkt aus dem Kontext heraus möglich.

---

## 2. Umgesetzte Änderungen

### 2.1 Analyse

**Dokument:** `docs/04_architecture/CHAT_CONTEXT_ACTIONS_ANALYSIS.md`

- Identifizierte Aktionen: Chat verschieben, Topic zuweisen, Chat umbenennen, Neuer Chat, Kontext wechseln
- UI-Optionen bewertet (Kontextbar erweitern, Kontextmenü, Aktionsbuttons)
- Service-Anbindung ohne neue Schicht
- Konsistenz-Regeln definiert

### 2.2 Service-Erweiterung

**ProjectService.move_chat_to_project(chat_id, target_project_id, topic_id=None)**

- Entfernt Chat aus aktuellem Projekt (falls vorhanden)
- Ordnet Chat dem Zielprojekt zu
- Ermöglicht Verschieben zwischen Projekten und Hinzufügen globaler Chats zu Projekten

### 2.3 ChatContextBar – Interaktiv

**Datei:** `app/gui/domains/operations/chat/panels/chat_context_bar.py`

| Änderung | Beschreibung |
|----------|--------------|
| Klickbare Labels | Projekt-, Chat-, Topic-Labels als flache Buttons (Cursor: Pointer) |
| Signale | `project_clicked`, `chat_clicked`, `topic_clicked`, `context_menu_requested` |
| Kontextmenü | Rechtsklick auf Bar → Kontextmenü mit allen Aktionen |

### 2.4 ChatWorkspace – Kontext-Aktionen

**Datei:** `app/gui/domains/operations/chat/chat_workspace.py`

| Aktion | Trigger | Handler |
|--------|---------|---------|
| Projekt wechseln | Klick auf Projekt-Label | `_on_context_bar_project_clicked` → ProjectSwitcherDialog |
| Chat umbenennen | Klick auf Chat-Label | `_on_context_bar_chat_clicked` → Details-Panel Umbenennen |
| Topic ändern | Klick auf Topic-Label | `_on_context_bar_topic_clicked` → Details-Panel Topic-Combo |
| Kontextmenü | Rechtsklick auf Bar | `_show_context_bar_menu` → build_context_bar_context_menu |

### 2.5 Kontextmenü

**Datei:** `app/gui/domains/operations/chat/panels/chat_item_context_menu.py`

- Neue Funktion: `build_context_bar_context_menu(...)`
- Aktionen: Projekt wechseln, Chat umbenennen, Zu Topic verschieben, Pin/Archive/ Duplicate, **Chat verschieben zu…**, Löschen
- Für globale Chats: „Chat zu Projekt hinzufügen…"
- `_do_move_chat_to_project`: Verschiebt Chat und wechselt aktives Projekt

### 2.6 Styling

**Datei:** `app/gui/themes/base/shell.qss`

- Hover-Effekt für klickbare Kontext-Labels (color_text bei Hover)

---

## 3. Konsistenz

| Aktion | ContextBar | NavigationPanel | DetailsPanel |
|--------|------------|-----------------|--------------|
| Projekt wechseln | ✓ (project_context_changed) | ✓ (subscribe) | ✓ (refresh) |
| Chat verschieben | ✓ refresh | ✓ refresh | ✓ refresh |
| Topic ändern | ✓ refresh | ✓ refresh | ✓ refresh |
| Chat umbenennen | ✓ refresh | ✓ refresh | ✓ refresh |
| Neuer Chat | ✓ refresh | ✓ refresh | ✓ refresh |

**Implementierung:** Alle Aktionen rufen `on_action`-Callback auf, der `_session_explorer.refresh()` und `_refresh_context_bar()` auslöst (bereits über `_on_details_chat_updated` etabliert).

---

## 4. Tests

**Neu:** `tests/structure/test_chat_context_actions.py`

| Test | Verifiziert |
|------|-------------|
| `test_move_chat_to_project` | Chat verschieben zwischen Projekten |
| `test_move_global_chat_to_project` | Globaler Chat zu Projekt hinzufügen |
| `test_topic_change_updates_context` | Topic ändern → get_chat_info liefert neues Topic |
| `test_new_chat_in_project_context` | Neuer Chat im Projekt-Kontext hat korrektes Projekt |
| `test_context_bar_signals` | ContextBar emittiert project_clicked, chat_clicked, topic_clicked |

---

## 5. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `chat_context_bar.py` | Klickbare Labels, Signale, Kontextmenü |
| `chat_workspace.py` | Handler für Kontext-Aktionen, Verbindung |
| `chat_item_context_menu.py` | build_context_bar_context_menu, _do_move_chat_to_project |
| `project_service.py` | move_chat_to_project |
| `shell.qss` | Hover-Styles für Kontext-Labels |
| `CHAT_CONTEXT_ACTIONS_ANALYSIS.md` | Neu |
| `CHAT_CONTEXT_ACTIONS_REPORT.md` | Neu |
| `test_chat_context_actions.py` | Neu |

---

## 6. Ergebnis

Der Chat ist nicht mehr nur Anzeige, sondern ein **interaktiver Arbeitsraum im Kontext eines Projekts**:

- Nutzer kann Projekt wechseln, Chat umbenennen, Topic ändern per Klick auf die Kontextbar
- Rechtsklick eröffnet erweiterte Aktionen (Chat verschieben, Pin, Archive, Duplicate, Delete)
- Keine neue Architektur, keine KI-Erweiterung – reine Nutzung bestehender Services
- Keine Überladung – keine neue UI-Ebene
