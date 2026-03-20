# Chat UI Phase 1 – Architekturanalyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** ARCHITECTURE_GUARD_RULES.md, test_gui_does_not_import_ui.py

---

## Kontext

Agents UI Migration ist abgeschlossen. Die nächste Domain ist **Chat**.

**Bekannte Violations (Architektur-Guard):**
- `gui/legacy/chat_widget.py` → app.ui.chat, app.ui.sidepanel
- `gui/domains/operations/chat/panels/chat_navigation_panel.py` → app.ui.chat.chat_topic_section

**Ziel:** Vorbereitung der Chat UI Migration. Kein Featurebau, keine UI-Neuentwicklung, nur Architektur-Analyse.

---

## 1. Chat UI Analyse: app/ui/chat/

### 1.1 __init__.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Re-Export-Hub für Legacy-Konsumenten. Kombiniert gui- und ui-Module. |
| **Imports** | `app.gui.domains.operations.chat.panels.chat_message_widget`, `app.ui.chat.chat_composer_widget`, `app.ui.chat.chat_header_widget`, `app.ui.chat.conversation_view`, `app.ui.chat.chat_list_item`, `app.ui.chat.chat_topic_section`, `app.gui.domains.operations.chat.panels.topic_editor_dialog`, `app.gui.domains.operations.chat.panels.topic_actions`, `app.gui.domains.operations.chat.panels.chat_item_context_menu` |
| **Abhängigkeiten** | 5 ui-Module (composer, header, conversation_view, list_item, topic_section); 4 gui-Module (message_widget, topic_editor, topic_actions, chat_item_context_menu) |
| **Beziehung zu gui/domains/operations/chat** | Re-exportiert ChatMessageWidget, topic_editor_dialog, topic_actions, chat_item_context_menu aus gui. Re-exportiert ui-Komponenten für Legacy. |
| **Klassifikation** | **KEEP_TEMP** |
| **Begründung** | Wird von gui/legacy/chat_widget und Tests importiert. Nach Migration aller ui-Komponenten zu gui: nur noch Re-Exports aus gui; dann kann ui/chat/__init__ entfernt oder auf reine Re-Exports reduziert werden. |

---

### 1.2 chat_message_widget.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Re-Export. Kanonisch unter app.gui.domains.operations.chat.panels.chat_message_widget. |
| **Imports** | `app.gui.domains.operations.chat.panels.chat_message_widget` |
| **Abhängigkeiten** | Nur gui. Keine eigene Implementierung. |
| **Beziehung zu gui/domains/operations/chat** | Re-exportiert ChatMessageWidget aus gui. |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Reiner Re-Export. Keine eigene Logik. Nach Migration der Konsumenten: Datei entfernen, __init__ anpassen. |

---

### 1.3 chat_item_context_menu.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Re-Export. Kanonisch unter app.gui.domains.operations.chat.panels.chat_item_context_menu. |
| **Imports** | `app.gui.domains.operations.chat.panels.chat_item_context_menu` |
| **Abhängigkeiten** | Nur gui. Keine eigene Implementierung. |
| **Beziehung zu gui/domains/operations/chat** | Re-exportiert build_chat_item_context_menu aus gui. |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Reiner Re-Export. Keine eigene Logik. Nach Migration der Konsumenten: Datei entfernen. |

---

### 1.4 topic_actions.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Re-Export. Kanonisch unter app.gui.domains.operations.chat.panels.topic_actions. |
| **Imports** | `app.gui.domains.operations.chat.panels.topic_actions` |
| **Abhängigkeiten** | Nur gui. Keine eigene Implementierung. |
| **Beziehung zu gui/domains/operations/chat** | Re-exportiert create_topic, rename_topic, delete_topic, assign_chat_to_topic, remove_chat_from_topic, build_topic_header_menu, build_chat_topic_menu aus gui. |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Reiner Re-Export. Keine eigene Logik. Nach Migration der Konsumenten: Datei entfernen. |

---

### 1.5 topic_editor_dialog.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Re-Export. Kanonisch unter app.gui.domains.operations.chat.panels.topic_editor_dialog. |
| **Imports** | `app.gui.domains.operations.chat.panels.topic_editor_dialog` |
| **Abhängigkeiten** | Nur gui. Keine eigene Implementierung. |
| **Beziehung zu gui/domains/operations/chat** | Re-exportiert TopicCreateDialog, TopicRenameDialog, TopicDeleteConfirmDialog aus gui. |
| **Klassifikation** | **REMOVE** |
| **Begründung** | Reiner Re-Export. Keine eigene Logik. Nach Migration der Konsumenten: Datei entfernen. |

