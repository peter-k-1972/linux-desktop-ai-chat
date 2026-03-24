"""
Release-Labels für Governance: App-, Backend- und UI-Contract-Version.

Diese Werte werden mit ``qml/theme_manifest.json`` abgeglichen, bevor die QML-Shell startet.
Bei Releases anpassen und die Kompatibilitätsmatrix unter ``docs/release/`` pflegen.
"""

from __future__ import annotations

# Semantische Release-Zeile der Anwendung (Widget- + Service-Stack).
APP_RELEASE_VERSION = "0.9.1"

# Gebündelte Backend-/Service-Kompatibilitätsmarke (vereinfachtes Governance-Label).
BACKEND_BUNDLE_VERSION = "0.9.1"

# UI-Contracts / Ports — Kompatibilitätsmarke für die QML↔Kern-Grenze.
UI_CONTRACTS_RELEASE_VERSION = "0.9.1"

# Öffentliche Shell-/Context-Bridge der QML-Library-GUI (Python-Seite, Governance-Label).
BRIDGE_INTERFACE_VERSION = "0.1.0"
