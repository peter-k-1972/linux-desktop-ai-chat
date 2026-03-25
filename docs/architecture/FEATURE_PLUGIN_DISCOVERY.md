# FeatureRegistrar Discovery

## Zweck

Neben den **eingebauten** Registraren (`app/gui/registration/feature_builtins.py`) können
`FeatureRegistrar`-Instanzen aus weiteren Quellen geladen werden — **ohne** Plugin-Lifecycle,
Sandbox oder Installations-UI.

`register_builtin_registrars` in `app/features/builtins.py` ruft
`register_discovered_feature_registrars` auf, das `discover_feature_registrars()` abarbeitet
(jeweils als `DiscoveredFeatureRegistrar` mit `FeatureSourceKind`) und dabei **Governance-Validierung**
(`plan_registration_order` in `app.features.feature_validation`) anwendet — siehe
`FEATURE_EXTENSION_GOVERNANCE.md`.

## Reihenfolge der Quellen

1. **Builtins** — `iter_builtin_feature_registrars()` im Modul `feature_builtins`
2. **`app.plugins.<subpkg>.feature_registrar`** — jedes direkte Unterpaket von `app.plugins`, das ein Submodul `feature_registrar` hat
3. **`app.extensions.<subpkg>.feature_registrar`** — gleiches Muster für `app.extensions`
4. **Entry Points** — Gruppe `linux_desktop_chat.features` (``importlib.metadata``); verbindlicher Vertrag: [PLUGIN_PACKAGES_ENTRY_POINTS.md](PLUGIN_PACKAGES_ENTRY_POINTS.md), Konstanten in ``app/features/entry_point_contract.py``
5. **Umgebung** — `LDC_FEATURE_REGISTRAR_MODULES` (kommaseparierte Modulnamen), die `get_feature_registrars()` oder `FEATURE_REGISTRARS` exportieren

## Kontrakt pro Modul

Ein Discovery-Modul kann liefern:

- `get_feature_registrars() -> Sequence[FeatureRegistrar]` (oder einzelner Registrar), **oder**
- `FEATURE_REGISTRARS` — Liste/Tuple von Registraren

## Fail-soft

Importfehler, kaputte Entry Points, **Governance-Validierung** (Name, Gruppen, Kompatibilität,
`requires_features`, `incompatible_features`, Duplikate im Batch) sowie **doppelte Feature-Namen**
beim finalen `register_registrar` (`ValueError`) führen zu **Warn-Logs** und Überspringen —
**kein** Prozessabbruch der Shell allein deswegen.
Builtins sind kritisch: schlagen sie fehl, wird die Exception weitergereicht (App kann ohne
Kernfeatures nicht sinnvoll starten).

## Verhältnis zu Editionen und Produktfreigabe

Die Registry wird mit ``apply_active_feature_mask(effective_activation_features(edition))`` gesetzt:
**Builtins** wie in der Edition deklariert; **externe** Namen zusätzlich nur bei Host-**Produktfreigabe**
(siehe [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md)).
Entdeckte, aber weder edition- noch freigabewirksame Features bleiben in der Registry **inaktiv**.

## Verhältnis zu Dependency Groups / Availability

Entdeckte Registrare nutzen dieselbe `FeatureRegistrar.is_available()`-Kette
(`optional_dependencies`, `dependency_availability`) wie Builtins.

## Externe Plugin-Pakete

Entry Points sind produktiv für **eigenständige** Python-Pakete nutzbar (PEP 621). Beispiel:
`examples/plugins/ldc_plugin_example/`. Autorendoku: [../developer/PLUGIN_AUTHORING_GUIDE.md](../developer/PLUGIN_AUTHORING_GUIDE.md).

## Verweise

- `app/features/feature_discovery.py`
- `app/features/entry_point_contract.py`
- [PLUGIN_PACKAGES_ENTRY_POINTS.md](PLUGIN_PACKAGES_ENTRY_POINTS.md)
- [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](PLUGIN_FEATURE_PRODUCT_ACTIVATION.md)
- [PLUGIN_FEATURE_RELEASE_CONFIGURATION.md](PLUGIN_FEATURE_RELEASE_CONFIGURATION.md)
- [DEPENDENCY_GROUP_AVAILABILITY.md](DEPENDENCY_GROUP_AVAILABILITY.md)
- [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md)
