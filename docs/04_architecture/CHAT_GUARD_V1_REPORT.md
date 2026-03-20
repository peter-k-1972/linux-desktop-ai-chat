# Chat Guard v1 – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Schlanker Chatwächter zwischen User-Input und Modellaufruf.

---

## 1. Gewählter Integrationspunkt

**ChatService.chat()** – vor dem Aufruf von `ollama_client.chat()`.

- GUI bleibt frei von Guard-Logik
- Logik in Service-Schicht (app/core/chat_guard, app/services)
- Kein GUI→Provider-Direktpfad
- Spätere Agenten-Integration: AgentTaskRunner nutzt ggf. ChatService → Guard greift automatisch

**Ablauf:**
```
ChatWorkspace → chat_svc.chat(model, messages)
    → ChatService._apply_chat_guard(messages)
    → get_chat_guard_service().assess(last_user_content)
    → get_chat_guard_service().apply_to_messages(messages, result)
    → ollama_client.chat(model, modified_messages, ...)
```

---

## 2. Intent-Modell

**Modul:** `app/core/chat_guard/intent_model.py`

| Intent | Bedeutung |
|--------|-----------|
| `chat` | Normale Unterhaltung |
| `command` | Slash-/Command-Pfad (/think, /agent, etc.) |
| `formal_reasoning` | Beweis, Axiom, formale Herleitung, Definition |
| `coding` | Code, Technik, Debug, Refactor |
| `knowledge_query` | Wissensfrage, Attribution (Autor, Werk) |
| `possibly_ambiguous` | Mögliche Ambiguität / Mismatch-Risiko |

**GuardResult:** intent, risk_flags, sanity_flags, routing_hint, prompt_mode, system_hint, user_prefix

---

## 3. Sanity-/Risk-Heuristiken

### 3.1 Heuristische Erkennung (heuristics.py)

| Kategorie | Muster (Beispiele) |
|-----------|-------------------|
| Command | `/think`, `/agent`, `/tool`, `/rag`, `/code`, `/formal`, `/help` |
| Formal | Beweis, Axiom, Definition, Theorem, Lemma, Satz des/der, logisch, mathematisch |
| Coding | Python, Code, Klasse, Funktion, Debug, Stacktrace, Exception, API, Bug |
| Knowledge | von X, wer schrieb, Gedicht, Autor, Werk, Roman, Ballade, Komponist |
| Ambiguität | Kombination Wissensfrage + Zuschreibung (von X, Autor von, Werk von) |

### 3.2 Risk-Flags

- `command_unrecognized`: Slash-Befehl nicht in bekannter Liste
- `attribution_risk`: Wissensfrage mit Autor-/Werk-Zuschreibung
- `mismatch_risk`: Mismatch-Risiko (falsche Zuordnung möglich)

### 3.3 Sanity-Flags

- `verify_assumptions`: Bei Wissensfrage mit Zuschreibung – Annahmen prüfen

---

## 4. Prompt-Härtung

**Modul:** `app/core/chat_guard/prompt_hardening.py`

| Intent / Flag | Hint (gekürzt) |
|---------------|----------------|
| formal_reasoning | Antworte formal, ohne Meta-Kommentare, mit klarer Struktur. |
| coding | Antworte technisch präzise, direkt und ohne Plaudertext. |
| knowledge_query + verify_assumptions | Prüfe zuerst, ob die Annahmen in der Frage korrekt sind. Korrigiere sie gegebenenfalls. |
| knowledge_query | Antworte sachlich und präzise. Bei Autor-/Werk-Zuschreibungen: Prüfe die Annahmen. |
| possibly_ambiguous | Prüfe die Annahmen in der Frage. Korrigiere sie gegebenenfalls. |
| command_unrecognized | Der Befehl wurde nicht erkannt. Antworte hilfreich. |

**Anwendung:** System-Nachricht am Anfang der Message-Liste (vor allen anderen Nachrichten).

---

## 5. Integrationsweise

- **ChatService.chat()** ruft `_apply_chat_guard(messages)` auf
- Extrahiert letzte User-Nachricht
- Ruft `guard.assess(content)` → GuardResult
- Ruft `guard.apply_to_messages(messages, result)` → ggf. mit System-Hint erweiterte Liste
- Bei Exception im Guard: Original-Messages unverändert (fail-safe)

---

## 6. Tests

**Datei:** `tests/unit/test_chat_guard.py`

| Testklasse | Inhalt |
|------------|--------|
| TestHeuristics | Slash, formal, coding, knowledge, attribution_risk, normal chat |
| TestSanityCheck | verify_assumptions bei knowledge + attribution |
| TestPromptHardening | Hint für formal, coding, knowledge_verify, kein Hint für chat |
| TestChatGuardService | assess, apply_to_messages |
| TestNoRegression | Normale Chatfrage nicht blockiert, leere Messages unverändert |

**Ergebnis:** 20 Tests bestanden.

---

## 7. Grenzen von v1

- Kein vollständiges Agenten-Routing
- Keine Wissensdatenbank für Autor/Werk-Prüfung
- Keine Blockierung von Anfragen – immer durchlassen, nur härten
- Keine UI-Anzeige von Intent/Risk (nur intern)
- Legacy ChatWidget nutzt eigenen Pfad – Guard greift dort nicht
- Heuristiken: Keyword-basiert, keine ML

---

## 8. Empfohlene nächste Ausbaustufen

1. **Routing v2:** `routing_hint` für Modellwahl nutzen (z.B. formales Modell bei formal_reasoning)
2. **Agentenintegration:** Guard in AgentTaskRunner-Pfad einbinden
3. **Bekannte Commands erweitern:** /xyz in Config/Registry
4. **Optional:** Intent/Risk im Debug-Panel anzeigen
5. **Legacy:** ChatWidget auf ChatService umstellen oder Guard dort nachziehen
