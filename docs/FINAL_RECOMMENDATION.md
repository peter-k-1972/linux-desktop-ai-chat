# FINAL_RECOMMENDATION – Linux Desktop Chat

**Stand:** 2026-03-21

## Handlungsempfehlung

1. **`app/gui.zip` entfernen oder aus dem App-Paket auslagern** und erneut `tests/architecture/test_app_package_guards.py` fahren – das ist ein **schneller, objektiver** Schritt und beseitigt RB-02.

2. **Einen CI-Job ergänzen**, der nach `pip install -r requirements.txt` die **gesamte** `pytest`-Suite (oder eine definierte Obermenge inkl. Architektur + Chat + DB) ausführt – sonst wiederholt sich die aktuelle **Rotphase unbemerkt**.

3. **Failures clustern und nacheinander schließen:** zuerst **Governance-Imports/EventBus/Provider** (klare Architekturentscheidung: Guard lockern *oder* Code anpassen), danach **Chat-Kontext-Injektion vs. Tests** (einheitliches Sollverhalten dokumentieren), dann **DB/Projekt-Tests** (writable Test-DB / Fixtures).

4. **`docs/IMPLEMENTATION_GAP_MATRIX.md` und `DOC_GAP_ANALYSIS.md`** an den **heutigen Code** anpassen, damit Audits nicht gegen veraltete Tabellen laufen.

**Kein sinnvoller nächster Schritt:** „Release taggen“ oder „Phase-6 sign-off“ – **erst** wenn die Gesamtsuite **grün** ist oder der **Scope** der Freigabe **explizit** auf „nur Unit + manuelle Smoke“ reduziert wird (dann **andere** Freigabe-Matrix verwenden).

---

*Ende FINAL_RECOMMENDATION*
