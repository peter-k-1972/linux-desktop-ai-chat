# Chat-Kontext-Aktionen – Analyse

**Stand:** 2026-03-17  
**Ziel:** Chat von passivem Interface zu aktivem Arbeitswerkzeug erweitern.

---

## 1. Ausgangslage

Der Chat ist kontextbewusst:

- Projekt sichtbar (ContextBar)
- Chat sichtbar (ContextBar)
- Topic optional sichtbar (ContextBar)
- Kontext aktualisiert sich korrekt bei Projekt-/Chat-Wechsel

**Lücke:** Kontext ist nur Anzeige – keine Aktionen direkt aus dem Kontext heraus.

---

## 2. Identifizierte Kontext-Aktionen

### 2.1 Chat verschieben zwischen Projekten

| Aspekt | Detail |
|--------|--------|
| **Service** | ProjectService: `remove_chat_from_project(old_id, chat_id)` + `add_chat_to_project(new_id, chat_id)` |
| **Voraussetzung** | Chat muss einem Projekt zugeordnet sein ODER global sein |
| **UX** | Projekt-Auswahl-Dialog (ähnlich ProjectSwitcherDialog) |
| **Nach Aktion** | ContextBar + NavigationPanel aktualisieren; ggf. aktives Projekt wechseln |

### 2.2 Topic zuweisen/ändern

| Aspekt | Detail |
|--------|--------|
| **Service** | ChatService: `move_chat_to_topic(project_id, chat_id, topic_id)` |
| **Voraussetzung** | Chat muss Projekt haben |
| **UX** | Bereits in ChatDetailsPanel (Topic-Combo) und ChatItemContextMenu vorhanden |
| **Erweiterung** | Kontextbar: Klick auf Topic-Label → gleiche Aktion wie Details-Panel |

### 2.3 Chat umbenennen

| Aspekt | Detail |
|--------|--------|
| **Service** | ChatService: `save_chat_title(chat_id, title)` |
| **Voraussetzung** | Chat ausgewählt |
| **UX** | Bereits in ChatDetailsPanel und ChatItemContextMenu |
| **Erweiterung** | Kontextbar: Klick auf Chat-Label → Umbenennen-Dialog |

### 2.4 Neuen Chat im Kontext erstellen

| Aspekt | Detail |
|--------|--------|
| **Service** | ChatService: `create_chat_in_project(project_id, title, topic_id)` oder `create_chat(title)` |
| **Voraussetzung** | Projekt aktiv (für Projekt-Chat) oder global |
| **UX** | Bereits: "Neuer Chat" in NavigationPanel; "Neues Topic" |
| **Erweiterung** | Kontextbar: kleines "+"-Icon oder Menüpunkt "Neuer Chat hier" |

### 2.5 Kontext wechseln

| Aspekt | Detail |
|--------|--------|
| **Service** | ProjectContextManager: `set_active_project(project_id)` |
| **Voraussetzung** | — |
| **UX** | Bereits: ProjectSwitcherButton in TopBar |
| **Erweiterung** | Kontextbar: Klick auf Projekt-Label → ProjectSwitcherDialog öffnen |

---

## 3. UI-Integration (minimal-invasiv)

### 3.1 Option A: Kontextbar erweitern (empfohlen)

- **Projekt-Label:** Klickbar → ProjectSwitcherDialog öffnen
- **Chat-Label:** Klickbar → Umbenennen-Dialog (wie Details-Panel)
- **Topic-Label:** Klickbar → Topic-Auswahl (wie Details-Panel Combo)
- **Aktions-Button:** Kleines Menü-Icon (⋮) rechts in der Bar → Kontextmenü mit allen Aktionen

**Vorteil:** Keine Überladung, Nutzer erwartet Klickbarkeit bei Labels.

### 3.2 Option B: Kontextmenü auf Kontextbar

- Rechtsklick auf die gesamte Bar → Menü mit: Projekt wechseln, Chat umbenennen, Topic ändern, Neuer Chat, Chat verschieben

**Vorteil:** Keine sichtbaren Änderungen, nur bei Bedarf.

### 3.3 Option C: Kleine Aktionsbuttons

