"""Minimaler Smoke-Test: Paket-Root ohne models (kein app.chat nötig)."""


def test_import_projects_root() -> None:
    import app.projects

    assert "models" in app.projects.__all__
