"""
Verbindlicher Entry-Point-Vertrag für externe Feature-Pakete (PEP 621 / setuptools).

Gruppe (Distribution-Metadata, ``importlib.metadata``):

    linux_desktop_chat.features

Jeder Eintrag ist ein setuptools-Entry-Point im Format ``qualified.module:target``.

Empfohlene Primärform (``target``)
    Aufrufbare Funktion ``get_feature_registrars()`` ohne Argumente, die eine
    Sequenz von :class:`~app.features.registrar.FeatureRegistrar` (oder einen
    einzelnen Registrar) zurückgibt.

Legacy / alternativ (``target``)
    - Konstante ``FEATURE_REGISTRARS`` (Liste/Tuple) — nur sinnvoll, wenn
      ``target`` auf das **Modul** zeigt und die Discovery ``FEATURE_REGISTRARS``
      ausliest (siehe :func:`app.features.feature_discovery.discover_feature_registrars`).
    - Jedes andere nicht-aufrufbare Objekt, das bereits eine Sequenz von
      Registraren ist (nach dem Laden per ``EntryPoint.load()``).

Modul als ``target`` (Fallback)
    Zeigt der Entry Point auf ein Modulobjekt, wendet die Discovery dieselbe
    Extraktion wie bei Umgebungsmodulen an: zuerst ``get_feature_registrars()``,
    dann ``FEATURE_REGISTRARS``.

Hinweis: Externe Pakete liefern **Features** (Registrare), keine Editionen.
Editionen bleiben Host-seitig; entdeckte Features sind nicht automatisch aktiv,
wenn sie nicht in der gewählten Edition enthalten sind.
"""

from __future__ import annotations

#: ``importlib.metadata``-Gruppe für ``entry_points(group=...)``.
ENTRY_POINT_GROUP: str = "linux_desktop_chat.features"

#: Empfohlener Attribut-/Funktionsname auf dem Exportmodul (Doku / Konvention).
ENTRY_POINT_PRIMARY_CALLABLE: str = "get_feature_registrars"

#: Legacy-Konstantenname auf dem Exportmodul (Modul-Scan / Modul-Fallback).
ENTRY_POINT_LEGACY_REGISTRARS_ATTR: str = "FEATURE_REGISTRARS"
