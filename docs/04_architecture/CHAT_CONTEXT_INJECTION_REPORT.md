# Chat-Kontext-Injection – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Chat kontextsensitiv machen – Projekt-/Chat-/Topic-Kontext aktiv und promptwirksam im Modell-Anfragefluss.

---

## 1. Analysierter Anfragefluss

```
ChatWorkspace._run_send(text)
    → chat_svc.load_chat(chat_id)
    → chat_svc.chat(model, api_messages, chat_id=chat_id, ...)
        → _apply_chat_guard(messages)
        → _inject_chat_context(messages, chat_id)
        → ollama_client.chat(model, messages, ...)
```

**Dokument:** `docs/04_architecture/CHAT_CONTEXT_INJECTION_ANALYSIS.md`

---

## 2. Gewähltes Kontextobjekt

**ChatRequestContext** (`app/chat/context.py`)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| project_id | Optional[int] | Projekt-ID (intern) |
| project_name | Optional[str] | Anzeigename |
| chat_id | Optional[int] | Chat-ID |
| chat_title | Optional[str] | Chat-Titel |
| topic_id | Optional[int] | Topic-ID (optional) |
| topic_name | Optional[str] | Topic-Name (optional) |
| is_global_chat | bool | True wenn kein Projekt |

Klein gehalten, klar als Request-/Conversation-Kontext gedacht. Kein Monsterobjekt.

---

## 3. Integrationspunkt

**ChatService.chat()** – nach Chat Guard, vor ollama_client.

- Optionaler Parameter `chat_id`
- Bei chat_id: `_inject_chat_context(messages, chat_id)`
- Rückwärtskompatibel: chat_id=None → keine Injection (AgentTaskRunner, PromptTestLab)

---

## 4. Kontextquelle

Kontext aus Systemquellen, nicht aus UI:

- **ProjectService:** get_project_of_chat, get_project
- **ChatService:** get_chat_info (title, topic_id, topic_name)

Keine doppelte Wahrheit, keine direkte UI-Abhängigkeit im Kernfluss.

---

## 5. Injektionsstrategie

### 5.1 Format (nüchtern, systemisch, kurz)

```
Kontext:
- Projekt: XYZ
- Chat: Debug Session
- Topic: API
```

- Globale Chats: `- Projekt: (globale Chats)`
- Fehlendes Topic: Zeile weggelassen

### 5.2 Merge mit Chat Guard

- Wenn erste Nachricht `system`: Kontext-Block davor prependen
- Sonst: neue System-Nachricht am Anfang

### 5.3 Aktivierungslogik

| Bedingung | Verhalten |
|-----------|-----------|
| chat_id fehlt | Keine Injection |
| chat_title fehlt | Keine Injection (is_empty) |
| Globale Chats | Injection mit "Projekt: (globale Chats)" |
| Fehlendes Topic | Topic-Zeile weggelassen |
| Leere Daten | Robust, keine kaputten Fragmente |

---

## 6. Debug / Transparenz

- **DEBUG-Log:** project, chat, topic, is_global bei Injektion
- Kein großes Logging-Feuerwerk
- Später erweiterbar für Runtime/Debug-Panel

---

## 7. Tests

**Datei:** `tests/structure/test_chat_context_injection.py`

| Test | Verifiziert |
|------|-------------|
| test_chat_context_empty | Leerer Kontext |
| test_chat_context_with_chat_title | Nur chat_title |
| test_chat_context_full | Projekt, Chat, Topic, Format |
| test_build_chat_context_without_services | Keine Services → leer |
| test_build_chat_context_with_chat | Kontext aus DB |
| test_build_chat_context_global_chat | is_global_chat=True |
| test_global_chat_injection_format | "Projekt: (globale Chats)" |
| test_missing_topic_does_not_break | Fehlendes Topic bricht nichts |
| test_inject_context_* | Injection, Merge, chat_id=None |
| test_chat_service_accepts_chat_id | Parameter vorhanden |

---

## 8. Bekannte Grenzen

- **Kein Agenten-Routing:** AgentTaskRunner nutzt keinen Chat-Kontext
- **Kein RAG-Kontext:** RAG-Kontextfusion nicht Teil dieses Tasks
- **Kein Chat-Guard v2:** Bestehende Guard-Logik unverändert
- **Legacy chat_widget:** Nutzt eigenen Prompt-Flow, nicht ChatService.chat()

---

## 9. Empfohlene nächste Ausbaustufen

1. **Optional:** Runtime/Debug-Panel zeigt injizierten Kontext
2. **Optional:** Kontext-Format konfigurierbar (z.B. kürzer/länger)
3. **Optional:** Projekt-/Topic-Beschreibung als erweiterter Kontext (wenn vorhanden)
4. **Nicht:** Agenten-Routing, RAG-Fusion, Chat-Guard v2 – außerhalb des Scopes

---

## 10. Geänderte / neue Dateien

| Datei | Änderung |
|-------|----------|
| app/chat/context.py | ChatRequestContext, Format, Aktivierungslogik |
| app/chat/__init__.py | Export ChatRequestContext |
| app/services/chat_service.py | chat_id, _inject_chat_context |
| app/gui/domains/operations/chat/chat_workspace.py | chat_id an chat() |
| docs/04_architecture/CHAT_CONTEXT_INJECTION_ANALYSIS.md | Erweitert |
| docs/04_architecture/CHAT_CONTEXT_INJECTION_REPORT.md | Erweitert |
| tests/structure/test_chat_context_injection.py | +4 Tests (global, Topic) |

---

## 11. Ergebnis

Der Chat nutzt seinen Kontext aktiv und promptwirksam:

- Projektname, Chat-Titel, optional Topic werden automatisch an das Modell übergeben
- Keine neue KI-Architektur, keine neuen Modelle, kein Agenten-Vollausbau
- Kontext aus echten Systemquellen, saubere Trennung, keine UI-Abhängigkeit
- Robust bei fehlendem Kontext, keine kaputten Prompt-Fragmente
