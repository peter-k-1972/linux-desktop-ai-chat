"""
Settings-Modal — Ollama-Cloud-Provider (Qt-frei).

Der eigentliche API-Vertrag ist :class:`OllamaProviderSettingsPort`; diese DTOs
dienen Dokumentation und optionalen Tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class OllamaCloudApiKeyValidateRequested:
    """Anfrage zur Key-Prüfung (für spätere Presenter-Anbindung)."""

    api_key: str


OllamaCloudApiKeyValidationKind = Literal["valid", "invalid", "error"]


@dataclass(frozen=True, slots=True)
class OllamaCloudApiKeyValidationResult:
    """Ergebnis der asynchronen Key-Prüfung (Presenter → Sink, kein Qt in der Nutzlast)."""

    kind: OllamaCloudApiKeyValidationKind
    message: str
