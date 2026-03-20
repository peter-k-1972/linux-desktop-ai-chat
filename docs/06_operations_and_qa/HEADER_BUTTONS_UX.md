# Header-Buttons (TopBar) – UX-Entscheidungen

## Status-Button

### Ursache
- Kein Signal/Slot verbunden – `action_status` hatte kein `triggered.connect`
- Kein Ziel-Panel oder Overlay definiert

### Gewählter Fix
- **Verdrahtung:** `status_requested`-Signal ergänzt, mit `triggered.connect` verbunden
- **Ziel:** Öffnet Runtime / Debug (Agent-Status, Agent Activity, System Graph)
- **Tooltip:** „Runtime / Debug – Agent-Status, Aktivität“

### UX-Begründung
Runtime/Debug enthält die relevanten Status-Informationen (Agent-Status, Aktivität). Der Button führt damit eine sinnvolle Aktion aus statt wirkungslos zu bleiben.

---

## Suche/Befehle-Button

### Ursache
- Button war als „Suche“ beschriftet, öffnete aber nur die Command Palette
- Command Palette ist eine **Befehlssuche** (Navigation, Theme, etc.), keine Inhalts-Suche (Chats, Prompts)

### Gewählter Fix
- **Label:** „Suche“ → „Befehle“
- **Tooltip:** „Command Palette – Befehle suchen (Ctrl+Shift+P)“

### UX-Begründung
Die Bezeichnung „Befehle“ macht klar, dass Befehle gesucht werden, nicht App-Inhalte. Keine irreführende Erwartung an eine globale Inhalts-Suche.

---

## Betroffene Dateien

| Datei | Änderung |
|-------|----------|
| `app/gui/shell/top_bar.py` | Status: `status_requested`-Signal, Verdrahtung; Suche: Label „Befehle“, Tooltip angepasst |
| `app/gui/shell/main_window.py` | `status_requested` → `show_area(RUNTIME_DEBUG)` |
