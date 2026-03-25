# Konfiguration der Plugin-Produktfreigabe (Host)

## Abgrenzung

| Schicht | Rolle |
|---------|--------|
| **Discovery** | Findet installierte / registrierte Registrare |
| **Governance** | Validiert Deskriptor, Namen, Gruppen |
| **Registry** | Hält alle akzeptierten Feature-Namen |
| **Produktfreigabe (Code)** | `CENTRAL_PRODUCT_RELEASED_PLUGIN_FEATURES`, `EditionDescriptor.released_plugin_features` |
| **Produktfreigabe (Konfiguration)** | Optional: YAML ergänzt Allow / entzieht per Deny — nur **externe** Namen |
| **Edition** | Primäre Aktivierung: `enabled_features` / `disabled_features` |
| **Availability** | `is_available()`, Dependency-Gruppen |

## Primärquelle

- Standardpfad: `config/plugin_feature_release.yaml` (Repo-Root)
- Überschreiben: Umgebungsvariable **`LDC_PLUGIN_RELEASE_CONFIG`** (absoluter oder repo-relativer Pfad)

Fehlt die Datei: unverändertes Verhalten wie ohne Konfiguration (nur Code/Edition).

Referenzinhalt: `config/plugin_feature_release.example.yaml`

## Schema (klein)

| Schlüssel | Bedeutung |
|-----------|-----------|
| `allow_additional_plugin_features` | Liste externer Feature-Namen, die **zusätzlich** zur code-seitigen Freigabe gelten |
| `deny_plugin_features` | Liste externer Namen, die **global** aus der Freigabe entfernt werden (auch wenn in Code/Edition freigegeben) |
| `apply_to_editions` | Optional: Liste von Edition-Namen (kleingeschrieben verglichen). Fehlt oder leer: **Allow** gilt für **alle** Editionen; **Deny** ist immer global |

Builtin-Namen in Listen werden protokolliert und **ignoriert** — Builtins bleiben ausschließlich editionsgesteuert.

## Was die Konfiguration darf / nicht darf

**Darf:**

- Externe Freigabe **ergänzen** (Allow, editionsgebunden möglich)
- Externe Freigabe **verengen** (globaler Deny)
- Operativ zwischen Umgebungen wechseln (andere Datei per Env)

**Darf nicht** (bewusst nicht implementiert):

- Editionen ersetzen oder Features aktivieren, die **nicht** in der Edition stehen
- Builtins deaktivieren oder umbiegen
- Eine zweite, widersprüchliche Produktwahrheit neben den Editionen erzeugen

Effektive Aktivierung externer Features bleibt:

```text
Edition ∩ Extern ∩ (Code-Freigabe ∪ Config-Allow) \ Config-Deny
```

(Builtins: `Edition ∩ Builtins` wie bisher.)

## Demo-Plugin `ldc.plugin.example`

- Standard: Edition **`plugin_example`** + `released_plugin_features` im Code — kein Config-Zwang.
- Optional: In `full` (oder anderer Edition) den Namen **nur** über ein angepasstes Edition-Manifest aufnehmen **und** ihn per Config **allow** freigeben, wenn er nicht in `released_plugin_features` dieser Edition im Code steht — ohne `builtins.py` zu ändern (nur für klar kontrollierte Setups).

Ohne Edition-Eintrag reicht **keine** Konfiguration allein.

## Technik

- Loader: `app/features/plugin_release_config.py` (PyYAML)
- Einbindung: `product_releasable_plugin_feature_names` → `apply_plugin_release_config`
- Cache: `lru_cache` pro absolutem Pfad; für Tests `clear_plugin_release_config_cache()`

## Bewusst nicht implementiert

- UI, Marketplace, Signing, Rollen
- Mehrere konkurrierende Config-Quellen
- Policy-DSL

## Verweise

- [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md)
- [PLUGIN_PACKAGES_ENTRY_POINTS.md](PLUGIN_PACKAGES_ENTRY_POINTS.md)
