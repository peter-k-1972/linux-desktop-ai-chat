# Plugin-Features: Discovery, Produktfreigabe, Edition, Availability

## Ziel

Externe Feature-Registrare dürfen **entdeckt** und in der **Registry** landen, werden aber **nicht** allein durch Installation produktwirksam. Dafür gibt es eine kleine, hostseitige **Produktfreigabe** — ohne Plugin-UI, Marketplace, Signing oder Rechte-Framework.

## Begriffe (Reihenfolge der Pipeline)

1. **Discovery** — findet Registrare (Builtins, Paketpfade, Entry Points, Env).
2. **Governance** — validiert Deskriptor, Namen, Kompatibilität, Dependency-Gruppen (fail-soft).
3. **Registry** — enthält alle akzeptierten Feature-Namen und Registrare.
4. **Produktfreigabe** — erlaubt **externen** Namen zusätzlich, in der Edition-Maske überhaupt aktivierbar zu sein (Code + optional **YAML**, siehe [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md)).
5. **Edition** — definiert die **gewünschte** Feature-Menge (`enabled_features` / `disabled_features`); für Externe gilt Schnittmenge mit Freigabe.
6. **Availability** — `is_available()` / optionale Dependency-Gruppen begrenzen die technisch nutzbare Teilmenge.
7. **UI / Bootstrap** — Screens, Navigation, Commands nur aus **aktivierten und verfügbaren** Registraren.

Code: `effective_activation_features` in `app/features/manifest_resolution.py` verbindet Edition-Deklaration und Produktfreigabe; `build_feature_registry_for_edition` wendet diese Menge auf die Registry an.

## Builtins vs. externe Features

| Kategorie | Builtin-Katalog (`ALL_BUILTIN_FEATURE_NAMES`) | Extern (Discovery, nicht Builtin) |
|-----------|-----------------------------------------------|-----------------------------------|
| In Edition aufgeführt | reicht für Aktivierung (wie bisher) | **zusätzlich** Produktfreigabe nötig |
| Produktfreigabe | entfällt (keine Erschwerung der Kernplattform) | zentral und/oder pro Edition |

Freigabe-Mechanismus:

- **`CENTRAL_PRODUCT_RELEASED_PLUGIN_FEATURES`** in `app/features/feature_product_release.py` (meist leer; organisationsweite Allowlist).
- **`EditionDescriptor.released_plugin_features`** — pro Edition explizit freigegebene externe Namen.
- **Optionale Host-Datei** `config/plugin_feature_release.yaml` — Allow (editionsgebunden möglich) und globaler Deny; siehe [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md).

Effektive Aktivierung (vereinfacht):

```text
Freigabe_extern = (Zentral ∪ Edition.released ∪ Config.allow*) \ Config.deny_global
aktiv = (Edition ∩ Builtins) ∪ (Edition ∩ Extern ∩ Freigabe_extern)
```
*Config.allow nur, wenn `apply_to_editions` passt oder nicht eingeschränkt.*

## Warum Installation allein nicht genügt

- **Discovery** ist bewusst offen (Entry Points etc.).
- **Produkt** soll nicht durch bloßes `pip install` wachsen; Host-Team und Editionen behalten die Kontrolle, welche externen Namen je Kontext wirksam werden.

## Edition `plugin_example`

Die interne Edition **`plugin_example`** (siehe `app/features/editions/builtins.py`) enthält die minimale Builtin-Menge plus **`ldc.plugin.example`** und trägt diesen Namen in **`released_plugin_features`**. So ist das Beispiel-Plugin unter `LDC_EDITION=plugin_example` **aktivierbar**, sofern es installiert und durch Governance akzeptiert wird — ohne die Standard-Editionen `minimal`–`full` zu erweitern.

## Bewusst nicht implementiert

- Plugin-Verwaltungs-GUI, Marketplace  
- Security / Signing / Trust  
- Rollen- oder Policy-Engine  
- Lifecycle (Unload, Hot-Reload)  

## Verweise

- [PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md](PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md) — `plugin_example` in Release-/Smoke-Architektur
- `app/features/feature_product_release.py`
- `app/features/plugin_release_config.py`
- [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md)
- [PLUGIN_PACKAGES_ENTRY_POINTS.md](PLUGIN_PACKAGES_ENTRY_POINTS.md)
- [PLUGIN_AUTHORING_GUIDE.md](../developer/PLUGIN_AUTHORING_GUIDE.md)
- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md)
- [FEATURE_PLUGIN_DISCOVERY.md](FEATURE_PLUGIN_DISCOVERY.md)
