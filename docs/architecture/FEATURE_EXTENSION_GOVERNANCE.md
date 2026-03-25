# Feature-Extension-Governance (Discoverbare Registrare)

## Zweck

Discoverbare `FeatureRegistrar`-Instanzen (Plugins, Extensions, Entry Points, Umgebungsmodule)
unterliegen einem **kleinen, verbindlichen Vertrag**: Namen, Pflichtmetadaten, Kompatibilitätsfelder,
Abhängigkeiten zu **Dependency-Gruppen** und optionale **Feature-zu-Feature**-Anforderungen.

Dies ist **kein** Plugin-Lifecycle, **keine** Sandbox, **kein** Paketmanager, **keine** Signatur-
oder Trust-Infrastruktur und **keine** UI zur Verwaltung von Erweiterungen.

## Vertrag für discoverbare Registrare

### Pflicht (FeatureRegistrar)

- `get_descriptor() -> FeatureDescriptor` mit nicht leerer `description`.
- `name` im Deskriptor erfüllt die **Namensregeln** (siehe unten), abhängig von der Discovery-Quelle.
- `optional_dependencies` verweist nur auf **bekannte** Dependency-Gruppen (Registry), sofern nicht
  durch explizite Kompatibilitätsdaten überschrieben.

### Optional: `get_feature_compatibility() -> FeatureCompatibility | None`

Wenn die Methode fehlt oder `None` liefert, wird `FeatureCompatibility` aus dem Deskriptor **synthetisiert**:

- `requires_features`: leer (Default). Das Deskriptorfeld `dependencies` bezeichnet **App-Paket-
  Top-Level** (`core`, `gui`, …), **nicht** andere Feature-Namen — für Feature-zu-Feature nutzt
  man explizit `get_feature_compatibility()`.
- `declared_dependency_groups`: aus `optional_dependencies`.
- `api_version`: `"1"`.
- Host-Band und `incompatible_features`: leer bzw. nicht gesetzt.

Explizite Rückgabe muss eine Instanz von `FeatureCompatibility` sein (kein beliebiges Objekt).

### Discovery-Metadaten: `FeatureSourceKind`

Die Pipeline setzt pro Eintrag die **tatsächliche Quelle** (`builtin`, `plugin`, `extension`,
`entry_point`, `env`). Dieser Wert **gewinnt** gegenüber einem etwaigen `source_kind`-Feld in
von der Extension gelieferten Objekten — Spoofing der Quelle durch Erweiterungscode ist damit
ausgeschlossen.

`discover_feature_registrars()` liefert `DiscoveredFeatureRegistrar(registrar, source_kind)`.

## Namensregeln

| Quelle | Regel |
|--------|--------|
| **Builtin** | Name muss exakt in `ALL_BUILTIN_FEATURE_NAMES` (`app.features.feature_name_catalog`) stehen. |
| **Alle anderen** | Name darf **kein** Builtin-Name sein (reserviert). Zusätzlich: Muster `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$` **und** entweder Präfix `plugin_` oder `ext_` **oder** mindestens ein `.` (Namespace, z. B. `acme.audio_tools`). |

Beispiele: `knowledge_rag` (nur Builtin), `plugin_audio_tools`, `ext_audio_tools`, `vendor.feature_name`.

## Kompatibilitätsfelder (`FeatureCompatibility`)

| Feld | Bedeutung |
|------|-----------|
| `feature_name` | Muss mit `FeatureDescriptor.name` übereinstimmen. |
| `api_version` | Einfache String-Stufe der Extension-API (kein SemVer-Parser). |
| `min_host_version` / `max_host_version` | Optionales Band gegenüber `FEATURE_HOST_PLATFORM_VERSION` (einfacher Komponenten-Vergleich). |
| `requires_features` | Namen anderer Features, die **bereits gültig** sind (Builtins oder zuvor in derselben Discovery-Phase akzeptierte Extensions, siehe Reihenfolge). |
| `incompatible_features` | Kollision mit **bereits registrierten** Namen in derselben Phase → Registrar wird übersprungen. |
| `declared_dependency_groups` | Müssen im `DependencyGroupRegistry` existieren. |

## Validierung

Zentrale Funktionen in `app.features.feature_validation`:

- `validate_feature_descriptor`
- `validate_feature_compatibility`
- `validate_feature_registrar`
- `plan_registration_order` — filtert die Discovery-Liste (Builtins zuerst, dann Extensions in
  Eingabereihenfolge), prüft Duplikate im Batch und `incompatible_features`.

`register_discovered_feature_registrars` ruft `plan_registration_order` auf und registriert nur
die akzeptierten Registrare.

## Fail-soft-Verhalten

- **Builtins**: Weiterhin kritisch — Ladefehler der Builtin-Liste bricht `discover_feature_registrars` ab.
- **Extensions**: Validierungsfehler, unbekannte Dependency-Gruppen, Namensverstöße, Host-Band-
  Verletzungen, fehlende `requires_features`-Ziele, Duplikate und Inkompabilität → **Warnung im Log**,
  Eintrag wird **übersprungen**; die App lädt weiter mit den gültigen Features.

Reine **Validierungs-Warnungen** (`ValidationResult.warnings`) werden protokolliert; die Registrierung
erfolgt trotzdem, sofern keine Errors vorliegen (derzeit selten genutzt).

## Bewusst nicht gelöst (nächste sinnvolle Schritte)

- Lifecycle (Aktivieren/Deaktivieren/Upgrade zur Laufzeit außerhalb der Edition-Maske).
- Isolation / Sandbox, Code-Signing, Vertrauensketten.
- Paketinstallation, Marketplace, Plugin-Verwaltungs-UI.
- Vollständige SemVer-Semantik für `api_version` / Host-Version.
- Symmetrisches globales Modell für „Feature A verbietet B und B verbietet A“ (nur gerichtete
  `incompatible_features` beim Merge).

## Verwandte Doku

- `FEATURE_PLUGIN_DISCOVERY.md` — Quellen und Modulkontrakt.
- `FEATURE_SYSTEM.md` — FeatureRegistry / Editionen.
- `DEPENDENCY_GROUP_AVAILABILITY.md` — technische Verfügbarkeit.
