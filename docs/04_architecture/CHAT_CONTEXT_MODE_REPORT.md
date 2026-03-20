# Chat-Kontext-Modus – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Konfigurierbarer Kontextmodus für die Kontext-Injektion – Backend-gesteuert, evaluierbar, vergleichbar.

---

## 1. Klare Trennung des Scopes

### 1.1 Implementiert (dieser Schritt)

| Bereich | Umsetzung |
|---------|-----------|
| **Settings (Backend)** | ChatContextMode-Enum, get_chat_context_mode(), chat_context_mode-Persistenz |
| **ChatService Integration** | _inject_chat_context liest Modus, delegiert an Context-Formatter |
| **Context Formatter** | to_system_prompt_fragment(mode), _to_neutral_fragment(), _to_semantic_fragment() |
| **Tests** | test_context_modes.py, test_context_mode_comparison.py, test_chat_context_injection.py |

### 1.2 Nicht Teil dieses Schritts

- **GUI Integration** – Die UI (AdvancedSettingsPanel) existiert bereits, ist aber nicht Gegenstand dieser Backend-Finalisierung.

---

## 2. Architekturprinzip

> **Kontextmodus ist eine Backend-Entscheidung.**  
> Die UI darf ihn lediglich konfigurieren, niemals interpretieren.

Die Interpretation des Modus (OFF / NEUTRAL / SEMANTIC) und die Erzeugung der Prompt-Fragmente liegen ausschließlich im Backend. Die UI speichert und lädt nur den Rohwert.

---

## 3. Modi – Definition

| Modus | Verhalten | Charakteristik |
|-------|-----------|----------------|
| **OFF** | Keine Injection | messages bleiben unverändert |
| **NEUTRAL** | Rein deklarativ | Kontext: - Projekt: X - Chat: Y - Topic: Z |
| **SEMANTIC** | Erklärend + Instruktion | Arbeitskontext mit Hints (Themenbereich, laufende Konversation, fokussierter Bereich) und Anweisung „Berücksichtige diesen Kontext bei der Antwort.“ |

### 3.1 OFF

→ Keine Injektion. Kein Kontextfragment in den Messages.

### 3.2 NEUTRAL

→ Rein deklarativ. Keine semantischen Zusätze, keine Anweisung.

```
Kontext:
- Projekt: XYZ
- Chat: Debug Session
- Topic: API
```

### 3.3 SEMANTIC

→ Erklärend + Instruktion. Semantische Hints und explizite Anweisung.

```
Arbeitskontext:
- Projekt: XYZ (Themenbereich)
- Chat: Debug Session (laufende Konversation)
- Topic: API (fokussierter Bereich)

Berücksichtige diesen Kontext bei der Antwort.
```

---

## 4. Technischer Ablauf

```
ChatService.chat(model, messages, chat_id=...)
    → _inject_chat_context(messages, chat_id)
        → mode = settings.get_chat_context_mode()
        → if mode == OFF: return messages
        → context = build_chat_context(chat_id)
        → fragment = context.to_system_prompt_fragment(mode)
        → inject_chat_context_into_messages(messages, fragment)
```

| Komponente | Datei | Verantwortung |
|------------|-------|---------------|
| ChatContextMode | app/core/config/settings.py | Enum, get_chat_context_mode() |
| AppSettings | app/core/config/settings.py | chat_context_mode (load/save) |
| ChatRequestContext | app/chat/context.py | to_system_prompt_fragment(mode) |
| inject_chat_context_into_messages | app/chat/context.py | Fragment in Messages injizieren (append, keine Duplikate) |
| ChatService._inject_chat_context | app/services/chat_service.py | Modus lesen, Kontext bauen, Fragment erzeugen, injizieren |

---

## 5. Debug-Nachvollziehbarkeit

| Modus | DEBUG-Log |
|-------|-----------|
| OFF | `ChatContextMode: off (skipped)` |
| NEUTRAL | `ChatContextMode: neutral` |
| SEMANTIC | `ChatContextMode: semantic` |

Kein Logging im Context-Modul.

---

## 6. Tests

| Datei | Inhalt |
|-------|--------|
| tests/chat/test_context_modes.py | Modus-Logik, Format, Injection-Verhalten |
| tests/chat/test_context_mode_comparison.py | Gleicher Input → unterschiedliche Modi → vergleichbare Outputs |
| tests/structure/test_chat_context_injection.py | Integration, build_chat_context, Settings |

---

## 7. Zukünftige Nutzung

> **Der Kontextmodus ist Grundlage für systematische Prompt-Vergleiche.**

- Gleicher Input, unterschiedliche Modi → messbar unterschiedliche Outputs
- Test Harness (test_context_mode_comparison.py) ermöglicht reproduzierbare Vergleiche
- Snapshots (neutral_fragment.txt, semantic_fragment.txt) machen Formatänderungen sichtbar
- Anschlussfähig für Qualitätsbewertung (Antwortqualität vs. Kontextmenge)

---

## 8. Ergebnis

- Keine Scope-Verwirrung: Backend implementiert, GUI außerhalb dieses Schritts
- Klare Architekturentscheidung: Modus ist Backend-Entscheidung, UI konfiguriert nur
- Modi definiert: OFF (keine Injection), NEUTRAL (deklarativ), SEMANTIC (erklärend + Instruktion)
- Anschlussfähig für systematische Prompt-Vergleiche und nächste Ausbaustufen
