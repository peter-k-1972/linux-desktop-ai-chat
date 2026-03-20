---
id: troubleshooting
title: Fehlerbehebung
category: troubleshooting
tags: [fehler, ollama, rag, chromadb]
related: [knowledge_overview, settings_overview]
order: 10
---

# Fehlerbehebung

## Ollama nicht erreichbar

**Symptom**: Statusleiste zeigt „Ollama: offline“

**Lösung**:
1. Ollama starten: `ollama serve`
2. Prüfen: `curl http://localhost:11434/api/tags`
3. Firewall/Port 11434 prüfen

## Keine Modelle sichtbar

**Symptom**: Modell-Dropdown leer

**Lösung**:
1. Modell laden: `ollama pull qwen2.5`
2. Anwendung neu starten
3. Einstellungen → Modell prüfen

## RAG liefert keine Ergebnisse

**Symptom**: RAG aktiv, aber kein Kontext

**Lösung**:
1. Dokumente indexieren: `python scripts/index_rag.py --space default ./docs`
2. `nomic-embed-text` installieren: `ollama pull nomic-embed-text`
3. Space in Einstellungen prüfen (default, documentation, …)
4. Top-K erhöhen (z.B. 10)

## Cloud-Eskalation funktioniert nicht

**Symptom**: Cloud-Checkbox aktiv, aber keine Cloud-Modelle

**Lösung**:
1. OLLAMA_API_KEY in Einstellungen oder .env setzen
2. API-Key bei Ollama Cloud gültig prüfen
3. cloud_via_local: ggf. deaktivieren wenn direkt Cloud genutzt werden soll

## Thinking-Modus-Probleme

**Symptom**: Antworten enthalten „Thinking-Daten“ oder Platzhalter

**Lösung**:
1. think_mode auf „off“ setzen (Einstellungen oder Header)
2. retry_without_thinking ist standardmäßig aktiv – prüfen ob Fehler auftreten
3. Modell wechseln (nicht alle unterstützen Thinking)

## Agenten werden nicht geladen

**Symptom**: Agent-Dropdown leer oder fehlerhaft

**Lösung**:
1. Agenten verwalten öffnen – Seed-Agenten werden automatisch angelegt
2. Datenbank prüfen (chat_history.db, Agent-Tabellen)
3. Anwendung neu starten

## Prompts speichern schlägt fehl

**Symptom**: Prompt kann nicht gespeichert werden

**Lösung**:
1. prompt_storage_type prüfen (database vs. directory)
2. Bei directory: Pfad existiert und ist beschreibbar?
3. SQLite-Datei nicht beschädigt?

## ChromaDB-Fehler (RAG)

**Symptom**: Fehler beim RAG-Indexieren oder Abfragen

**Lösung**:
1. chromadb installieren: `pip install chromadb`
2. ChromaDB-Datenverzeichnis prüfen (Standard: ./chroma_db)
3. Bei Korruption: Verzeichnis löschen und neu indexieren