- Zusätzliche Icons (Stift, Pfeil, etc.) neben den Labels

**Nachteil:** Kann überladen wirken.

### 3.4 Empfehlung

**Kombination A + B:**

1. Labels klickbar machen (Projekt → Switcher, Chat → Umbenennen, Topic → Topic-Combo/Dialog)
2. Rechtsklick auf Bar → Kontextmenü mit erweiterten Aktionen (Chat verschieben, Neuer Chat)
3. Kein zusätzliches Menü-Icon – Reduktion der visuellen Elemente

---

## 4. Service-Anbindung

### 4.1 Bestehende Services (keine neue Schicht)

| Aktion | Service | Methode |
|--------|---------|---------|
| Chat verschieben | ProjectService | `remove_chat_from_project` + `add_chat_to_project` |
| Topic ändern | ChatService | `move_chat_to_topic` |
| Chat umbenennen | ChatService | `save_chat_title` |
| Neuer Chat | ChatService | `create_chat_in_project` / `create_chat` |
| Projekt wechseln | ProjectContextManager | `set_active_project` (via ProjectSwitcherDialog) |

### 4.2 Erweiterung ProjectService (optional)

Für "Chat verschieben" könnte eine Hilfsmethode sinnvoll sein:

```python
def move_chat_to_project(self, chat_id: int, target_project_id: int) -> None:
    """Verschiebt Chat von aktuellem Projekt zu target_project."""
    old_id = self.get_project_of_chat(chat_id)
    if old_id:
        self.remove_chat_from_project(old_id, chat_id)
    self.add_chat_to_project(target_project_id, chat_id)
```

**Hinweis:** Wird in UI-Layer aufgerufen; ProjectService hat bereits die nötigen Methoden. Eine `move_chat_to_project`-Methode vereinfacht die Logik und stellt Atomarität sicher.

---

## 5. Konsistenz nach Aktionen

| Aktion | ContextBar | NavigationPanel | DetailsPanel |
|--------|------------|-----------------|--------------|
| Projekt wechseln | ✓ (via project_context_changed) | ✓ (subscribe) | ✓ (refresh) |
| Chat verschieben | ✓ refresh | ✓ refresh | ✓ refresh |
| Topic ändern | ✓ refresh | ✓ refresh | ✓ refresh |
| Chat umbenennen | ✓ refresh | ✓ refresh | ✓ refresh |
| Neuer Chat | ✓ refresh | ✓ refresh | ✓ refresh |

**Implementierung:** Alle Aktionen rufen `on_action`-Callback auf, der in ChatWorkspace `_session_explorer.refresh()` und `_refresh_context_bar()` auslöst. Bereits etabliert in `_on_details_chat_updated`.

---

## 6. Kontext-Leaks vermeiden

- **Chat verschieben:** Nach Verschiebung in anderes Projekt: Wenn aktuelles Projekt ≠ Zielprojekt, Chat verschwindet aus NavigationPanel. ContextBar zeigt dann Zielprojekt ODER aktives Projekt – je nach UX-Entscheidung.
- **Empfehlung:** Nach Verschieben in anderes Projekt → aktives Projekt auf Zielprojekt wechseln (damit Nutzer den Chat weiter sieht).
- **Neuer Chat:** Immer im Kontext des aktiven Projekts erstellen (bereits so implementiert).

---

## 7. Zusammenfassung

| Aktion | Priorität | Service | UI-Ort |
|--------|-----------|---------|--------|
| Projekt wechseln (Klick) | Hoch | ProjectContextManager | Kontextbar Projekt-Label |
| Chat umbenennen (Klick) | Hoch | ChatService | Kontextbar Chat-Label |
| Topic ändern (Klick) | Hoch | ChatService | Kontextbar Topic-Label |
| Chat verschieben | Mittel | ProjectService | Kontextmenü Kontextbar |
| Neuer Chat im Kontext | Mittel | ChatService | Kontextmenü / bereits NavPanel |

**Keine neue Architektur, keine KI-Erweiterung – reine Nutzung von Projekt-/Chat-/Topic-Kontext und bestehenden Services.**
