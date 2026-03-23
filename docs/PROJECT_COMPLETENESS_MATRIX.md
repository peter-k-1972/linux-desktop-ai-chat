# PROJECT_COMPLETENESS_MATRIX – Linux Desktop Chat

**Stand:** 2026-03-21 · Soll aus Produkt-/Audit-Erwartung und `docs/QA_ACCEPTANCE_MATRIX.md`; Ist aus Code- und Testlauf.

| Bereich | Soll-Zustand | Ist-Zustand | Status | Bemerkung |
|---------|--------------|-------------|--------|-----------|
| Chat (Senden, Sessions, Streaming) | Produktiv nutzbar, regressionsgesichert | Codepfad vorhanden; **mehrere Chat-/Strukturtests fehlgeschlagen** | **Teilweise** | Siehe pytest-Failures `tests/chat/*`, `tests/structure/test_chat_context_injection.py` |
| Kontext (Modi, Injection, Policies) | Konsistent mit Tests und Architektur | **Tests widersprechen aktuellem Nachrichtenaufbau** (z. B. erwartete 2 Messages / `Kontext:`-Prefix) | **Lücke** | Soll/Ist-Abgleich Code vs. Test nötig |
| Control Center – Tools | Ehrliche Darstellung; ideal Live oder klar gekennzeichnet | **Live-artige Snapshot-Zeilen** aus `infrastructure_snapshot` + erklärender Text | **Erfüllt** | Weicht von älterer `IMPLEMENTATION_GAP_MATRIX` ab |
| Control Center – Data Stores | Wie Tools | **Proben** (SQLite read-only, RAG-Pfad, Chroma-Hinweise) | **Erfüllt** | — |
| Dashboard (Kommandozentrale) | Kein irreführender „fertiger KPI“-Schein | **Hint + Refresh** an Panels | **Erfüllt** | Vertiefung weiterhin über Command Center |
| Control Center – Agents | HR mit Service | `AgentManagerPanel` + Service (laut vorherigen Audits; nicht erneut E2E verifiziert) | **Annahme erfüllt** | Kein Blocker aus dieser Prüfung |
| Settings (Kernkategorien) | Editierbar, persistiert | Umfangreiche Kategorien implementiert (Stichprobe ok) | **Erfüllt** | — |
| Settings – Project/Workspace | Keys **oder** konsistente Leere + Doku | **Empty State** mit klarer Copy | **Erfüllt** (Scope „ehrlich leer“) | Keine projekt-spezifischen Keys |
| RAG / Knowledge | UI + Backend | Code vorhanden; Teilbereiche mit zukünftiger Verdrahtung (z. B. Source-Item-Aktionen) | **Teilweise** | Nicht release-blockierend laut dieser Abnahme |
| Prompt Studio | Editor, Manager, Preview | Implementiert; Preview-Detail nicht vollständig in dieser Abnahme vermessen | **Teilweise** | — |
| Agent Tasks | Workspace ohne alte Queue-Panels | `result_panel` etc.; keine neue Queue-UI | **Teilweise** | Laut `REMAINING_GAPS` bekannt |
| Pipelines (Comfy/Media) | Platzhalter mit klarem Fehler | Erwartung unverändert „Placeholder“ | **Offen** | Nicht Gegenstand grüner Gesamtsuite |
| Critic | Kein stiller Fake | **Warn-Log + unveränderte Antwort**; dokumentiert | **Erfüllt** (Feature absichtlich reduziert) | — |
| CLI Context / Repro | Dev-ausführbar + Doku | Module + **`docs/05_developer_guide/CLI_CONTEXT_TOOLS.md`**, `DEVELOPER_GUIDE` | **Erfüllt** | `DOC_GAP` §1 teils veraltet |
| Unit-Tests | Grün | **`pytest tests/unit` grün** | **Erfüllt** | — |
| Integration / Architektur-Tests | Grün | **Rot** (siehe Report) | **Nicht erfüllt** | Release-Blocker |
| CI | Mindestens Markdown + Kontext + Gesamtregression | **Nur Teiljobs** | **Lücke** | Blocker RB-06 |
| Doku kanonisch | Keine widersprüchlichen BLOCKER | **Teilweise** widersprüchlich | **Lücke** | Blocker RB-08 |

---

*Ende PROJECT_COMPLETENESS_MATRIX*
