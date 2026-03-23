# QA-Checkliste: Projects-Workspace (Operations → Projekte)

Zweck: **schnelle, reproduzierbare** Prüfung der zentralen Projektverwaltung nach Änderungen am Workspace, an `ProjectService`/`DatabaseManager` oder an Policy/Löschlogik.

**Automatisierte Smoke-Abdeckung (DB/Service/UI-Import):** `tests/smoke/test_projects_workspace_smoke.py`  
**Tiefere Delete-Semantik (SQLite):** `tests/test_project_delete_semantics.py`

---

## Kritische Pfade (Kurz)

| Pfad | Erwartung |
|------|-----------|
| Anlegen → Liste | Eintrag sichtbar, Auswahl setzt Overview + Inspector |
| Bearbeiten → Persistenz | `get_project` / erneutes Öffnen des Dialogs zeigt gespeicherte Werte |
| Aktives Projekt bearbeiten | PCM + TopBar/Breadcrumb zeigen aktualisierten Namen |
| Löschen | Bestätigungstext = reale Semantik; DB-Zeile weg; Kontext ggf. leer |
| Kennzahlen | Gleiche Labels/Zahlen in Overview-Stats und Inspector (gleiche Service-Aufrufe) |

---

## 1. Projekt anlegen

- [ ] **Neues Projekt** anlegen (Name Pflicht, Beschreibung optional).
- [ ] Projekt **erscheint in der Liste** mit korrektem Namen.
- [ ] Nach Auswahl: **Kennzahlen** sind plausibel initial (z. B. Chats/Quellen/Prompts/Workflows/Datei-Links ≥ 0, meist 0).
- [ ] **Auswahl** wechselt Overview und Inspector ohne Fehler.

---

## 2. Projekt bearbeiten

- [ ] **Name** ändern → speichern.
- [ ] **Beschreibung** ändern → speichern.
- [ ] **Status** ändern → speichern.
- [ ] **Default Context Policy** auf einen bekannten Wert setzen → speichern.
- [ ] Policy auf **App-Standard** (NULL in DB) setzen → speichern.

**Verifizieren:**

- [ ] **Header** (Name, Beschreibung, Status, Policy-Zeile) aktualisiert.
- [ ] **Inspector** zeigt dieselben Texte/Zahlen wie der Overview-Bereich (kein Widerspruch).
- [ ] **Liste** zeigt den **neuen Namen** nach Refresh/Auswahl.

---

## 3. Aktives Projekt bearbeiten

- [ ] Projekt **als aktiv setzen** (Schaltfläche im Overview).
- [ ] **Bearbeiten** (Name o. ä.) → speichern.
- [ ] **TopBar / Breadcrumb** zeigen den neuen Namen (PCM lädt aus DB).
- [ ] Kein „hängender“ alter Projektname im aktiven Kontext.

---

## 4. Projekt löschen

- [ ] **Projekt löschen** öffnet Bestätigungsdialog.
- [ ] **Informations-Text** beschreibt ehrlich: Chats bleiben / entkoppelt; Prompts/Agents/Workflows **globalisiert**; Knowledge-Raum der App entfernt; **keine** automatische Löschung physischer Quelldateien; DB-Links (z. B. `project_files`) weg; aktives Projekt wird ggf. **geleert**.

**Nach Bestätigung:**

- [ ] Projekt **nicht mehr in der Liste**.
- [ ] **Overview** leer oder **nächstes** Projekt (wenn noch vorhanden).
- [ ] War das Projekt **aktiv**, ist danach **kein** aktives Projekt gesetzt (oder konsistent mit App-Regeln).

---

## 5. Kennzahlen

Prüfen, dass die **Beschriftungen** zur Bedeutung passen:

- [ ] **Chats** – zugeordnete Chats des Projekts.
- [ ] **Knowledge-Quellen** – RAG-Quellen des Projekts (nicht gleich Dateitabelle).
- [ ] **Prompts** – projektbezählte Prompts.
- [ ] **Workflows (Projekt)** – nur **projektgebundene** Workflows (ohne globale).
- [ ] **Datei-Links (DB)** – Einträge in `project_files`, **nicht** „alle Dateien auf der Platte“.

**Explizit:**

- [ ] **Knowledge-Quellen ≠ Datei-Links** (Zahlen dürfen unterschiedlich sein; Labels nicht vertauschen).

---

## 6. Listen-Refresh / Auswahl

- [ ] Nach Aktionen, die die Liste neu laden (z. B. externer Refresh, Filterwechsel), bleibt die **Auswahl nach `project_id`** erhalten, wenn das Projekt noch existiert.
- [ ] Nach **Löschen** des ausgewählten Projekts: sinnvoller Folgezustand (leer oder anderes Projekt), **kein** stehengebliebener Overview für gelöschte ID.

---

## 7. Edge Cases

- [ ] **Letztes Projekt löschen:** leere Liste, Overview ohne Projekt, kein Crash.
- [ ] Projekt mit **Workflows / Prompts / Agents / Knowledge** löschen: Inhalte **nicht** verworfen, wo die Semantik **Globalisierung** vorsieht; Chats **ohne** Projektbindung; Knowledge-**Space** der App entfernt (physische Dateien unangetastet – nur prüfen, dass die App nicht behauptet, alles sei „von der Platte“ weg).

**Referenz-Automatisierung:** `tests/test_project_delete_semantics.py` für SQLite-Transaktion und Zuordnungen.

---

## Bekannte Risiken / Grenzen

1. **Policy-Werte außerhalb `ChatContextPolicy`**  
   In der DB gespeicherte unbekannte Strings: Dialog zeigt einen **Fallback-Eintrag** („Gespeichert: …“); Caption im Header kann „Gespeichert (unklar)“ nutzen.

2. **Knowledge-Space-Löschung**  
   Fehler beim Entfernen des RAG-Unterordners werden **nur geloggt**; UI meldet trotzdem erfolgreiches Projekt-Löschen aus DB-Sicht. Manuell nur bei Bedarf Logs prüfen.

3. **Workflow-Zähler**  
   Zählt **nur** Workflows mit Projektzuordnung zu dieser `project_id`, **ohne** globale Workflows.

4. **GUI E2E**  
   Vollständige Klickpfade durch PySide6 sind **nicht** in der Smoke-Suite abgebildet; obige Checkliste und gezielte manuelle Läufe bleiben **bewusst** Teil der Freigabe.

---

## Ausführung (Dev)

```bash
# Smoke nur Projects-Workspace (Service/DB/Konstanten/UI-Instanziierung)
pytest tests/smoke/test_projects_workspace_smoke.py -q -m smoke

# Delete-Semantik (tiefer)
pytest tests/test_project_delete_semantics.py -q
```
