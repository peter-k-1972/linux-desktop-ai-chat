#!/usr/bin/env python3
"""
CI-Helfer: Release-Matrix validieren und GitHub-Actions-Job-Matrizen erzeugen.

- Öffentliche Editionen: ``print-matrix-json`` (``OFFICIAL_BUILD_RELEASE_EDITION_NAMES``).
- Interne Plugin-Validierung: ``print-internal-plugin-matrix-json`` (``PLUGIN_VALIDATION_SMOKE_PROFILES``).

Keine hart kodierten Editionslisten in den Workflows — Export aus ``app.features.release_matrix``.

Voraussetzung: ``linux-desktop-chat-features`` installiert (Host-Monorepo: ``pip install -e ".[dev]"``
plus empfohlen ``pip install -e ./linux-desktop-chat-features`` für aktuelle ``dependency_groups``).
``validate_pep621_pyproject_alignment`` bezieht ``linux-desktop-chat-ui-contracts``,
``linux-desktop-chat-ui-runtime``, ``linux-desktop-chat-ui-themes``, ``linux-desktop-chat-pipelines``,
``linux-desktop-chat-providers``, ``linux-desktop-chat-utils``, ``linux-desktop-chat-infra``,
``linux-desktop-chat-runtime`` und
``linux-desktop-chat-cli`` aus
``project.dependencies`` ein — alle eingebetteten Distributionen sollten vor ``validate`` erreichbar sein
(CI: zusätzlich ``pip install -e ./linux-desktop-chat-ui-contracts``,
``pip install -e ./linux-desktop-chat-ui-runtime``, ``pip install -e ./linux-desktop-chat-ui-themes``,
``pip install -e ./linux-desktop-chat-pipelines``, ``pip install -e ./linux-desktop-chat-providers``,
``pip install -e ./linux-desktop-chat-utils``, ``pip install -e ./linux-desktop-chat-infra``,
``pip install -e ./linux-desktop-chat-runtime``,
``pip install -e ./linux-desktop-chat-cli``).
Auf GitHub Actions ist ``GITHUB_WORKSPACE`` gesetzt; optional ``LDC_REPO_ROOT`` gleich Workspace
für Matrix-Pfad-Checks.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# In-Tree-Features vor site-packages: sonst liefert ein veraltetes Wheel falsche _repo_root_for_matrix_checks().
_FEATURES_SRC = _REPO_ROOT / "linux-desktop-chat-features" / "src"
if _FEATURES_SRC.is_dir() and str(_FEATURES_SRC) not in sys.path:
    sys.path.insert(0, str(_FEATURES_SRC))
# Plugin-Smoke-Pfadprüfungen: immer diese Host-Wurzel (nicht setdefault — vermeidet falsches LDC aus der Shell).
os.environ["LDC_REPO_ROOT"] = str(_REPO_ROOT)
os.environ.setdefault("GITHUB_WORKSPACE", str(_REPO_ROOT))


def _validate_matrix() -> list[str]:
    from app.features.dependency_packaging import validate_pep621_pyproject_alignment
    from app.features.release_matrix import (
        build_release_matrix,
        release_matrix_to_json_dict,
        validate_release_matrix_consistency,
    )

    kwargs: dict[str, Path] = {}
    if "repo_root" in inspect.signature(validate_release_matrix_consistency).parameters:
        kwargs["repo_root"] = _REPO_ROOT
    errors = validate_release_matrix_consistency(**kwargs)
    if errors:
        return errors
    try:
        json.dumps(release_matrix_to_json_dict(build_release_matrix()))
    except (TypeError, ValueError) as exc:
        return [f"release_matrix JSON export failed: {exc}"]
    pe = validate_pep621_pyproject_alignment(_REPO_ROOT / "pyproject.toml")
    if pe:
        return pe
    return []


def cmd_validate() -> int:
    errors = _validate_matrix()
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print("release_matrix: validate OK", file=sys.stderr)
    return 0


def build_github_actions_matrix_payload() -> dict[str, list[dict[str, str]]]:
    """``{"include": [{"edition", "smoke_paths", "pip_extras"}, ...]}`` — ``pip_extras`` für ``pip install -e ".[...]"``."""
    from app.features.release_matrix import build_release_matrix

    errors = _validate_matrix()
    if errors:
        raise ValueError("release matrix invalid:\n" + "\n".join(errors))

    m = build_release_matrix()
    rows: list[dict[str, str]] = []
    for t in m.targets:
        extra_groups = sorted(frozenset(t.pip_runtime_extras) | frozenset(t.pip_ci_extras))
        rows.append(
            {
                "edition": t.edition_name,
                "smoke_paths": " ".join(t.suggested_smoke_paths),
                "pip_extras": ",".join(extra_groups),
            }
        )
    return {"include": rows}


def cmd_print_matrix_json() -> int:
    print(json.dumps(build_github_actions_matrix_payload(), separators=(",", ":")))
    return 0


def cmd_write_github_output() -> int:
    errors = _validate_matrix()
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        print("GITHUB_OUTPUT is not set (use --print-matrix-json locally)", file=sys.stderr)
        return 1
    payload = build_github_actions_matrix_payload()
    with open(path, "a", encoding="utf-8") as gh:
        gh.write("matrix<<MATRIX_EOF\n")
        gh.write(json.dumps(payload))
        gh.write("\nMATRIX_EOF\n")
    print("Wrote matrix to GITHUB_OUTPUT", file=sys.stderr)
    return 0


def cmd_print_internal_plugin_json() -> int:
    """JSON der internen Plugin-Validierungsprofile (kein CI-Matrix-Ersatz)."""
    from app.features.release_matrix import plugin_validation_profiles_to_json_dict

    print(json.dumps(plugin_validation_profiles_to_json_dict(), indent=2))
    return 0


def build_internal_plugin_github_actions_matrix_payload() -> dict[str, list[dict[str, str]]]:
    """Siehe ``app.features.release_matrix.build_internal_plugin_github_actions_matrix_payload``."""
    from app.features.release_matrix import build_internal_plugin_github_actions_matrix_payload as _payload

    return _payload()


def cmd_print_internal_plugin_matrix_json() -> int:
    """Kompakte ``{"include": [...]}``-Matrix für GitHub Actions (nur ``PLUGIN_VALIDATION_SMOKE_PROFILES``)."""
    errors = _validate_matrix()
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print(json.dumps(build_internal_plugin_github_actions_matrix_payload(), separators=(",", ":")))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "command",
        nargs="?",
        default="validate",
        choices=(
            "validate",
            "print-matrix-json",
            "print-internal-plugin-json",
            "print-internal-plugin-matrix-json",
            "write-github-output",
        ),
        help=(
            "validate (default) | print-matrix-json | print-internal-plugin-json | "
            "print-internal-plugin-matrix-json | write-github-output"
        ),
    )
    args = p.parse_args()
    if args.command == "validate":
        return cmd_validate()
    if args.command == "print-matrix-json":
        return cmd_print_matrix_json()
    if args.command == "print-internal-plugin-json":
        return cmd_print_internal_plugin_json()
    if args.command == "print-internal-plugin-matrix-json":
        return cmd_print_internal_plugin_matrix_json()
    return cmd_write_github_output()


if __name__ == "__main__":
    raise SystemExit(main())
