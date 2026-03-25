# Externe Plugin-Pakete (Python Entry Points)

## Zweck

Eigenständige **Python-Distributionen** (Wheel/sdist, lokal oder Index) können
`FeatureRegistrar`-Instanzen in den Host **Linux Desktop Chat** einspeisen, ohne
das Host-Repo zu forken und ohne Marketplace, Plugin-UI, Lifecycle, Sandbox oder
Signing.

## Verbindlicher Vertrag

- **Metadata-Gruppe** (setuptools / `importlib.metadata`): `linux_desktop_chat.features`
- **Definition**: Konstante `ENTRY_POINT_GROUP` in `app/features/entry_point_contract.py`
- **PEP-621** (im Plugin-`pyproject.toml`):

  ```toml
  [project.entry-points."linux_desktop_chat.features"]
  my_plugin_id = "my_package.registrar:get_feature_registrars"
  ```

### Erwartete Exportform

| Form | Status | Beschreibung |
|------|--------|--------------|
| `qualified.module:get_feature_registrars` | **Empfohlen** | Callable ohne Argumente; Rückgabe: ein Registrar oder Sequenz von Registraren |
| Modul als Ziel (Fallback) | Unterstützt | Modul mit `get_feature_registrars()` und/oder Konstante `FEATURE_REGISTRARS` |
| `qualified.module:SOME_LIST` | Legacy | Nach `load()` nicht-aufrufbare Sequenz von Registraren |

Ungültige Einzelobjekte (kein Registrar) werden bei der Discovery **protokolliert und übersprungen** (fail-soft).

## Ablauf im Host

1. **Discovery** — `discover_feature_registrars()` in `app/features/feature_discovery.py` lädt Entry Points der Gruppe, in fester Reihenfolge nach Builtins, `app.plugins.*`, `app.extensions.*`.
2. **Validierung / Governance** — `register_discovered_feature_registrars` nutzt `plan_registration_order` / `validate_feature_registrar` (Namen, Kompatibilität, Dependency-Gruppen, `requires_features`, Duplikate). Fehler → Warn-Log, kein Abbruch der gesamten Pipeline.
3. **Registry** — Akzeptierte Registrare liegen in `FeatureRegistry`.
4. **Produktfreigabe + Edition** — `build_feature_registry_for_edition` nutzt `effective_activation_features` und `apply_active_feature_mask`: Builtins wie bisher; **externe** Namen nur bei zusätzlicher Produktfreigabe (Code, Edition-Feld, optional **YAML** `config/plugin_feature_release.yaml` / `LDC_PLUGIN_RELEASE_CONFIG`). Siehe [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md), [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md).
5. **Availability** — `is_available()` und `optional_dependencies` im `FeatureDescriptor` bleiben maßgeblich; Plugins umgehen keine technische Availability-Logik.

## Verhältnis zu Editionen und Dependency Groups

- **Editionen** definieren der Host und gebundene Manifeste — **externe Pakete liefern keine Editionen**.
- Ein entdecktes Plugin-Feature erscheint in der Registry; Aktivierung verlangt **Edition ∩ Produktfreigabe** für externe Namen (plus `is_available()`).
- **Dependency Groups** und PEP-621-`optional-dependencies` des Hosts bleiben die Referenz; Plugin-Deskriptoren referenzieren nur **bekannte** Gruppennamen in `optional_dependencies` (Governance).

## Was bewusst nicht Teil dieser Phase ist

- Kein Marketplace, keine Plugin-Verwaltungs-GUI  
- Kein Install/Update/Unload-Lifecycle im Host  
- Keine Sandbox, kein Trust/Signing  
- Kein Zwang zu mehreren Repos für den Host  

## Verweise

- Kontrakt: `app/features/entry_point_contract.py`
- Discovery: `app/features/feature_discovery.py`
- Governance: `docs/architecture/FEATURE_EXTENSION_GOVERNANCE.md`, `docs/architecture/FEATURE_PLUGIN_DISCOVERY.md`
- Autoren: `docs/developer/PLUGIN_AUTHORING_GUIDE.md`
- Produktfreigabe: [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md)
- Release-/Smoke-Einordnung Demo-Edition: [PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md](PLUGIN_RELEASE_AND_SMOKE_POSITIONING.md)
- Beispielpaket: `examples/plugins/ldc_plugin_example/`
