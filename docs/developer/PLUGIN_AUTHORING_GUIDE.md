# Plugin-Autoren: FeatureRegistrar per Entry Point

Dieses Dokument richtet sich an Maintainer **externer Python-Pakete**, die Linux Desktop Chat um Features erweitern wollen — ohne den Host-Code zu kopieren.

## Minimale Paketstruktur

```
my_plugin/
  pyproject.toml
  src/
    my_plugin/
      __init__.py
      feature_entry.py   # oder beliebiges Modul für den Entry Point
```

## `pyproject.toml` (PEP 621)

```toml
[project]
name = "my-plugin"
version = "0.1.0"
requires-python = ">=3.10"

[project.entry-points."linux_desktop_chat.features"]
my_plugin = "my_plugin.feature_entry:get_feature_registrars"

[tool.setuptools.packages.find]
where = ["src"]
```

Die Gruppe **`linux_desktop_chat.features`** ist verbindlich (siehe `app/features/entry_point_contract.py`).

**Hinweis (Split):** Der Importpfad **`app.features`** für öffentliche Typen (z. B. `FeatureDescriptor`) bleibt auch nach Auslagerung in die Distribution **`linux-desktop-chat-features`** bestehen — siehe [`PACKAGE_FEATURES_PHYSICAL_SPLIT.md`](../architecture/PACKAGE_FEATURES_PHYSICAL_SPLIT.md). Plugins ändern ihre Importzeilen dafür nicht.

## Registrar-Vertrag

Implementierung entspricht dem Protocol `FeatureRegistrar` (`app/features/registrar.py`):

- `get_descriptor() -> FeatureDescriptor`
- `register_screens`, `register_navigation`, `register_commands`, `register_services`
- `is_available() -> bool`

Metadaten: `app/features/descriptors.py`. Optional: `get_feature_compatibility()` für explizite Governance (`app/features/compatibility.py`).

### Import-Grenze

Im Plugin-Code **nur** `app.features.*` und stabile Domänen-APIs nutzen, die ihr dokumentiert — **nicht** `app.gui` aus einem reinen Metadaten-Modul importieren (Host-AST-Guards / Schichtung).

## Naming & Governance

- Feature-Namen dürfen **keine** Builtin-Namen aus dem Host-Katalog belegen.
- Erweiterungen: Präfix `plugin_` oder `ext_`, **oder** punkt-separierter Namespace (z. B. `vendor.product.feature`).
- `optional_dependencies` im Deskriptor: nur **vom Host registrierte** Dependency-Gruppen; unbekannte Gruppen führen zur Ablehnung des Registrars (fail-soft im Gesamtbootstrap).

## Produktfreigabe (Host)

Discovery und gültiger Registrar reichen **nicht**: Der Host aktiviert externe Namen nur, wenn sie

1. in der gewählten **Edition** vorkommen (`enabled_features`), und  
2. **produktfreigegeben** sind — zentral (`CENTRAL_PRODUCT_RELEASED_PLUGIN_FEATURES`) und/oder im Feld **`released_plugin_features`** der jeweiligen `EditionDescriptor`.

Builtins unterliegen dieser Extra-Freigabe nicht. Vollständige Kette: [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](../architecture/PLUGIN_FEATURE_PRODUCT_ACTIVATION.md).

**Demo:** Edition `plugin_example` + Beispiel-Feature `ldc.plugin.example` (siehe Host-`builtins`); Start z. B. `LDC_EDITION=plugin_example` nach Installation des Beispiel-Pakets.

**Optional (Host):** Zusätzliche Freigabe oder globaler Entzug über eine kleine YAML-Datei — ohne Edition zu ersetzen; siehe [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](../architecture/PLUGIN_FEATURE_RELEASE_CONFIGURATION.md).

## Lokale Testinstallation

```bash
# Terminal A: Host-Repo
cd /path/to/linux-desktop-chat
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Plugin
pip install -e ./examples/plugins/ldc_plugin_example
```

Prüfen, ob der Registrar ankommt (nach erfolgreicher Validierung in der Registry; Log-Level ggf. auf INFO/WARNING stellen):

- Python-One-Liner: `FeatureRegistry` mit `register_discovered_feature_registrars` bauen und `list_registrar_names()` prüfen — siehe Tests unter `tests/unit/features/test_entry_point_plugin_integration.py`.

## Deaktivieren / Entfernen

- **Entfernen**: `pip uninstall ldc-plugin-example` (Paketname aus dem jeweiligen `pyproject.toml`).
- **Edition**: Ein Feature kann in der Registry existieren, aber **ohne** Eintrag in der aktiven Edition inaktiv bleiben.
- **Produktfreigabe**: Selbst bei Edition-Eintrag bleiben **externe** Namen inaktiv, wenn der Host sie nicht freigibt (Allowlist / `released_plugin_features`).
- **Temporär**: Virtuelle Umgebung ohne das Plugin neu aufsetzen oder editable-Install entfernen.

## Referenz-Beispiel

Repository-Pfad: `examples/plugins/ldc_plugin_example/` — enthält `get_feature_registrars()` und ein harmlose No-op-Feature `ldc.plugin.example`.

Architektur: [PLUGIN_PACKAGES_ENTRY_POINTS.md](../architecture/PLUGIN_PACKAGES_ENTRY_POINTS.md), [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](../architecture/PLUGIN_FEATURE_PRODUCT_ACTIVATION.md).
