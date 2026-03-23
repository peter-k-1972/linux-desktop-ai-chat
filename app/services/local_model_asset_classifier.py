"""
Klassifikation lokaler Modell-Artefakte nach Pfad/Suffix.

Keine Dateiinhalte lesen; nur Pfad/Name. Werte entsprechen ModelAssetType.
"""

from __future__ import annotations

from pathlib import Path

from app.persistence.enums import ModelAssetType

# Reihenfolge: spezifisch vor allgemein
_SUFFIX_MAP: tuple[tuple[str, str], ...] = (
    (".gguf", ModelAssetType.GGUF.value),
    (".gguf.part", ModelAssetType.GGUF.value),
    (".safetensors", ModelAssetType.SAFETENSORS.value),
    (".bin", ModelAssetType.WEIGHTS.value),  # oft weights; konservativ
    (".pt", ModelAssetType.WEIGHTS.value),
    (".pth", ModelAssetType.WEIGHTS.value),
    (".onnx", ModelAssetType.WEIGHTS.value),
    (".ckpt", ModelAssetType.WEIGHTS.value),
    (".h5", ModelAssetType.WEIGHTS.value),
    (".npz", ModelAssetType.WEIGHTS.value),
)

_NAME_HINTS: tuple[tuple[str, str], ...] = (
    ("modelfile", ModelAssetType.MODELFILE.value),
    ("tokenizer", ModelAssetType.TOKENIZER.value),
    ("vocab", ModelAssetType.TOKENIZER.value),
    ("merges", ModelAssetType.TOKENIZER.value),
    ("adapter", ModelAssetType.ADAPTER.value),
    ("lora", ModelAssetType.LORA.value),
    ("peft", ModelAssetType.LORA.value),
    ("adapter_config", ModelAssetType.CONFIG.value),
    ("config.json", ModelAssetType.CONFIG.value),
    ("generation_config.json", ModelAssetType.CONFIG.value),
    ("params.json", ModelAssetType.CONFIG.value),
)


def classify_path(path: Path, *, is_dir: bool) -> str:
    """
    Liefert ModelAssetType-String.

    Verzeichnisse: directory, außer bekannte Modell-Container-Namen bleiben directory.
    """
    if is_dir:
        return ModelAssetType.DIRECTORY.value

    name_lower = path.name.lower()
    for suf, atype in _SUFFIX_MAP:
        if name_lower.endswith(suf):
            return atype

    for hint, atype in _NAME_HINTS:
        if hint in name_lower:
            return atype

    if name_lower in ("modelfile", "dockerfile") or name_lower.endswith("modelfile"):
        return ModelAssetType.MODELFILE.value

    return ModelAssetType.OTHER.value
