# Chat-Kontext-Injection – Analyse

**Stand:** 2026-03-17  
**Ziel:** Kontext (Projekt, Chat, Topic) aktiv und promptwirksam in den Chat-Anfragefluss integrieren.

---

## 1. Aktueller Anfragefluss

### 1.1 Sendepfad (ChatWorkspace → Modell)

```
ChatWorkspace._run_send(text)
    → messages = chat_svc.load_chat(chat_id)  # [(role, content), ...]
    → api_messages = [{"role": r, "content": c} for r, c in ...]
    → chat_svc.chat(model, api_messages, chat_id=chat_id, ...)
        → _apply_chat_guard(messages)     # optional: prepend system hint
        → _inject_chat_context(messages, chat_id)  # Kontext-Injection
        → ollama_client.chat(model, messages, ...)
```

### 1.2 Model-/Provider-Aufrufkette

| Schicht | Komponente | Verantwortung |
|---------|------------|---------------|
| GUI | ChatWorkspace | Sendet Request, übergibt chat_id |
| Service | ChatService.chat() | Chat Guard, Kontext-Injection, Delegation |
| Infra | ollama_client | HTTP-Request an Ollama API |

**Keine Provider-spezifische Logik** in der Kontext-Injection – der Kontext ist reiner Message-Inhalt.

### 1.3 System-Prompt-Erzeugung

| Ort | Quelle | Inhalt |
|-----|--------|--------|
| ChatGuardService | GuardResult.system_hint | Intent-Hints (formal, coding, knowledge) |
| **Kontext-Injection** | ChatRequestContext | Projekt, Chat, Topic |
| AgentTaskRunner | agent.system_prompt | Agent-Prompt (kein chat_id) |

**Reihenfolge in finaler Message-Liste:** Kontext-Block → ggf. Chat-Guard-Hint → user/assistant messages

### 1.4 Vorhandene Message-Metadaten

- Standard-Format: `{"role": "user"|"assistant"|"system", "content": "..."}`
- Keine zusätzlichen Metadaten im Provider-Payload – Kontext wird als System-Nachricht transportiert

---

## 2. Geeigneter Integrationspunkt

**Gewählt:** ChatService.chat() – nach Chat Guard, vor ollama_client.

**Begründung:**
- Zentrale Stelle für alle Chat-Requests
- Keine UI-Abhängigkeit (chat_id kommt von Workspace, Kontext wird aus Services gebaut)
- Kein Provider-Leak (Ollama/Cloud-agnostisch)
- Saubere Merge-Logik mit Chat Guard

---

## 3. Kontextdaten – Quellen und Verfügbarkeit

| Feld | Quelle | Methode | Verfügbar |
|------|--------|---------|-----------|
| project_id | ProjectService | get_project_of_chat(chat_id) | Immer (oder None) |
| project_name | ProjectService | get_project(project_id).name | Bei Projekt |
| chat_id | Parameter | — | Immer |
| chat_title | ChatService | get_chat_info(chat_id).title | Immer |
| topic_id | ChatService | get_chat_info(chat_id).topic_id | Optional |
| topic_name | ChatService | get_chat_info(chat_id).topic_name | Optional |
| is_global_chat | Abgeleitet | project_id is None | Immer |

**Kontextquelle:** ProjectContextManager, ChatService, ProjectService – keine UI-Texte.

---

## 4. Sinnvoll promptwirksame Kontexte

| Kontext | Promptwirksam | Begründung |
|---------|---------------|------------|
| Projektname | Ja | Modell kann thematisch einordnen |
| Chat-Titel | Ja | Modell kennt Gesprächskontext |
| Topic-Name | Ja (optional) | Feine Unterteilung innerhalb Projekt |
| Projekt-ID / Chat-ID | Nein (intern) | Nur für Systemlogik, nicht für Modell |

---

## 5. Risiken und Vermeidung

| Risiko | Vermeidung |
|--------|------------|
| **Duplikation** | Kontext aus Services, nicht aus UI – eine Wahrheit |
| **UI-Abhängigkeit** | Kein Import von GUI-Modulen in context.py |
| **Provider-Leakage** | Kontext als generische System-Nachricht, kein Ollama-spezifischer Code |
| **Kaputte Fragmente** | is_empty()-Prüfung, _should_inject_context, keine leeren Blöcke |
| **Überladene Prompts** | Kurzes Format, nur relevante Zeilen (Topic weglassen wenn leer) |

---

## 6. Kontextobjekt (ChatRequestContext)

```python
@dataclass
class ChatRequestContext:
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    is_global_chat: bool = False
```

**Format für System-Prompt (nüchtern, kurz):**
```
Kontext:
- Projekt: XYZ
- Chat: Debug Session
- Topic: API
```

Bei globalen Chats: `- Projekt: (globale Chats)`  
Bei fehlendem Topic: Topic-Zeile weggelassen.

---

## 7. Aktivierungslogik

| Bedingung | Injektion |
|-----------|-----------|
| chat_id gesetzt | Prüfen |
| chat_title vorhanden | Ja (mindestens) |
| chat_title fehlt | Nein |
| Projekt fehlt (global) | Ja, mit "Projekt: (globale Chats)" |
| Topic fehlt | Ja, Topic-Zeile weggelassen |
| Leere/unvollständige Daten | Robust, keine kaputten Fragmente |

---

## 8. Debug / Transparenz

- **DEBUG-Log:** project, chat, topic, is_global bei Injektion
- Kein großes Logging-Feuerwerk
- Später erweiterbar: Runtime/Debug-Panel könnte injizierten Kontext anzeigen
