# Service Governance Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/SERVICE_GOVERNANCE_AUDIT.md`  
**Tests:** `tests/architecture/test_service_governance_guards.py`

---

## 1. Ziel

Services und angrenzende Backend-Bausteine sollen:
- klar geschnitten
- konsistent benannt
- stabil referenzierbar
- ohne stille Drift zwischen GUI, Services, Providern und Tools
- automatisiert überprüfbar

sein.

---

## 2. Layer-Regeln

### 2.1 Erlaubte Richtungen

| Quelle | Erlaubte Ziele |
|-------|----------------|
| `core` | Nur `core` (keine services, providers, gui) |
| `services` | `core`, `providers` |
| `providers` | `core` (nur base, ollama_client) |
| `gui` | `services`, `core`, `agents`, `rag`, `prompts`, `debug`, `metrics`, `qa`, `resources`, `help`, `utils` |

### 2.2 Verbotene Richtungen

| Quelle | Verboten |
|-------|----------|
| `core` | `services`, `providers`, `gui` |
| `services` | `gui` (außer dokumentierte Ausnahme) |
| `providers` | `gui`, `services`, `agents` |
| `gui` | Direkt `providers`, außer dokumentierte Ausnahmen |

### 2.3 Dokumentierte Ausnahmen

| Ausnahme | Begründung |
|----------|------------|
| ~~`services/infrastructure.py` → gui~~ | **BEHOBEN** (2026-03-16): Dependency Inversion. Backend wird von GUI-Bootstrap injiziert. |
| `main.py` → `app.providers` | Legacy MainWindow; Übergangsphase. Follow-up: Umstellung auf Services. |
| `gui/domains/settings/settings_dialog.py` → `app.providers` | Legacy Settings-Dialog; Modell-/Ollama-Konfiguration. Follow-up: ProviderService/ModelService erweitern. |

---

## 3. Service Identity / Ownership

### 3.1 Benennung

- Services: `*_service.py` (z.B. `chat_service`, `model_service`)
- Provider: `*_provider.py` oder `*_client.py` (z.B. `local_ollama_provider`, `ollama_client`)
- Keine stillen Duplikate fachlicher Verantwortlichkeit

### 3.2 Registries / Factories

- Eindeutige Keys/IDs pro Registry
- Keine toten Registrierungen
- Auflösbare Ziele (importierbar, instanziierbar)

### 3.3 Zentrale Service-Liste

- `docs/TRACE_MAP.md` Sektion "Services" und `app/services/` müssen konsistent sein
- Neue Services in TRACE_MAP und ggf. FEATURE_REGISTRY ergänzen

---

## 4. Provider Usage

### 4.1 Regel

- GUI nutzt **Services** statt Provider, wo ein dokumentierter Service-Pfad existiert
- Keine wilden Direktimporte in GUI-Domains, wenn ein Service/Facade existiert

### 4.2 Ausnahmen

- Siehe Abschnitt 2.3
- Neue Ausnahmen nur nach Architektur-Review und Eintrag in Guard-Config

---

## 5. Tool / Event / Adapter Linkage

### 5.1 Regel

- Tool- oder Event-nahe Infrastruktur hat klaren Besitz
- Keine versteckten Cross-Layer-Abkürzungen
- `app/tools` importiert nicht `gui`, `services`, `providers`
- `app/agents` importiert nicht `gui` (außer dokumentiert)

---

## 6. Ausnahmen

- Bekannte Sonderfälle explizit in `tests/architecture/arch_guard_config.py` oder Service-Guard-Config dokumentieren
- Keine stillen Ausnahmen
- Jede Ausnahme mit Begründung und Follow-up versehen
