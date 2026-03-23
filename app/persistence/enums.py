"""Fachliche Enumerations für Model-Usage (Persistenz als String)."""

from __future__ import annotations

from enum import Enum


class UsageType(str, Enum):
    CHAT = "chat"
    TOOL = "tool"
    EMBEDDING = "embedding"
    SYSTEM = "system"
    AGENT_RUN = "agent_run"


class UsageScopeType(str, Enum):
    GLOBAL = "global"
    USER = "user"
    WORKSPACE = "workspace"
    PROJECT = "project"
    SESSION = "session"
    CHAT = "chat"


class UsageStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class PeriodType(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    TOTAL = "total"


class QuotaScopeType(str, Enum):
    GLOBAL = "global"
    USER = "user"
    WORKSPACE = "workspace"
    PROJECT = "project"
    API_KEY = "api_key"
    MODEL = "model"
    OFFLINE_DEFAULT = "offline_default"


class QuotaMode(str, Enum):
    NONE = "none"
    WARN = "warn"
    HARD_BLOCK = "hard_block"


class QuotaSource(str, Enum):
    PROVIDER = "provider"
    API_KEY = "api_key"
    MANUAL = "manual"
    DEFAULT_OFFLINE = "default_offline"
    SYSTEM = "system"


class ModelAssetType(str, Enum):
    WEIGHTS = "weights"
    GGUF = "gguf"
    SAFETENSORS = "safetensors"
    TOKENIZER = "tokenizer"
    MODELFILE = "modelfile"
    ADAPTER = "adapter"
    LORA = "lora"
    CONFIG = "config"
    DIRECTORY = "directory"
    OTHER = "other"
