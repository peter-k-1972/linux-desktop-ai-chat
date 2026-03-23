# Manuelle Release-Checkliste – Linux Desktop Chat

Kurze, wiederholbare Prüfung vor einer Freigabe. Voraussetzung: `pip install -r requirements.txt`, optional Ollama mit mindestens einem Modell.

## Start & Navigation

1. App starten: `python -m app` (oder `main.py` / `run_gui_shell.py`).
2. Sidebar: alle Hauptbereiche öffnen (PROJECT: Systemübersicht, Projekte; Operations-Unterpunkte; Control Center; QA; Runtime/Debug; Settings) — kein Crash, kein leeres Fenster ohne Rahmen.
3. Workspace-Graph (falls über Menü/Palette erreichbar): Knoten wählen, „Workspace öffnen“ und „Hilfe öffnen“ prüfen.

## Zentrale Pfade

| Pfad | Prüfpunkte |
|------|-------------|
| **Chat** | Session anlegen/wählen, Nachricht senden (mit laufendem Ollama: Antwort; ohne: verständliche Fehlermeldung). Details/Navigation/Pin nachvollziehbar. |
| **Prompt Studio** | Prompt laden oder anlegen, speichern; Vorschau/Test-Lab ohne irreführende „fertig“-Versprechen bei fehlendem Modell. |
| **Knowledge** | Collections/Sources/Status; leerer Index ehrlich kommuniziert; Collection-Dialoge deutsch konsistent. |
| **Agent Tasks** | Agent wählen, Task starten; Ergebnisbereich aktualisiert sich; ohne Projekt ggf. leere Liste mit sinnvollem Hinweis. |
| **Projekte** | Projekt anlegen/aktiv setzen; Settings → Project zeigt aktives Projekt. |
| **Workflows** | Workflow anlegen oder laden, validieren, Test-Run; Run erscheint in Liste; Canvas/Inspector stimmig. |
| **Hilfe** | Hilfefenster öffnen, Stichwortsuche, Kategoriewechsel; **Semantische Doku-Suche**: ohne Index Hinweis im Panel, mit Index Suche ausführbar. |
| **Control Center** | Models, Providers, Agents, Tools, Data Stores — keine harten Crashes; Tools/Data Stores als Konfig-Snapshot verstanden (keine externe Registry). |

## Regression kurz

- Zwischen 3–4 Workspaces wechseln: Inspector/Details keinen „alten“ Inhalt von vorherigem Workspace zeigen (stichprobenartig).
- Settings speichern, App neu starten: zentrale Schalter (z. B. Theme, Kontextmodus) bleiben erhalten.

## Automatisierte Smoke-Tests (lokal)

```bash
python -m pytest tests/smoke/ -q
```

## Bekannte Grenzen (kein Blocker, aber ehrlich)

- Semantische Hilfe-Suche und RAG benötigen gebaute Chroma-Indizes (`tools/build_doc_embeddings.py` bzw. RAG-Indexierung).
- Einige Runtime-Debug-Flächen sind diagnostisch; nicht jede Kachel muss produktionsdaten haben.
- Pipeline-Executor-Platzhalter (Comfy/Media) sind bewusst nicht produktiv — nur prüfen, dass die UI das nicht als „fertiges Produkt“ verkauft.
