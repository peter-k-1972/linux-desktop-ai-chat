# Markiert das Verzeichnis 'app' als Python-Paket.
# Commit 2: app.features aus linux-desktop-chat-features; app.ui_contracts aus
# linux-desktop-chat-ui-contracts; app.pipelines aus linux-desktop-chat-pipelines;
# app.providers aus linux-desktop-chat-providers; app.cli aus linux-desktop-chat-cli
# (site-packages/editable). extend_path verbindet den Host-app-Baum mit weiteren app/*-Segmenten.
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
