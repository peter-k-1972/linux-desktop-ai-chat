# Chat-Kontext-Modus – Analyse

**Stand:** 2026-03-17  
**Ziel:** Konfigurierbaren Semantik-Modus für die Kontext-Injektion – kontrollierbar, evaluierbar, vergleichbar.

---

## 1. Aktueller Stand der Kontext-Injektion

### 1.1 Pfad

```
ChatWorkspace._run_send(text)
    → chat_svc.chat(model, api_messages, chat_id=chat_id, ...)
        → _apply_chat_guard(messages)
        → _inject_chat_context(messages, chat_id)
            → app.chat.context.inject_chat_context_into_messages(messages, chat_id)
                → build_chat_context(chat_id)
                → ctx.to_system_prompt_fragment()
                → Merge in messages[0] (system) oder neue System-Nachricht
        → ollama_client.chat(model, messages, ...)
```

### 1.2 Aktuelles Format (fest verdrahtet, semantisch)

`ChatRequestContext.to_system_prompt_fragment()` liefert aktuell **immer** semantisches Format:

```
Arbeitskontext:
- Projekt: XYZ (Themenbereich)
- Chat: Debug Session (laufende Konversation)
- Topic: API (fokussierter Bereich)

Berücksichtige diesen Kontext bei der Antwort.
```

### 1.3 Beteiligte Komponenten

| Komponente | Datei | Verantwortung |
|------------|-------|---------------|
| ChatRequestContext | app/chat/context.py | Dataclass, to_system_prompt_fragment() |
| build_chat_context | app/chat/context.py | Baut Kontext aus chat_id via ProjectService, ChatService |
| inject_chat_context_into_messages | app/chat/context.py | Aktivierungslogik, Merge-Logik |
| ChatService._inject_chat_context | app/services/chat_service.py | Delegation an context-Modul |
| AppSettings | app/core/config/settings.py | Persistierte Einstellungen |

---

## 2. Sinnvoller Ort für Kontextmodus

### 2.1 Empfehlung: AppSettings + Parameter-Weitergabe

| Ort | Pro | Contra |
|-----|-----|--------|
| **AppSettings** | Persistierbar, beim Start wiederherstellbar, konsistent mit chat_streaming_enabled | — |
| **ChatService** | Liest Settings, übergibt Modus an context-Modul | — |
| **context.py** | Erhält Modus als Parameter, bleibt Qt/Infra-frei | — |

**Gewählt:** `chat_context_mode` in AppSettings. ChatService liest beim Aufruf von `_inject_chat_context` und übergibt an `inject_chat_context_into_messages(messages, chat_id, context_mode=...)`.

### 2.2 Keine Modus-Logik in GUI

- Kein neuer Settings-Panel-Ausbau erforderlich
- Optional später: Dropdown in AdvancedSettingsPanel
- Für Evaluierung reicht zunächst: Settings-Datei / Backend manuell setzen oder Test-Fixture

---

## 3. Praktikable Modi

### 3.1 Drei Modi

| Modus | Beschreibung | Format |
|-------|--------------|--------|
| **off** | Keine Kontext-Injektion | — |
| **neutral** | Nüchtern, deklarativ | Kontext: - Projekt: X - Chat: Y - Topic: Z |
| **semantic** | Semantisch angereichert (aktuell) | Arbeitskontext: ... (Themenbereich) ... Berücksichtige ... |

### 3.2 Begründung für "off"

- **Architektonisch sinnvoll:** Reproduzierbare Basislinie – gleicher Prompt ohne Kontext
- **Evaluierung:** A/B-Vergleich: off vs. neutral vs. semantic
- **Debug:** Bei Problemen Kontext abschaltbar
- **Kein Overhead:** Einfache if-Abfrage, kein Architekturbruch

---

## 4. Risiken bei Umschaltung / Fallback

| Risiko | Mitigation |
|--------|------------|
| Ungültiger Modus-Wert | Normalisierung: unbekannte Werte → "semantic" (Default) |
| Settings nicht geladen | getattr(settings, "chat_context_mode", "semantic") |
| Modus "off" vergessen | Klar dokumentiert, Log bei Skip |
| Regression in Tests | Bestehende Tests mit mode="semantic" oder Default |
| Prompt-Duplikation | Eine Methode to_system_prompt_fragment(mode), gemeinsame Grundlogik |

---

## 5. Injektionslogik pro Modus

### 5.1 off

- Keine Injektion
- `inject_chat_context_into_messages` gibt `messages` unverändert zurück
- DEBUG-Log: "Chat context skipped (mode=off)"

### 5.2 neutral

```
Kontext:
- Projekt: XYZ
- Chat: Debug Session
- Topic: API
```

- Globale Chats: `- Projekt: (globale Chats)`
- Fehlendes Topic: Zeile weggelassen
- Keine Anweisungszeile

### 5.3 semantic

```
Arbeitskontext:
- Projekt: XYZ (Themenbereich)
- Chat: Debug Session (laufende Konversation)
- Topic: API (fokussierter Bereich)

Berücksichtige diesen Kontext bei der Antwort.
```

- Wie aktuell implementiert

---

## 6. Debugbarkeit / Nachvollziehbarkeit

| Aspekt | Umsetzung |
|--------|-----------|
| Aktiver Modus | DEBUG-Log bei Injektion: mode, project, chat, topic |
| Modus off | DEBUG-Log: "Chat context skipped (mode=off)" |
| Erzeugter Block | Bereits geloggt (project, chat, topic) – optional: fragment-Länge |
| Keine UI-Baustelle | Log reicht; optional später: Debug-Panel |

---

## 7. Manuelle Variantentests – Vorbereitung

- **Reproduzierbar:** Gleicher Chat, gleiche Nachricht, Modus umschalten
- **Vorgehen:** Settings auf neutral → Senden → Settings auf semantic → Senden (ggf. neuer Chat)
- **Kein Benchmarking:** Keine Plattform nötig – sauberer Modus reicht

---

## 8. Nächste Schritte (Implementierung)

1. `chat_context_mode` in AppSettings (load/save, Default "semantic")
2. `ChatRequestContext.to_system_prompt_fragment(mode)` erweitern
3. `inject_chat_context_into_messages(messages, chat_id, context_mode)` erweitern
4. ChatService liest Modus, übergibt an context-Modul
5. Tests für alle drei Modi
6. CHAT_CONTEXT_MODE_REPORT.md
