# Business

Kurzfassung für Entscheidungsträger: wofür die Anwendung eingesetzt wird, welche Bausteine das ermöglichen und welche betrieblichen und fachlichen Risiken aus der Produktarchitektur folgen. Inhalte spiegeln die implementierten Module wider, keine zusätzlichen Produktversprechen.

## Relevante Module (Überblick)

- [Chat](../../modules/chat/README.md) · [RAG](../../modules/rag/README.md) · [Agenten](../../modules/agents/README.md) · [Provider](../../modules/providers/README.md)  
- [Architektur (kanonisch)](../../../docs/ARCHITECTURE.md) · [Produkt-Architektur](../../../docs/01_product_overview/architecture.md)

## Aufgaben

- Einschätzen, ob die **lokale Desktop-Plattform** (PySide6 + Ollama + optional RAG/Agenten) zu IT- und Arbeitsmodellen passt.
- **Nutzen** gegenüber reinem Web-Chat abwägen: Datenverarbeitung auf dem Arbeitsplatz/Server, konfigurierbare Modell- und Wissensanbindung.
- **Risiken** mit IT (Provider, Cloud, Speicherorte) und Fachbereichen (Prompt-Qualität, RAG-Genauigkeit) klären.

## Typische Workflows (organisatorisch)

### Einführung für Wissensarbeit mit internen Dokumenten

1. IT stellt **Ollama** und Basis-Modelle bereit.
2. Fachbereich definiert, welche **Dokumente** in den RAG-Index dürfen (`Knowledge`-Workspace, `rag_space`).
3. Nutzer arbeiten in **Operations → Chat** mit aktiviertem RAG, wenn die Policy das erlaubt.
4. Qualitätssicherung: Stichproben auf Halluzinationen und veraltete Chunk-Inhalte.

### Einführung für spezialisierte Bearbeitung (Agenten / Delegation)

1. **Control Center → Agents:** Profile pflegen (Rollen, Modelle).
2. Nutzer nutzen **Agent Tasks** oder `/delegate Aufgabe` im Chat für Aufgaben, die die Agenten-Pipeline abdeckt (`app/agents/`).
3. Klärung, welche Aufgaben **nicht** automatisiert werden dürfen (Compliance, Freigaben).

### Standardisierung von Texten (Prompts)

1. **Prompt Studio** als zentrale Vorlagenbibliothek nutzen (`operations_prompt_studio`).
2. Speicherort festlegen: Datenbank vs. Verzeichnis (`prompt_storage_type`, `prompt_directory`).
3. Schulung: Vorlagen versionieren und verbindlich machen, wo sinnvoll.

## Genutzte Module (Nutzen in Geschäftssprache)

| Modul | Nutzen / Einsatzmöglichkeit |
|-------|-----------------------------|
| [chat](../../modules/chat/README.md) | Zentraler Dialog mit Sprachmodellen; Streaming; Rollen-Steuerung über Befehle. |
| [context](../../modules/context/README.md) | Steuerbarer Projekt-/Chat-Bezug im Prompt; reduzierbar für Datenschutz oder breitere Fragen. |
| [rag](../../modules/rag/README.md) | Antworten mit Bezug zu **euren** Dokumenten (nach Indexierung). |
| [agents](../../modules/agents/README.md) | Spezialprofile und Mehrschritt-Orchestrierung für komplexe Aufgaben. |
| [prompts](../../modules/prompts/README.md) | Einheitliche Kommunikations- und Prozessvorlagen. |
| [providers](../../modules/providers/README.md) | Lokaler Betrieb; optional Cloud-Ollama mit API-Key. |
| [settings](../../modules/settings/README.md) | Zentrale Schalter für Modell, RAG, Cloud, Kontext, Darstellung. |
| [gui](../../modules/gui/README.md) | Eine Oberfläche für Chat, Wissen, Steuerung, QA-Ansichten und Einstellungen. |

## Risiken

| Risiko | Herkunft (Produkt) |
|--------|---------------------|
| **Falsche oder veraltete RAG-Antworten** | Retrieval und Chunking liefern nur Ausschnitte; keine Garantie auf Vollständigkeit (`app/rag/`). |
| **Cloud-Übermittlung** | Bei aktivierter Cloud-Eskalation und gültigem Key gehen Anfragen an Ollama-Cloud-Infrastruktur (`cloud_ollama_provider`, Einstellungen). |
| **Kein impliziter Projektbezug** | Kontextmodus **Aus** oder Overrides — Modell „sieht“ Projektmetadaten ggf. nicht (`ChatService`, Modul **context**). |
| **Delegations- und Agentenfehler** | Automatisierte Pfade können fehlschlagen oder unerwartete Zwischenschritte erfordern (`app/agents/`). |
| **Abhängigkeit von Ollama** | Ausfall oder Performance des Dienstes blockiert Chat (`app/providers/`). |
| **Technische Komplexität** | QA-/Runtime-Workspaces zeigen Systemtiefe — für reine Fachnutzer ggf. überfordert; Zugriff steuern. |

## Best Practices

- **Policy schriftlich:** wann RAG, wann Cloud, wann Kontext **Aus** für sensible Themen.
- **Pilot:** begrenzte Nutzergruppe, definierte Use Cases (Chat-only, Chat+RAG, Agenten).
- **Governance:** Nutzung der **QA & Governance**-Workspaces (`qa_*`) in größeren Organisationen mit IT-Qualitätsprozess abstimmen.
- **Schulung:** Slash-Commands und Kontextleiste (Projekt/Chat) erklären — reduziert Supportaufwand.
