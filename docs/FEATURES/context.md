# Feature: Context (Chat-Kontext)

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [GUI-Anbindung](#gui-anbindung)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Chat](chat.md) · [Feature: Settings](settings.md) · [Feature: Ketten (Override-Kette)](chains.md#1-kontext-override-kette-chat)  
- [Architektur – Zentrale Systeme / Context](../ARCHITECTURE.md#4-zentrale-systeme) · [Governance](../04_architecture/CHAT_CONTEXT_GOVERNANCE.md)

**Konzept → Umsetzung**

| Stelle | Rolle |
|--------|--------|
| `app/chat/context.py` | `ChatRequestContext`, Rendering, Limits-Anwendung |
| `app/chat/context_profiles.py` | Profile, Auflösung aus Presets |
| `app/services/chat_service.py` | `_resolve_context_configuration`, Injektion |
| `app/core/config/settings.py` | Persistierte `chat_context_*`-Schlüssel |
| GUI (Modus) | `app/gui/domains/settings/panels/advanced_settings_panel.py` |

**Typische Nutzung**

- [Kontext steuern (Workflow)](../../docs_manual/workflows/context_control.md)  
- [Benutzerhandbuch – Kontextmodi](../USER_GUIDE.md#3-kontextmodi-verstehen)  
- [Hilfe: Chat-Kontext](../../help/settings/settings_chat_context.md)

## Zweck

Strukturierte Metadaten (Projekt, Chat, Topic) als Systemtext an das Modell zu übergeben – gesteuert durch **Context Mode**, **Detail Level**, **Profile** und **Overrides**.

Ohne diesen Pfad „weiß“ das Modell nur aus dem sichtbaren Dialog, was Sie geschrieben haben — nicht notwendigerweise, unter welchem Projektnamen oder Session-Titel diese Konversation läuft. Der Chat-Kontext fügt diese Einordnung gezielt als formatierten Systemblock hinzu oder unterlässt das bei `off`. Er ist damit komplementär zum **RAG**-Kontext: RAG liefert Inhalte aus Dokumenten; der Chat-Kontext liefert **organisatorische** Kurzinformation zur aktuellen Sitzung.

## Funktionsweise

Die Daten werden einmal als `ChatRequestContext` zusammengestellt und dann — abhängig von Modus und Limits — in Text gewandelt. `ChatContextMode.OFF` wird im `ChatService` abgefangen: In diesem Fall wird gar kein Fragment aus diesem Objekt in die Message-Liste gemischt.

- **Datenobjekt:** `ChatRequestContext` in `app/chat/context.py` – wird aus Services befüllt.  
- **Rendering:** `to_system_prompt_fragment(mode, detail_level, render_options, render_limits)` erzeugt den Text für `neutral` oder `semantic`. Mode **`off`** führt zur vollständigen Unterdrückung der Injektion im Service (Fragment wird nicht verwendet).  
- **Limits:** `app/chat/context_limits.py` – Kürzung nach Zeichen und Zeilen; leere oder nutzlose Fragmente werden verworfen (Failsafe in `context.py`).  
- **Profile:** `ChatContextProfile` + `resolve_chat_context_profile()` in `app/chat/context_profiles.py`.  
- **Overrides:** `ChatService._resolve_context_configuration()` in `app/services/chat_service.py` wählt die siegreiche Quelle aus der Prioritätskette.

## Konfiguration

Die folgenden Schlüssel leben in `AppSettings` und werden beim Senden über `_resolve_context_configuration` mit eventuellen Overrides zusammengeführt. Nur weil ein Wert gespeichert ist, muss er nicht wirksam sein — die Prioritätskette kann eine andere Quelle durchsetzen.

### Context Mode

`chat_context_mode`: `off` | `neutral` | `semantic` (ungültig → `semantic`).

### Detail Level

`chat_context_detail_level`: `minimal` | `standard` | `full` (ungültig → `standard`).

### Felder

- `chat_context_include_project` (bool)  
- `chat_context_include_chat` (bool)  
- `chat_context_include_topic` (bool)  

### Profile

- `chat_context_profile_enabled` (bool)  
- `chat_context_profile`: `strict_minimal` | `balanced` | `full_guidance` (ungültig → `balanced`)

### Override-Priorität (höchste zuerst)

1. `profile_enabled`  
2. `explicit_context_policy`  
3. `chat_default_context_policy`  
4. `project_default_context_policy`  
5. `request_context_hint`  
6. `individual_settings` (Mode, Detail, Include-Flags)

## Beispiel

**Beispiel** — Konfigurationsideen:

- Nur Titel, wenig Text: Context Mode `semantic`, Detail `minimal`, Include nur Projekt.  
- Maximale Führung: Profil `full_guidance` mit aktiviertem Profil-Modus.

## GUI-Anbindung

Unter `app/gui/domains/settings/panels/advanced_settings_panel.py` ist ausschließlich **`chat_context_mode`** an ein UI-Element gebunden. **Detail Level**, **Include-Flags** und **Profil**-Schlüssel existieren in `AppSettings`, ohne weitere Settings-Panel-Bindings im gleichen Paket.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| „Kein Kontext“ trotz Erwartung | Mode `off` oder höherpriore Policy setzt minimales Profil |
| Topic fehlt | `include_topic` false oder Detail `minimal` ohne Topic-Name |
| Unverständliche Abweichung | Override-Kette: Inspector / Context-Explainability prüfen |
| Detail/Profil ändern sich nicht in der UI | Keine Formularfelder dafür in den Settings-Panels — nur Persistenz-Keys |
