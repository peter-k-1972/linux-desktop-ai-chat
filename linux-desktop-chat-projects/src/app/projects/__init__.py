"""
Öffentliche Importoberfläche von ``app.projects``.

Split-Vorbereitung:
- Paket-Root bleibt bewusst leichtgewichtig und re-exportiert keine Laufzeitobjekte.
- Kanonische Consumer-Pfade liegen eine Ebene tiefer in den dokumentierten Public-Modulen.
- Die Domain enthält aktuell bewusst noch die kleine Fachkante
  ``app.projects.models`` -> ``app.chat.context_policies``.
"""

__all__ = (
    "controlling",
    "lifecycle",
    "milestones",
    "models",
    "monitoring_display",
)
