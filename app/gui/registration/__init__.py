"""
Modulare Screen-Registrierung (Phase 1).

register_all_screens() in app.gui.bootstrap delegiert hierher.
"""

from app.gui.registration.screen_registrar import register_all_navigation_area_screens

__all__ = ["register_all_navigation_area_screens"]