---

### 1.6 conversation_view.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Zentrierte Gesprächsfläche. Scrollbarer Nachrichtenbereich mit begrenzter Content-Breite (1200px). Message-Factory-Pattern. |
| **Imports** | `PySide6.QtWidgets`, `PySide6.QtCore`, `app.gui.domains.operations.chat.panels.chat_message_widget` |
| **Abhängigkeiten** | Nur gui (ChatMessageWidget). Keine ui-Abhängigkeit. |
| **Beziehung zu gui/domains/operations/chat** | Nutzt ChatMessageWidget aus gui. ChatWorkspace nutzt ChatConversationPanel (gui) – anderes Design, keine ConversationView. |
| **Klassifikation** | **MIGRATE** |
| **Begründung** | Aktive Implementierung. Wird von gui/legacy/chat_widget und Tests genutzt. ChatWorkspace nutzt ChatConversationPanel (einfacher, QLabel-basiert). Migration: Nach gui/domains/operations/chat/panels/ verschieben oder als Alternative zu ChatConversationPanel integrieren. |

---

### 1.7 chat_header_widget.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Kompakte Topbar: Agent-Auswahl, Modell, Rolle, Auto-Routing, Cloud, Eskalation, Think-Mode, Websuche, RAG, Self-Improve. |
| **Imports** | `PySide6.QtWidgets`, `PySide6.QtCore`, `app.core.models.roles`, `app.resources.styles` |
| **Abhängigkeiten** | core, resources. Keine gui oder ui. |
| **Beziehung zu gui/domains/operations/chat** | ChatWorkspace nutzt ChatInputPanel (einfacher: Modell-Combo, Prompt-Button, Input). ChatHeaderWidget ist voller Feature-Set (Header + Agent + Routing + RAG). |
| **Klassifikation** | **MIGRATE** |
| **Begründung** | Aktive Implementierung. Wird von gui/legacy/chat_widget und Tests genutzt. ChatWorkspace hat kein Äquivalent. Migration: Nach gui/domains/operations/chat/panels/ verschieben. |

---

### 1.8 chat_topic_section.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Collapsible Topic-Sektion für Chat-Navigation. Gruppiert Chats unter Topic-Header. Header: Topic-Name, Collapse-Toggle, Add-Button. Body: ChatListItemWidget-Liste. |
| **Imports** | `PySide6.QtWidgets`, `PySide6.QtCore`, `app.gui.icons`, `app.gui.icons.registry`, `app.ui.chat.chat_list_item` |
| **Abhängigkeiten** | gui (icons), **ui (chat_list_item)**. |
| **Beziehung zu gui/domains/operations/chat** | Wird von ChatNavigationPanel (gui) importiert – **einzige gui→ui Violation**. ChatSessionExplorerPanel nutzt TopicSectionHeader + gui ChatListItemWidget (ohne ChatTopicSection). |
| **Klassifikation** | **MIGRATE** |
| **Begründung** | Aktive Implementierung. Wird von gui/domains/operations/chat/panels/chat_navigation_panel.py importiert. Hat ui-Abhängigkeit (chat_list_item). Migration: ChatTopicSection + ChatListItemWidget (ui) nach gui verschieben; gui ChatListItemWidget erweitern (preview, context_menu_requested) oder ui-Version ersetzen. |

---

### 1.9 chat_list_item.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Einzelner Chat-Eintrag in der projektbezogenen Chat-Navigation. Titel, last_activity, optional preview. context_menu_requested-Signal. |
| **Imports** | `datetime`, `PySide6.QtWidgets`, `PySide6.QtCore` |
| **Abhängigkeiten** | Nur stdlib und PySide6. Keine app-Abhängigkeiten. |
| **Beziehung zu gui/domains/operations/chat** | Wird von ChatTopicSection (ui) genutzt. gui hat chat_list_item.py mit anderer API: kein preview, kein context_menu_requested. |
| **Klassifikation** | **MIGRATE** |
| **Begründung** | Aktive Implementierung. Wird von gui (via ChatTopicSection) indirekt genutzt. gui ChatListItemWidget ist schlanker (kein preview, kein context_menu_requested). Migration: gui ChatListItemWidget um preview und context_menu_requested erweitern oder ui-Version ersetzen. |

---

### 1.10 chat_composer_widget.py

