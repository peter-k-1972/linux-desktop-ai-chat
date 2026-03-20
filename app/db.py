"""
Re-Export für Rückwärtskompatibilität.
DatabaseManager wurde nach app.core.db verschoben.
"""

from app.core.db.database_manager import DatabaseManager

__all__ = ["DatabaseManager"]
