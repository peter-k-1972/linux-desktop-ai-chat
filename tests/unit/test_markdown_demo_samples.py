"""Demo-Markdown-Dateien sind vorhanden und laden."""

from app.gui.devtools.markdown_demo_samples import (
    DEMO_MARKDOWN_DIR,
    MARKDOWN_DEMO_SAMPLES,
    load_sample_text,
)


def test_demo_markdown_dir_exists():
    assert DEMO_MARKDOWN_DIR.is_dir()


def test_all_samples_load_non_trivial():
    for s in MARKDOWN_DEMO_SAMPLES:
        text = load_sample_text(s.sample_id)
        assert len(text) > 20, s.sample_id
        path = DEMO_MARKDOWN_DIR / s.filename
        assert path.is_file(), path


def test_sample_files_use_project_app_resources():
    assert "resources" in DEMO_MARKDOWN_DIR.parts
    assert DEMO_MARKDOWN_DIR.name == "demo_markdown"
