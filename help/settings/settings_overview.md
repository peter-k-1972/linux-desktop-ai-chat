---
id: settings_overview
title: Einstellungen
category: settings
tags: [einstellungen, konfiguration, theme, modell]
related: [settings_rag, settings_prompts, settings_chat_context]
workspace: settings_appearance
order: 10
---

# Einstellungen

Hier pflegen Sie Werte, die die App **über Sitzungen hinweg** merken soll: Darstellung, Standardmodell, RAG, Routing, Datenschutzoptionen und weitere Schalter. Änderungen wirken oft sofort auf neue Anfragen; manche Unterpunkte (z. B. Kontext) können durch höherpriore Laufzeitregeln überstimmt werden — dazu steht mehr in [Chat-Kontext & Einstellungen](settings_chat_context).

## Inhalt

- [Navigation im Settings-Bildschirm](#navigation-im-settings-bildschirm)
- [Allgemein](#allgemein)
- [Routing](#routing)
- [Cloud](#cloud)
- [LLM-Pipeline](#llm-pipeline)
- [Prompts](#prompts)
- [RAG](#rag)
- [Speicherort](#speicherort)

**Siehe auch (Repository)**

- [Feature: Settings](../../docs/FEATURES/settings.md) · [Workflow: Einstellungen](../../docs_manual/workflows/settings_usage.md) · [Benutzerhandbuch – Settings](../../docs/USER_GUIDE.md#4-settings-bedienen)

## Navigation im Settings-Bildschirm

Die linke Liste entspricht `app/gui/domains/settings/navigation.py`:

1. **Application** — globale Anwendungsoptionen  
2. **Appearance** — Theme und Darstellung  
3. **AI / Models** — Standardmodell, Token, Temperatur, Denkmodus — die Modell-Liste zeigt nur **chat-laufzeitfähige** Einträge aus dem Unified-Katalog (reine Datei-Zeilen `local-asset:…` ohne Ollama/Cloud-Runtime erscheinen hier nicht; Inventar und unzugewiesene Assets siehe **Control Center → Models**).  
4. **Data** — datenbezogene Optionen  
5. **Privacy** — datenschutzbezogene Optionen  
6. **Advanced** — erweiterte Schalter  
7. **Project** — projektbezogene Einstellungen  
8. **Workspace** — arbeitsbereichsbezogene Einstellungen  

**Chat-Kontext** (Modus, Detailstufe, Profil, welche Felder einfließen): [Chat-Kontext & Einstellungen](settings_chat_context)

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
