# Feature: Settings

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Context](context.md) · [Feature: Chat](chat.md) · [Architektur – Settings](../ARCHITECTURE.md#42-settings)  
- [Benutzerhandbuch – Settings](../USER_GUIDE.md#4-settings-bedienen)

**Typische Nutzung**

- [Einstellungen (Workflow)](../../docs_manual/workflows/settings_usage.md)  
- [Hilfe: Einstellungen – Übersicht](../../help/settings/settings_overview.md)

## Zweck

Persistente Anwendungskonfiguration (Modell, Thema, RAG, Kontext, Routing, …) und zugehörige Vollbild-UI.

Einstellungen sind die **langfristige** Schicht: Sie überleben App-Neustarts und gelten typischerweise global, bis Sie sie ändern oder bis spezialisierte Mechanismen (z. B. Kontext-Policies, siehe Context-Feature) einzelne Werte zur Laufzeit überschreiben. Nicht jeder in `AppSettings` vorhandene Schlüssel hat ein sichtbares Formularfeld — manche existieren für Persistenz, API oder zukünftige UI und sind im Code dokumentiert.

## Funktionsweise

- **Logik:** `AppSettings` in `app/core/config/settings.py` liest/schreibt über `SettingsBackend` (`settings_backend.py`).  
- **GUI:** `app/gui/domains/settings/settings_workspace.py` – registrierte Kategorien:  
  `settings_application`, `settings_appearance`, `settings_ai_models`, `settings_data`, `settings_privacy`, `settings_advanced`, `settings_project`, `settings_workspace`.  
- **Navigation:** `app/gui/domains/settings/navigation.py` – Reihenfolge und Labels der linken Liste.  
- **Legacy-Mapping:** `SettingsScreen` in `settings_screen.py` mappt alte Workspace-IDs auf neue Kategorie-IDs.

## Konfiguration

Alle Keys sind in `AppSettings.load()` / `save()` aufgeführt. Wichtige Gruppen:

- Darstellung: `theme`, `theme_id`  
- Modell: `model`, `temperature`, `max_tokens`, `think_mode`  
- Routing: `auto_routing`, `cloud_escalation`, `cloud_via_local`, `default_role`, …  
- Kontext: `chat_context_mode`, `chat_context_detail_level`, `chat_context_include_*`, `chat_context_profile*`  
- RAG: `rag_enabled`, `rag_space`, `rag_top_k`, …  
- Prompts: `prompt_storage_type`, `prompt_directory`, …

## Beispiel

**Beispiel** — Theme und Standardmodell:

Theme wechseln: Settings → **Appearance** → Theme wählen (Anbindung an `ThemeManager` über die jeweiligen Panels).

**Weiteres Szenario:** Standardmodell festziehen unter **AI / Models**, dann im Chat nur noch bei Bedarf pro Nachricht abweichen — so bleibt das Verhalten vorhersagbar, wenn mehrere Nutzer oder Projekte dieselbe Installation teilen.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Einstellung „springt zurück“ | Speichern nicht ausgelöst oder Backend-Fehler |
| Falsche Kategorie nach Deep-Link | Alte `workspace_id` – Mapping in `settings_screen.py` prüfen |
| Kontext unwirksam | Siehe `FEATURES/context.md` – Overrides |
