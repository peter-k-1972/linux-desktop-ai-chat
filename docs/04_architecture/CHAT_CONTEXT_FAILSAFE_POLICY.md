# Chat-Kontext – Fail-Safe & Debug Policy

**Stand:** 2026-03-17  
**Ziel:** Kontextmechanismus im Betrieb sauber und unauffällig halten. Kein Crash, keine versteckten Entscheidungen.

---

## 1. Fail-Safe Policy

| Situation | Verhalten |
|-----------|-----------|
| **Settings ungültig** | Fallback auf dokumentierte Defaults (mode=semantic, detail=standard, fields=all) |
| **Kein Kontext aufgebaut** | Keine Injection, kein Crash – Messages unverändert zurückgeben |
| **Render-Optionen → leeres Fragment** | Keine Injection – Messages unverändert zurückgeben |
| **Messages malformed** | Fail-safe Rückgabe (original messages), DEBUG-Log bei Bedarf |
| **Mehrfach-Injection möglich** | Idempotent verhindern – [[CTX]]-Marker prüfen, keine Duplikate |

### 1.1 Truncation & Limits – Edge Cases

| Situation | Verhalten |
|-----------|-----------|
| **Nach Truncation alle Felder leer** | Keine Injection – Fragment wird verworfen |
| **Line limit erlaubt nur Header + 0 Felder** | Keine Injection – Fragment wird verworfen |
| **Fragment nur aus Marker/Header** | Keine Injection – nur sinnvolle Zeilen bleiben |
| **Truncation führt zu leerem "..."-Müll** | Feld weglassen – Zeile wird nicht gerendert |

---

## 2. Debug Policy

### DEBUG darf zeigen

- `mode` – aktueller Kontextmodus
- `detail` – Detailtiefe
- `fields` – aktive Felder (project, chat, topic)
- `stats` – chars, lines (Strukturmetriken)
- `skipped` / `injected` – ob Injection erfolgte oder übersprungen wurde

### DEBUG darf NICHT

- komplette Antwortinhalte aufblasen
- versteckte Entscheidungen treffen
- zusätzliche Kontextheuristiken enthalten

---

## Referenz

- Governance: CHAT_CONTEXT_GOVERNANCE.md
- Technische Umsetzung: app/services/chat_service.py (_inject_chat_context), app/chat/context.py
