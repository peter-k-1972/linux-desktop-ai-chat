# LLM-Modul-Struktur

**Datum:** 2026-03-16  
**Kontext:** Full System Checkup Restpoint Remediation

---

## Struktur

| Ort | Rolle |
|-----|-------|
| **app/core/llm/** | Kanonische Implementierung: OutputPipeline, ResponseCleaner, RetryPolicy, etc. |
| **app/llm/** | Re-Export für Rückwärtskompatibilität |

---

## Keine Duplikation

`app/llm` importiert ausschließlich von `app.core.llm` und re-exportiert. Keine eigene Logik.

```python
# app/llm/__init__.py
from app.core.llm import (
    OutputPipeline, ResponseCleaner, ResponseResult,
    ResponseStatus, RetryPolicy,
)
```

---

## Empfehlung

- Neue Imports: `from app.core.llm import ...`
- Bestehende Imports über `app.llm` bleiben gültig (Rückwärtskompatibilität)
- Kein Refactoring nötig; Struktur ist dokumentiert und beabsichtigt
