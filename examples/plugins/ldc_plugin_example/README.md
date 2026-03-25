# ldc-plugin-example

Minimales **externes** Python-Paket, das per setuptools-Entry-Point der Gruppe `linux_desktop_chat.features` einen `FeatureRegistrar` in den Host einhängt.

Voraussetzung: `linux-desktop-chat` (bzw. das Repo mit `app`) ist in derselben virtuellen Umgebung installiert (`pip install -e .` im Host-Repo).

```bash
# Im Host-Repo (einmalig)
pip install -e .

# Beispiel-Plugin
pip install -e examples/plugins/ldc_plugin_example

# Demo-Produktaktivierung (Host-Edition „plugin_example“, intern)
export LDC_EDITION=plugin_example

# Optional: zusätzliche/entzogene Freigabe per Host-YAML (siehe docs/architecture/PLUGIN_FEATURE_RELEASE_CONFIGURATION.md)
# export LDC_PLUGIN_RELEASE_CONFIG=/path/to/plugin_feature_release.yaml
```

Ausführliche Konventionen: [PLUGIN_AUTHORING_GUIDE.md](../../../docs/developer/PLUGIN_AUTHORING_GUIDE.md), [PLUGIN_PACKAGES_ENTRY_POINTS.md](../../../docs/architecture/PLUGIN_PACKAGES_ENTRY_POINTS.md), [PLUGIN_FEATURE_PRODUCT_ACTIVATION.md](../../../docs/architecture/PLUGIN_FEATURE_PRODUCT_ACTIVATION.md).
