# Einstellungen

## Allgemein

| Einstellung | Beschreibung |
|-------------|--------------|
| theme | light / dark |
| model | Standard-Modell |
| temperature | 0.0–1.0 |
| max_tokens | Maximale Token pro Antwort |
| icons_path | Pfad zu Icons |
| think_mode | auto, off, low, medium, high |

## Routing

| Einstellung | Beschreibung |
|-------------|--------------|
| auto_routing | Automatische Modellauswahl |
| cloud_escalation | Cloud-Modelle erlauben |
| cloud_via_local | Cloud über lokale Ollama |
| overkill_mode | Eskalation mit stärkerem Modell |
| web_search | Websuche als Kontext |
| default_role | Standard-Rolle |

## Cloud

| Einstellung | Beschreibung |
|-------------|--------------|
| ollama_api_key | API-Key für Ollama Cloud |

## LLM-Pipeline

| Einstellung | Beschreibung |
|-------------|--------------|
| retry_without_thinking | Bei Thinking-Fehlern erneut ohne Thinking |
| strip_html | HTML aus Antworten entfernen |
| preserve_markdown | Markdown beibehalten |
| max_retries | Maximale Wiederholungen |
| fallback_model | Fallback bei Fehlern |
| fallback_role | Fallback-Rolle |

## Prompts

| Einstellung | Beschreibung |
|-------------|--------------|
| prompt_storage_type | database / directory |
| prompt_directory | Pfad bei Directory-Speicherung |
| prompt_confirm_delete | Löschbestätigung |

## RAG

| Einstellung | Beschreibung |
|-------------|--------------|
| rag_enabled | RAG aktiv |
| rag_space | default, documentation, code, notes, projects |
| rag_top_k | Anzahl Chunks für Kontext |
| self_improving_enabled | Self-Improving aktiv |
| chat_mode | auto, … |

## Speicherort

Einstellungen werden in **QSettings** gespeichert: `OllamaChat` / `LinuxDesktopChat`.
