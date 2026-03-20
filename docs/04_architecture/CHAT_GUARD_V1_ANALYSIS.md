# Chat Guard v1 – Analyse

**Stand:** 2026-03-17  
**Ziel:** Schlanker Chatwächter zwischen User-Input und Modellaufruf.

---

## 1. Aktueller Anfragefluss

### 1.1 User-Input-Pfad

```
ChatInputPanel (QTextEdit)
    → User tippt, Enter oder Senden
    → send_requested.emit(text)
    → ChatWorkspace._on_send_requested(text)
    → ChatWorkspace._run_send(text)
```

### 1.2 Chat-Lauf (ChatWorkspace._run_send)

```
1. chat_svc.save_message(chat_id, "user", text)
2. messages = chat_svc.load_chat(chat_id)
3. api_messages = [{"role": row[0], "content": row[1]} for row in messages]
4. chat_svc.chat(model, api_messages, temperature, max_tokens, stream=True)
5. ChatService.chat → ollama_client.chat(model, messages, ...)
6. Stream-Chunks → update_last_assistant → save_message(assistant, ...)
```

### 1.3 Metadaten

- **DB messages:** role, content, timestamp, model, agent, completion_status
- **Kein System-Prompt** im Standard-Chatfluss – nur user/assistant
- **Prompt Studio:** Prompts können als System/User eingefügt werden, aber nicht im Standardpfad

### 1.4 Agenten-/Modellpfade

- **AgentTaskRunner:** Baut eigene messages mit agent.system_prompt, ruft orchestrator.chat
- **ChatWorkspace:** Nutzt ChatService direkt, kein Agent
- **RAG:** augment_prompt erweitert User-Prompt mit Kontext – separater Pfad

---

## 2. Geeigneter Integrationspunkt

**Empfehlung:** ChatService.chat()

**Begründung:**
- GUI bleibt dumm – keine Guard-Logik in ChatWorkspace
- ChatService ist der zentrale Eintritt für Modellaufrufe
- Vor dem ollama_client.chat() kann der Guard die messages inspizieren und anreichern
- Spätere Agenten-Integration: AgentTaskRunner nutzt ggf. ChatService – Guard greift automatisch

**Alternativen (verworfen):**
- ChatWorkspace: Würde Guard-Logik in GUI-Schicht ziehen
- OllamaClient: Zu niedrig, Provider-spezifisch
- Separater Wrapper um ChatService: Zusätzliche Indirektion ohne Nutzen

**Konkrete Integration:**
```python
# ChatService.chat() – vor ollama_client.chat()
last_user_content = _get_last_user_content(messages)
guard_result = chat_guard_service.assess(last_user_content)
messages = chat_guard_service.apply(messages, guard_result)
async for chunk in self._infra.ollama_client.chat(model, messages, ...):
    yield chunk
```

---

## 3. Entscheidungen vor Modellaufruf

| Entscheidung | Machbar v1 | Beschreibung |
|--------------|------------|--------------|
| Intent klassifizieren | Ja | Heuristisch: chat, command, formal_reasoning, coding, knowledge_query, possibly_ambiguous |
| Risk-Flags setzen | Ja | command_unrecognized, attribution_risk, mismatch_risk |
| Prompt härten | Ja | System-Nachricht oder User-Prefix je nach Intent/Risk |
| Modell-Routing | Vorbereitung | routing_hint setzen, aber kein Multi-Model-Switch in v1 |
| Anfrage blockieren | Nein v1 | Immer durchlassen, nur härten |

---

## 4. Heuristisch realistisch machbar (v1)

- **Slash-Commands:** /think, /agent, /tool etc. – Regex/Keyword
- **Formale Fragen:** Beweis, Axiom, Definition, logisch, mathematisch – Keyword
- **Coding:** Python, Code, Klasse, Funktion, Debug, Stacktrace – Keyword
- **Knowledge/Attribution:** von Goethe, wer schrieb, Gedicht, Autor, Werk – Keyword
- **Ambiguität:** Kombination z.B. "Wer schrieb X von Y?" – Mismatch-Risiko-Flag
- **Prompt-Härtung:** Kurze, feste Texte je Intent/Risk

---

## 5. Bewusst NICHT Teil von v1

- Vollständiges Agenten-Routing
- Wissensdatenbank für Autor/Werk-Prüfung
- Automatisches Retry bei Mismatch
- Perfekte KI-Intent-Erkennung
- Blockierung von Anfragen
- UI-Anzeige von Intent/Risk (nur intern/Debug)
- Schwere ML-Klassifikation
