# Markiert das Verzeichnis 'app' als Python-Paket.
# Commit 2: app.features aus linux-desktop-chat-features; app.ui_contracts aus
# linux-desktop-chat-ui-contracts; app.pipelines aus linux-desktop-chat-pipelines;
# app.providers aus linux-desktop-chat-providers; app.utils aus linux-desktop-chat-utils;
# app.cli aus linux-desktop-chat-cli; app.ui_themes aus linux-desktop-chat-ui-themes;
# app.ui_runtime aus linux-desktop-chat-ui-runtime;
# app.debug / app.metrics / app.tools aus linux-desktop-chat-infra (Welle 9).
# app.runtime / app.extensions aus linux-desktop-chat-runtime (Welle 10).
# (site-packages/editable). extend_path verbindet den Host-app-Baum mit weiteren app/*-Segmenten.
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
