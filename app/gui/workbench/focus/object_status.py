"""Consistent object lifecycle status for tabs, inspector, and explorer hints."""

from __future__ import annotations

from enum import Enum


class ObjectStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    INDEXING = "INDEXING"
    SYNCING = "SYNCING"