| Feld | Inhalt |
|------|--------|
| **Zweck** | Composer-Bereich: ChatInput (dynamische Höhe, Return-to-Send), Senden-Button, Slash-Command-Hinweis. Zentrierter Container (1200px). |
| **Imports** | `os`, `app.help.tooltip_helper`, `PySide6.QtWidgets`, `PySide6.QtCore`, `PySide6.QtGui` |
| **Abhängigkeiten** | app.help. Keine gui oder ui. |
| **Beziehung zu gui/domains/operations/chat** | ChatWorkspace nutzt ChatInputPanel (einfacher: QTextEdit, Modell-Combo, Prompt-Button). ChatComposerWidget: ChatInput (QPlainTextEdit), zentrierter Container, Slash-Hinweis. |
| **Klassifikation** | **MIGRATE** |
| **Begründung** | Aktive Implementierung. Wird von gui/legacy/chat_widget und Tests genutzt. ChatWorkspace hat ChatInputPanel (anderes Design). Migration: Nach gui/domains/operations/chat/panels/ verschieben oder als Alternative zu ChatInputPanel integrieren. |

---

## 2. Klassifikation Zusammenfassung

| Datei | Klassifikation | Begründung |
|-------|----------------|------------|
| __init__.py | KEEP_TEMP | Re-Export-Hub; nach Migration auf gui-Re-Exports reduzieren |
| chat_message_widget.py | REMOVE | Reiner Re-Export, keine Logik |
| chat_item_context_menu.py | REMOVE | Reiner Re-Export, keine Logik |
| topic_actions.py | REMOVE | Reiner Re-Export, keine Logik |
| topic_editor_dialog.py | REMOVE | Reiner Re-Export, keine Logik |
| conversation_view.py | MIGRATE | Aktive Implementierung, Legacy-ChatWidget |
| chat_header_widget.py | MIGRATE | Aktive Implementierung, Legacy-ChatWidget |
| chat_topic_section.py | MIGRATE | Aktive Implementierung, gui ChatNavigationPanel |
| chat_list_item.py | MIGRATE | Aktive Implementierung, von ChatTopicSection genutzt |
| chat_composer_widget.py | MIGRATE | Aktive Implementierung, Legacy-ChatWidget |

---

## 3. Importanalyse: app.ui.chat

### 3.1 Konsumenten von app.ui.chat

| Quelle | Importierte Module | Herkunft |
|--------|-------------------|----------|
| `app/gui/legacy/chat_widget.py` | conversation_view, chat_composer_widget, chat_header_widget | gui |
| `app/gui/domains/operations/chat/panels/chat_navigation_panel.py` | chat_topic_section | gui |
| `app/ui/chat/__init__.py` | chat_composer_widget, chat_header_widget, conversation_view, chat_list_item, chat_topic_section | ui (intern) |
| `app/ui/chat/chat_topic_section.py` | chat_list_item | ui (intern) |
| `tests/ui/test_chat_ui.py` | conversation_view, chat_composer_widget, chat_header_widget | tests |
| `tests/smoke/test_basic_chat.py` | conversation_view | tests |
| `tests/regression/test_agent_delete_removes_from_list.py` | chat_header_widget | tests |
| `tests/regression/test_chat_composer_send_signal_actually_emits.py` | chat_composer_widget, ChatInput | tests |

### 3.2 Import-Matrix

| Modul | gui | ui | tests |
|-------|-----|-----|------|
| conversation_view | 1 (chat_widget) | 1 (__init__) | 2 |
| chat_composer_widget | 1 (chat_widget) | 1 (__init__) | 2 |
| chat_header_widget | 1 (chat_widget) | 1 (__init__) | 1 |
| chat_topic_section | 1 (chat_navigation_panel) | 1 (__init__) | 0 |
| chat_list_item | 0 | 2 (__init__, chat_topic_section) | 0 |

### 3.3 Gui→Ui Violations (Architektur-Guard)

| Datei | Import |
|-------|--------|
| gui/legacy/chat_widget.py | app.ui.chat.conversation_view, app.ui.chat.chat_composer_widget, app.ui.chat.chat_header_widget |
| gui/domains/operations/chat/panels/chat_navigation_panel.py | app.ui.chat.chat_topic_section |

---

## 4. Zielstruktur: app/gui/domains/operations/chat/

### 4.1 Aktuelle Struktur

