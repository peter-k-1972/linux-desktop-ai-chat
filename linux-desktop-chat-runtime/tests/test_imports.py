from __future__ import annotations


def test_runtime_lifecycle_importable() -> None:
    from app.runtime.lifecycle import (
        register_shutdown_hooks,
        try_acquire_single_instance_lock,
    )

    assert try_acquire_single_instance_lock is not None
    assert register_shutdown_hooks is not None


def test_runtime_model_invocation_importable() -> None:
    from app.runtime.model_invocation import MODEL_INVOCATION_CHUNK_KEY

    assert MODEL_INVOCATION_CHUNK_KEY == "model_invocation"


def test_extensions_package_importable() -> None:
    import app.extensions

    assert app.extensions is not None
