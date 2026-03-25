"""
Workspace-spezifische UI-Verträge (Ebene B der Public Surface).

Öffentliche API: ``app.ui_contracts.workspaces.<modulname>`` — siehe
``docs/architecture/PACKAGE_UI_CONTRACTS_SPLIT_READY.md`` (Modultabelle, ``__all__``-Status).

Kleinere Module führen ein explizites ``__all__``; größere Workspace-Dateien (viele DTOs/Commands)
bleiben vorerst ohne Paket-``__all__`` (Public Surface über Modulinhalt + Doku).
"""