```
app/gui/domains/operations/chat/
├── __init__.py
├── chat_workspace.py
└── panels/
    ├── __init__.py
    ├── chat_navigation_panel.py      # importiert app.ui.chat.chat_topic_section
    ├── chat_message_widget.py
    ├── chat_item_context_menu.py
    ├── topic_actions.py
    ├── topic_editor_dialog.py
    ├── session_explorer_panel.py     # nutzt gui ChatListItemWidget (ohne ChatTopicSection)
    ├── chat_details_panel.py
    ├── conversation_panel.py         # ChatConversationPanel (einfacher als ConversationView)
    ├── input_panel.py                # ChatInputPanel (einfacher als ChatComposerWidget)
    └── chat_list_item.py            # gui-Version (ohne preview, ohne context_menu_requested)
```

### 4.2 Vorgeschlagene Struktur nach Migration

```
app/gui/domains/operations/chat/
├── __init__.py
├── chat_workspace.py
└── panels/
    ├── __init__.py
    ├── chat_navigation_panel.py      # importiert ChatTopicSection aus gui
    ├── chat_topic_section.py        # NEU: migriert aus ui
    ├── chat_list_item.py            # gui-Version erweitern (preview, context_menu_requested)
    ├── chat_message_widget.py
    ├── chat_item_context_menu.py
    ├── topic_actions.py
    ├── topic_editor_dialog.py
    ├── session_explorer_panel.py
    ├── chat_details_panel.py
    ├── conversation_panel.py         # oder: conversation_view.py (alternativ)
    ├── input_panel.py               # oder: chat_composer_widget.py (alternativ)
    ├── conversation_view.py        # NEU: migriert aus ui (für Legacy-ChatWidget)
    ├── chat_header_widget.py       # NEU: migriert aus ui (für Legacy-ChatWidget)
    └── chat_composer_widget.py     # NEU: migriert aus ui (für Legacy-ChatWidget)
```

### 4.3 Migrationsreihenfolge (Empfehlung)

1. **chat_list_item.py (gui)** erweitern: `preview`-Parameter, `context_menu_requested`-Signal, `format_relative_time` exportieren
2. **chat_topic_section.py** nach gui migrieren; Import von gui chat_list_item
3. **chat_navigation_panel.py** umstellen: Import von `app.gui.domains.operations.chat.panels.chat_topic_section`
4. **conversation_view.py** nach gui migrieren; Import von gui chat_message_widget (bereits vorhanden)
5. **chat_header_widget.py** nach gui migrieren
6. **chat_composer_widget.py** nach gui migrieren
7. **gui/legacy/chat_widget.py** umstellen: Import von gui.panels statt ui.chat
8. **Tests** umstellen: Import von gui.panels statt ui.chat
9. **Re-Export-Dateien** (chat_message_widget, chat_item_context_menu, topic_actions, topic_editor_dialog) entfernen
10. **ui/chat/__init__.py** prüfen: Re-Exports aus gui oder entfernen

### 4.4 Parallele Implementierungen (Architektur-Regel)

- **ConversationView vs ChatConversationPanel:** ChatWorkspace nutzt ChatConversationPanel (einfacher). Legacy-ChatWidget nutzt ConversationView (bubble-basiert). Beide können parallel bleiben; Migration verschiebt nur ConversationView nach gui.
- **ChatComposerWidget vs ChatInputPanel:** ChatWorkspace nutzt ChatInputPanel. Legacy-ChatWidget nutzt ChatComposerWidget. Beide können parallel bleiben.
- **ChatListItemWidget (ui vs gui):** ui hat preview + context_menu_requested; gui hat nur Basis. ChatTopicSection erfordert ui-Features. Empfehlung: gui-Version erweitern, ui-Version entfernen.

---

## 5. Abhängigkeiten-Diagramm (vor Migration)

```
app.ui.chat
├── chat_topic_section ──► chat_list_item (ui)
├── conversation_view ──► chat_message_widget (gui)
├── chat_header_widget
├── chat_composer_widget
└── chat_list_item

gui/legacy/chat_widget
├── conversation_view (ui)
├── chat_composer_widget (ui)
└── chat_header_widget (ui)

gui/chat_navigation_panel
└── chat_topic_section (ui)
```

---

## 6. Nächste Schritte (Phase 2)

1. **Phase 2 Migration:** chat_list_item (gui) erweitern, chat_topic_section migrieren, chat_navigation_panel umstellen
2. **Phase 3 Migration:** conversation_view, chat_header_widget, chat_composer_widget migrieren
3. **Phase 4 Legacy:** chat_widget umstellen, Tests umstellen
4. **Phase 5 Cleanup:** ui/chat Re-Exports entfernen, KNOWN_GUI_UI_VIOLATIONS leeren

---

**Hinweis:** Keine Dateien verschoben, keine Imports geändert, keine Refactorings durchgeführt. Nur Analyse.
