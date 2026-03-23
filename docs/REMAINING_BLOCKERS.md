# REMAINING_BLOCKERS – Linux Desktop Chat

**Stand:** 2026-03-21 · Nach Stabilisierungslauf (`pytest -q` Exit 0 in Referenz-venv).

Dieses Dokument listet **echte** verbleibende Punkte – keine kosmetischen Warnungen.

---

## Nicht-blockierend (bekannt)

| Thema | Befund |
|--------|--------|
| **Optional QA-Artefakte** | Einige Tests `skip`, wenn `docs/qa/artifacts/json/QA_TEST_INVENTORY.json` o. Ä. fehlen (z. B. minimale Clones ohne `docs/qa`). Im vollständigen Repo vorhanden → kein Failure. |
| **aiohttp „Unclosed client session“** | Warnung am Ende mancher Läufe; kein Test-Failure. Aufräumen der Sessions wäre separates Hygiene-Thema. |
| **Ohne venv** | `python3 -m pytest` ohne installierte `requirements.txt` → weiterhin erwartbare Import-Errors (z. B. `qasync`). **Referenz bleibt: venv + pip install.** |

---

## Zu beobachten (kein aktueller Test-Failure)

| Thema | Befund |
|--------|--------|
| **Doku-Drift** | `docs/IMPLEMENTATION_GAP_MATRIX.md` / `DOC_GAP_ANALYSIS.md` können sich erneut vom Code entfernen; nicht Teil dieser Stabilisierung. |
| **REGRESSION_CATALOG.md** | Wird von einem Inventory-Governance-Test referenziert; Test skipped wenn Datei fehlt. |

---

## Keine offenen Release-Blocker aus RB-01–RB-07

Unter den Annahmen: frischer Checkout **mit** `docs/qa`-Artefakten, **mit** venv und `pip install -r requirements.txt`, **Linux**-Runner – liefert die Suite grün.

---

*Ende REMAINING_BLOCKERS*
