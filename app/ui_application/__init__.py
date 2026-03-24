"""
Presenter- und ViewModel-Anbindung zwischen Qt-Widgets (später QML) und Services.

Regeln:
- Presenter orchestriert app.services (oder Ports darauf).
- ViewModels/Presenter importieren keine Themes.
- ViewModels führen keine Fachlogik aus (kein Parsing von Stream-Chunks).
"""
