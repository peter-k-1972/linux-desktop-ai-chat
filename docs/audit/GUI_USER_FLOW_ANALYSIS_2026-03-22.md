# GUI-User-Flow-Analyse — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** `ChatWorkspace`, `navigation_registry.py`, `USER_GUIDE.md` / `help/`-Struktur (stichprobenartig), Control-Center-Nav, Settings-Kategorien (`settings_workspace.py`).

---

## Flow 1: Chat starten

| Schritt | Aktion | Ort |
|---------|--------|-----|
| 1 | Sidebar: Bereich **WORKSPACE** aufklappen (falls zu) | `NavigationSidebar` |
| 2 | **Chat** wählen | `operations_chat` |
| 3 | Session wählen oder neue Session anlegen | `ChatNavigationPanel` |
| 4 | Nachricht eingeben, senden | `ChatInputPanel` |

**Probleme**

- Erste Nutzung: Sektion WORKSPACE kann **eingeklappt** sein — **Discoverability** von „Chat“ nicht maximal.  
- **Projektkontext:** Wechsel über TopBar oder Kontextleiste/Dialog — zusätzlicher mentaler Schritt.

**Verbesserungen**

- Dashboard-**Deep-Link** oder prominente Kachel „Zu Chat“ (Konzept).  
- Beim ersten Start **WORKSPACE** standardmäßig aufgeklappt erwägen (Policy-Frage).

---

## Flow 2: Modell wechseln

| Schritt | Aktion | Ort |
|---------|--------|-----|
| A (im Chat) | Modell in **Chat-Eingabe-/Kopfbereich** wählen | `ChatInputPanel` / zugehörige Widgets |
| B (global) | **SYSTEM → Models** | Control Center `cc_models` |
| C (Defaults) | **SETTINGS → AI / Models** | `settings_ai_models` |

**Probleme**

- **Drei** plausible Orte — ohne klare **Hilfe** „wo Default, wo pro Nachricht“ entsteht **Kontextwechsel**.  
- Control-Center-Labels **englisch**, Settings-Nav gemischt — **Bruch** beim Wechsel.

**Verbesserungen**

- Kurzer **Hilfetext** in Settings und Control Center: „Steuert Standard für neue Chats“ vs. „Laufzeit im Chat“.  
- Begriffe in **einer** Sprache.

---

## Flow 3: Kontext konfigurieren

| Schritt | Aktion | Ort |
|---------|--------|-----|
| 1 | Im Chat: **Kontextleiste** (Projekt, Chat, Topic) | `ChatContextBar` |
| 2 | Kontextmenü / Feineinstellungen | `chat_item_context_menu` / Policies |
| 3 | **Globale** Schalter: Settings **AI / Models** oder kontextbezogene Kategorien | `SettingsWorkspace` |

**Probleme**

- **Split** zwischen **Laufzeit-Kontext** (Chat) und **persistierten Defaults** (Settings) — **sachlich richtig**, für Nutzer **anspruchsvoll**.  
- Fehler in Dialogpfaden können **still** scheitern (`except: pass` in Chat-Workspace bei Projekt-Switch — aus `chat_workspace.py` Zeilen 153–154, 162–163).

**Verbesserungen**

- Sichtbares **Feedback** bei Fehlern beim Projektwechsel.  
- In-App-Hilfe **ein** durchgängiger Artikel „Kontext: Chat vs. Settings“ (`help/settings/settings_chat_context.md` existiert — **Auffindbarkeit** über F1 stärken).

---

## Flow 4: Workflow ausführen

| Schritt | Aktion | Ort |
|---------|--------|-----|
| 1 | **WORKSPACE → Workflows** | `operations_workflows` |
| 2 | Editor / Runs / **Geplant** (laut Doku) | `WorkflowsWorkspace` |

**Probleme**

- Alternativpfad **Workbench** mit Workflow-Builder — **zweites** mentales Modell (Audit).  
- Nutzer, die Workbench kennen, erwarten ggf. **dieselbe** Inspector-Funktionalität wie in der Shell — **Stubs** erzeugen Frustration.

**Verbesserungen**

- Produktkommunikation: **eine** empfohlene Oberfläche für DAG/Runs.  
- Workbench nur als „Experimentell“ kennzeichnen, bis Parität besteht.

---

## Flow 5: Projekt bearbeiten

| Schritt | Aktion | Ort |
|---------|--------|-----|
| 1 | **PROJECT → Projekte** oder TopBar **Project Switcher** | `operations_projects` / `ProjectSwitcherButton` |
| 2 | Liste, Dialoge bearbeiten | `ProjectsWorkspace` |

**Probleme**

- **Settings → Project** ist laut README eher **Lesensansicht** — Nutzer könnte **Bearbeitung** dort erwarten.

**Verbesserungen**

- In Settings **explizit:** „Verwaltung unter Operations → Projekte“ (Copy).

---

## Flow 6: Datei verwalten

| Schritt | Aktion | Ort |
|---------|--------|-----|
| — | **Kein** dedizierter globaler „Dateimanager“-Workspace in der Sidebar-Registry ersichtlich | — |

**Probleme**

- „Dateien verwalten“ ist **nicht** als zentraler Nav-Punkt modelliert; eher **Knowledge**/RAG und **Prompt**-Pfade oder Legacy/Workbench (`FileViewerCanvas` — Nebenpfad).

**Verbesserungen**

- Produkt klären: Wenn „Dateien“ = **Wissensquellen**, in **Knowledge**-Onboarding führen; wenn allgemeiner Dateizugriff gewünscht — **eigenes** Zielbild definieren (außerhalb dieser Review-Implementierung).

---

## Zusammenfassung Reibung

| Flow | Reibung (hoch → niedrig) |
|------|---------------------------|
| Chat starten | Niedrig–mittel |
| Modell wechseln | **Hoch** (mehrere Orte) |
| Kontext konfigurieren | **Hoch** (Chat vs. Settings + stiller Fehlerpfad) |
| Workflow | Mittel (Dual-Pfad Workbench) |
| Projekt | Mittel (Settings-Erwartung) |
| Dateien | **Unklar / fragmentiert** |

---

*Ende User-Flow-Analyse.*
