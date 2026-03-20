# Tools – Governance-Entscheidung

**Datum:** 2026-03-16  
**Kontext:** Full System Checkup Restpoint Remediation

---

## Entscheidung

**Bewusst keine formale Tools-Registry.**

---

## Begründung

1. **Kleine, stabile Menge:** Aktuell FileSystemTools und web_search. Erweiterung ist selten.
2. **Zentrale Deklaration:** `app/tools/__init__.py` listet alle Tools explizit. Änderungen erfordern Code-Review.
3. **Kein dynamisches Laden:** Tools werden nicht zur Laufzeit registriert; kein Bedarf für Registry-Pattern.
4. **REGISTRY_GOVERNANCE:** Gilt für Model, Nav, Screen, Command – nicht für Tools. Tools sind kein Registry-Fall.

---

## Governance

- Neue Tools: In `app/tools/` implementieren und in `app/tools/__init__.py` exportieren.
- Keine parallelen Tool-Definitionen außerhalb von app/tools/.
- Bei signifikantem Wachstum (>5 Tools, dynamische Erweiterung): Registry evaluieren.
