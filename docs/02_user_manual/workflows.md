# Workflows

## Übersicht

Das System unterstützt mehrere Workflow-Typen:

## 1. Standard-Chat

```
User → Modell-Router → Orchestrator → Provider → LLM → Stream → UI
```

## 2. RAG-Chat

```
User → RAGService.augment_if_enabled() → Retriever → Context
    → Erweiterter Prompt → LLM → Stream → UI
```

## 3. Research-Workflow

```
User → Planner (qwen2.5) → RAG Retriever → LLM (gpt-oss)
    → Critic (mistral) → Finale Antwort
```

Aktivierung: Rolle „Research“ oder `/research`

## 4. Delegation-Workflow

```
User → /delegate <Anfrage>
    → Task Planner → Task Graph
    → Delegation Engine → Agent-Zuordnung
    → Execution Engine → Task-Ausführung
    → Aggregierte Antwort
```

## 5. Self-Improving-Workflow

```
LLM-Antwort → Knowledge Extractor → Validator → Vector DB (Space: self_improving)
```

Aktivierung: Checkbox „Self-Improve“

## Task Graph

- **Task**: Beschreibung, Status, zugewiesener Agent
- **TaskGraph**: DAG von Tasks mit Abhängigkeiten
- **Execution Engine**: Führt Tasks in Reihenfolge aus, sammelt Ergebnisse
