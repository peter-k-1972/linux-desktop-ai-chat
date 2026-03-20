"""
Smoke: Kontextmodus-Experiment.

Script läuft ohne Crash, alle 3 Modi vorhanden.
"""

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_context_experiment_runs_all_modes():
    """run_context_experiment: Script läuft, alle 3 Modi im Output."""
    import sys
    import tempfile

    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from scripts.qa.run_context_experiment import (
        MODES,
        PROMPT,
        run_experiment,
    )

    async def mock_chat_stream(*args, **kwargs):
        yield {"message": {"content": "Smoke-Antwort"}}

    def mock_chat(*args, **kwargs):
        return mock_chat_stream()

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir) / "experiments"
        out_dir.mkdir()
        out_file = out_dir / "experiment_001.json"

        with patch("scripts.qa.run_context_experiment.OUTPUT_DIR", out_dir), patch(
            "scripts.qa.run_context_experiment.OUTPUT_FILE", out_file
        ), patch(
            "app.providers.ollama_client.OllamaClient.chat",
            side_effect=mock_chat,
        ):
            result = await run_experiment()

    assert "prompt" in result
    assert result["prompt"] == PROMPT
    assert "runs" in result
    assert len(result["runs"]) == 3
    modes_in_output = {r["mode"] for r in result["runs"]}
    assert modes_in_output == set(MODES)
    for r in result["runs"]:
        assert "mode" in r
        assert "final_messages" in r
        assert "response" in r
        assert "Smoke-Antwort" in r["response"] or "Fehler" in r["response"]
