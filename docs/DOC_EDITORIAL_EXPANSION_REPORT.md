# Dokumentation – Redaktioneller Ausbau (Bericht)

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-21  
**Ziel:** Erklärende Absätze und Übergänge ergänzen, ohne Struktur zu zerlegen und ohne vom Code abweichende Behauptungen.

Die inhaltliche Prüfung stützte sich auf die referenzierten Pfade unter `app/` (u. a. `ChatService._resolve_context_configuration`, `ChatRequestContext`, `chat_context_enums`, Provider-Paket).

---

## Erweiterte Dateien

| Datei | Ergänzungen (Kurz) |
|-------|-------------------|
| `docs/FEATURES/chat.md` | Zweck vertieft; Absatz zum Datenfluss GUI → Slash → Kontext → Guard → Provider; Abschnitt **Typischer Ablauf** |
| `docs/FEATURES/context.md` | Abgrenzung zu RAG; Ablauf `OFF` vs. Fragment; Einleitung unter **Konfiguration** zur Override-Kette |
| `docs/FEATURES/settings.md` | Rolle persistenter Einstellungen vs. Laufzeit-Overrides; zweites Nutzungsszenario (Standardmodell) |
| `docs/FEATURES/rag.md` | Zweck im Anwendungskontext; grober technischer Ablauf vor der Stichpunktliste |
| `docs/FEATURES/providers.md` | Rolle der Provider-Schicht; vereinfachter **Datenfluss** bis HTTP |
| `docs/FEATURES/prompts.md` | Zweck der Vorlagen; **Typischer Ablauf**; Abgrenzung zu Slash-Commands |
| `docs/02_user_manual/ai_studio.md` | Warum „AI Studio“ ein Sammelbegriff ohne eigene Screen-ID ist |
| `docs/01_product_overview/introduction.md` | Verweis auf kanonische Hilfe `help/getting_started/introduction.md` und Abgrenzung `docs` vs. Hilfe |
| `help/getting_started/introduction.md` | Navigation (Operations / Control Center / Settings) und Mindestvoraussetzungen für den Einstieg |
| `help/settings/settings_overview.md` | Einleitung zu Rolle der Einstellungen und Verweis auf Kontext-Overrides |
| `help/settings/settings_chat_context.md` | Ausführlicher Block **Context Mode** (inkl. Abgrenzung Verlauf vs. Metadaten); **Detail Level**; Missverständnis Include-Flags; **Profile**; **Override-Reihenfolge** |
| `help/operations/chat_overview.md` | Session-Fokus; Einleitung **Komponenten**; Slash-Commands; typischer Bedienfehler |
| `help/operations/prompt_studio_overview.md` | Übersicht mit Workflow-Hinweis; Erläuterung **Prompt-Typen**; Slash-Commands vs. gespeicherte Prompts |
| `docs_manual/modules/chat/README.md` | Kompakte Pipeline-Zusammenfassung in Fachsicht; neuer Abschnitt **Typischer Nutzungsablauf** |
| `docs_manual/workflows/chat_usage.md` | Rahmenabsatz vor **Ziel** (linearer Minimalpfad vs. Praxis) |

---

## Abschnitte mit gezielten Textergänzungen (nach Thema)

- **Chat:** Zweck, Funktionsweise, neuer Ablaufabschnitt  
- **Chat-Kontext (Hilfe + Feature Context):** Modus/Detail/Includes/Overrides in Prosa  
- **Einstellungen:** globale Rolle, Kontext-Override-Hinweis  
- **RAG / Provider / Prompts:** Einordnung und typische Nutzung  
- **AI Studio / Produkt-Einführung:** Begriffsklärung und Verweislogik  
- **Manual Chat-Modul & Workflow:** Didaktische Einordnung der Pipeline  

---

## Bereiche, die weiterhin dünn oder tabellenlastig sind

Nicht im Rahmen dieser Runde ausgebaut (bewusst begrenzter Umfang):

- **`docs/qa/**`, viele `docs/*_REPORT.md`, `*_MATRIX.md`, `*_PLAN.md`:** überwiegend Status-, Audit- oder CI-Dokumentation; dort sind Listen/Tabellen oft gewollt. Ein ausufernder Prosa-Ausbau würde Wartungskosten erhöhen, ohne Nutzen für Endanwender.  
- **`docs_manual/modules/*/`** (außer `chat`): viele Module folgen der Matrix-Vorlage (Rollen, Tabellen) — gleiche redaktionelle Behandlung wie bei Chat wäre sinnvoll, aber umfangreich.  
- **`help/control_center/*.md`, `help/operations/knowledge_overview.md`, `help/troubleshooting/troubleshooting.md`:** teils bereits narrativ; teils Kataloge — bei Bedarf gezielt nachziehen.  
- **`docs/02_user_manual/settings.md`, `models.md`, `rag.md`:** wenn vorhanden und stark tabellarisch, analog zu `FEATURES/*` mit Kurzprosa absätzen.  
- **Architektur-Tiefenberichte unter `docs/04_architecture/`:** oft Analyseartikel; Ergänzung von „Einleitung für Leser ohne Kontext“ wäre möglich, sollte aber fallweise erfolgen, um nicht mit bestehenden Audit-Zitaten zu kollidieren.

---

## Qualitätssicherung (QA-Redaktion)

- Keine neuen Feature-Versprechen eingeführt; Aussagen zu Kontextmodi, `OFF`-Behandlung, Prioritätskette und `ChatRequestContext` an Code angelehnt.  
- Redundanz bewusst begrenzt: Hilfe- und `FEATURES`-Dateien überschneiden sich leicht bei Kontext — dort wurde mit unterschiedlichem Fokus (Nutzer vs. Entwickler-Kurzreferenz) gearbeitet.  
- Marketing- und Floskel-Sprache vermieden.

---

## Empfehlung für Folgeiterationen

1. Dieselbe Ergänzungslogik auf `help/operations/knowledge_overview.md` und `help/control_center/control_center_overview.md` anwenden (typische Abläufe + Fehlerbilder).  
2. `docs_manual/modules/context/README.md` und `modules/rag/README.md` mit je einem erklärenden Absatz zur Schnittstelle zum `ChatService` versehen.  
3. Große Report-Sammlungen unter `docs/` nicht flächig „entprosaisieren“; stattdessen je README/Index eine **Leserichtung** (1 Absatz) ergänzen.
