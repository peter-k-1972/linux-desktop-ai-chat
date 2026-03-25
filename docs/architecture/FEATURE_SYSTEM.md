# Feature-System (Phase 1 / 2)

## Zweck

Das Feature-System beschreibt **logische Produkt-Features** zentral unter `app/features/`. **Phase 2** ergänzt **FeatureRegistrar** als verbindliche Registrierungseinheit — siehe [FEATURE_REGISTRAR_ARCHITECTURE.md](FEATURE_REGISTRAR_ARCHITECTURE.md). **Editionen / Dependency-Gruppen** (deklarativ, ohne Gating): [EDITION_AND_DEPENDENCY_MANIFESTS.md](EDITION_AND_DEPENDENCY_MANIFESTS.md).

Es ist die **technische Grundlage** für:

- spätere **Editionen** (welche Features aktiv sind),
- **modulare Screen-Registrierung** (`app/gui/registration/`),
- **optionale Dependencies** und Import-Gates (Phase 3+),
- Abgleich mit der **vertikalen Paketarchitektur** (Zielpakete `ldt_*` im SOLL-Bericht).

Phase 1: **Registrierung und Dokumentation nur** — keine Feature-Gates, keine Änderung des sichtbaren Verhaltens der Shell.

## Komponenten

| Modul | Rolle |
|--------|--------|
| `app/features/descriptors.py` | `FeatureDescriptor` (Phase 2: `enabled_by_default`, Nav/Command-IDs) |
| `app/features/registrar.py` | `FeatureRegistrar`-Vertrag |
| `app/features/registry.py` | `FeatureRegistry`, `apply_feature_screen_registrars` |
| `app/features/builtins.py` | Lazy-Laden der GUI-Registrare (`importlib`) |
| `app/features/feature_manifest.py` | `iter_default_feature_descriptors()` (lazy über Default-Registry) |
| `app/features/feature_registry.py` | Re-Exporte aus `registry.py` |
| `app/features/feature_flags.py` | `is_feature_experimental` |
| `app/gui/registration/feature_builtins.py` | Eingebaute `FeatureRegistrar`-Implementierungen |
| `app/gui/registration/screen_registrar.py` | Weiterhin Screen-Hilfsfunktionen (von Registraren genutzt) |

## Beziehung zur Paketarchitektur

- `FeatureDescriptor.packages` nennt **informative** Zuordnungen zu `app/`-Top-Level-Paketen (z. B. `chat`, `rag`). Sie sind **keine** Import-Anweisungen.
- Später können Zielpakete (`ldt_kernel`, `ldt_knowledge`, …) **1:1 oder n:1** auf Feature-IDs abgebildet werden.

## Beziehung zu Editionen

- Eine **Edition** (Phase 4+) wählt eine Teilmenge aktiver Features und optional installierte Extras.
- Phase 1: **alle** Deskriptoren werden mit `active=True` registriert — entspricht der **vollen** Desktop-Shell.

## Bootstrap-Reihenfolge (Widget-GUI)

In `run_gui_shell._run_widget_gui`:

1. `init_infrastructure(...)`
2. `set_feature_registry(build_default_feature_registry())`
3. später im Fenster-Lebenszyklus: `register_all_screens()` → modulare Registrare

## Beispiel `FeatureDescriptor`

```python
FeatureDescriptor(
    name="knowledge",
    description="Knowledge / RAG (Operations Knowledge-Workspace).",
    packages=("rag", "services"),
    screens=("operations",),
    services=("KnowledgeService",),
    dependencies=("core",),
    optional_dependencies=("rag",),
    experimental_flag=False,
)
```

## Core → GUI (bekannte Ausnahme)

`app.core` darf laut Architektur-Guards **nicht** `app.gui` importieren. **Ausnahme** (bis Entkopplung): `core/context/project_context_manager.py` — siehe `tests/architecture/arch_guard_config.py` (`KNOWN_IMPORT_EXCEPTIONS`). Ziel bleibt ein **domänischer Event-Port** statt direkter GUI-Events (Roadmap).

## Referenzen

- `tests/architecture/test_feature_system_guards.py` — Isolation `app.features`, Registrierungsschicht
- `tests/unit/features/test_feature_registry.py` — Registry-Verhalten
