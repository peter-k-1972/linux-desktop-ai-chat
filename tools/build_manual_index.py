#!/usr/bin/env python3
"""
Build machine-readable and human-readable manual index:
  docs_manual/index/manual_index.json
  docs_manual/index/manual_index.md

Mapping is declared explicitly below (no LLM, no fuzzy matching).
Run: python3 tools/build_manual_index.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "docs_manual" / "index"
OUT_JSON = OUT_DIR / "manual_index.json"
OUT_MD = OUT_DIR / "manual_index.md"

UnitType = Literal["module", "workflow", "role", "help", "architecture"]
OwnerLayer = Literal[
    "application",
    "gui",
    "services",
    "core",
    "data",
    "tooling",
    "platform",
    "documentation",
    "cross_cutting",
]
Status = Literal["documented", "partial", "missing"]


@dataclass(frozen=True)
class UnitSpec:
    id: str
    type: UnitType
    owner_layer: OwnerLayer
    primary_manual_path: str | None
    source_code_paths: tuple[str, ...] = ()
    related_docs: tuple[str, ...] = ()
    related_help: tuple[str, ...] = ()
    related_tests: tuple[str, ...] = ()
    requires_primary_manual: bool = True


# --- Explicit catalogue (Handbuch + Code + Langdoku + Help + Tests) -----------------

UNITS: tuple[UnitSpec, ...] = (
    UnitSpec(
        id="chat",
        type="module",
        owner_layer="application",
        primary_manual_path="docs_manual/modules/chat/README.md",
        source_code_paths=(
            "app/gui/domains/operations/chat/",
            "app/services/chat_service.py",
            "app/core/commands/chat_commands.py",
            "app/chat/",
        ),
        related_docs=(
            "docs_manual/modules/chat/README.md",
            "docs/FEATURES/chat.md",
            "docs/02_user_manual/ai_studio.md",
        ),
        related_help=("help/operations/chat_overview.md",),
        related_tests=(
            "tests/ui/test_chat_message_rendering.py",
            "tests/unit/test_chat_extract_content_streaming.py",
        ),
    ),
    UnitSpec(
        id="context",
        type="module",
        owner_layer="core",
        primary_manual_path="docs_manual/modules/context/README.md",
        source_code_paths=(
            "app/context/",
            "app/chat/context.py",
            "app/chat/context_limits.py",
            "app/chat/context_profiles.py",
        ),
        related_docs=(
            "docs_manual/modules/context/README.md",
            "docs/FEATURES/context.md",
        ),
        related_help=("help/settings/settings_chat_context.md",),
        related_tests=(
            "tests/chat/test_context_modes.py",
            "tests/context/test_context_serializer.py",
        ),
    ),
    UnitSpec(
        id="settings",
        type="module",
        owner_layer="gui",
        primary_manual_path="docs_manual/modules/settings/README.md",
        source_code_paths=(
            "app/gui/domains/settings/",
            "app/core/config/settings.py",
            "app/core/config/settings_backend.py",
        ),
        related_docs=(
            "docs_manual/modules/settings/README.md",
            "docs/FEATURES/settings.md",
            "docs/04_architecture/SETTINGS_ARCHITECTURE.md",
        ),
        related_help=(
            "help/settings/settings_overview.md",
            "help/settings/settings_rag.md",
            "help/settings/settings_prompts.md",
        ),
    ),
    UnitSpec(
        id="providers",
        type="module",
        owner_layer="services",
        primary_manual_path="docs_manual/modules/providers/README.md",
        source_code_paths=(
            "linux-desktop-chat-providers/src/app/providers/",
            "linux-desktop-chat-utils/src/app/utils/",
            "app/services/model_service.py",
        ),
        related_docs=(
            "docs_manual/modules/providers/README.md",
            "docs/FEATURES/providers.md",
        ),
        related_help=(
            "help/control_center/cc_models.md",
            "help/control_center/cc_providers.md",
        ),
    ),
    UnitSpec(
        id="agents",
        type="module",
        owner_layer="application",
        primary_manual_path="docs_manual/modules/agents/README.md",
        source_code_paths=(
            "app/agents/",
            "app/services/agent_service.py",
            "app/gui/domains/operations/agent_tasks/",
        ),
        related_docs=(
            "docs_manual/modules/agents/README.md",
            "docs/FEATURES/agents.md",
        ),
        related_help=(
            "help/operations/agents_overview.md",
            "help/control_center/control_center_agents.md",
        ),
    ),
    UnitSpec(
        id="rag",
        type="module",
        owner_layer="data",
        primary_manual_path="docs_manual/modules/rag/README.md",
        source_code_paths=(
            "app/rag/",
            "app/gui/domains/operations/knowledge/",
        ),
        related_docs=(
            "docs_manual/modules/rag/README.md",
            "docs/FEATURES/rag.md",
        ),
        related_help=(
            "help/operations/knowledge_overview.md",
            "help/control_center/cc_data_stores.md",
        ),
    ),
    UnitSpec(
        id="chains",
        type="module",
        owner_layer="core",
        primary_manual_path="docs_manual/modules/chains/README.md",
        source_code_paths=(
            "linux-desktop-chat-pipelines/src/app/pipelines/",
            "app/commands/",
        ),
        related_docs=(
            "docs_manual/modules/chains/README.md",
            "docs/FEATURES/chains.md",
        ),
        related_help=("help/control_center/cc_tools.md",),
    ),
    UnitSpec(
        id="prompts",
        type="module",
        owner_layer="application",
        primary_manual_path="docs_manual/modules/prompts/README.md",
        source_code_paths=(
            "app/prompts/",
            "app/gui/domains/operations/prompt_studio/",
        ),
        related_docs=(
            "docs_manual/modules/prompts/README.md",
            "docs/FEATURES/prompts.md",
            "docs/02_user_manual/prompts.md",
        ),
        related_help=(
            "help/operations/prompt_studio_overview.md",
            "help/settings/settings_prompts.md",
        ),
    ),
    UnitSpec(
        id="gui",
        type="module",
        owner_layer="gui",
        primary_manual_path="docs_manual/modules/gui/README.md",
        source_code_paths=(
            "app/gui/shell/",
            "app/gui/navigation/",
            "app/gui/domains/",
            "app/gui/commands/",
        ),
        related_docs=(
            "docs_manual/modules/gui/README.md",
            "docs/ARCHITECTURE.md",
        ),
        related_help=(
            "help/getting_started/introduction.md",
            "help/control_center/control_center_overview.md",
        ),
    ),
    UnitSpec(
        id="cli_tools",
        type="module",
        owner_layer="tooling",
        primary_manual_path="docs_manual/README.md",
        source_code_paths=(
            "linux-desktop-chat-cli/src/app/cli/",
            "tools/",
        ),
        related_docs=(
            "docs_manual/README.md",
            "docs/05_developer_guide/README.md",
            "docs/DEVELOPER_GUIDE.md",
        ),
        related_help=(),
        related_tests=("tests/helpers/",),
    ),
    UnitSpec(
        id="deployment",
        type="module",
        owner_layer="platform",
        primary_manual_path="README.md",
        source_code_paths=(
            "requirements.txt",
            "main.py",
        ),
        related_docs=(
            "README.md",
            "docs/05_developer_guide/README.md",
            "docs/USER_GUIDE.md",
        ),
        related_help=("help/troubleshooting/troubleshooting.md",),
        related_tests=(),
    ),
    # --- Workflows (separate index rows) ---
    UnitSpec(
        id="chat_usage",
        type="workflow",
        owner_layer="application",
        primary_manual_path="docs_manual/workflows/chat_usage.md",
        source_code_paths=("app/gui/domains/operations/chat/", "app/services/chat_service.py"),
        related_docs=(
            "docs_manual/workflows/chat_usage.md",
            "docs/FEATURES/chat.md",
        ),
        related_help=("help/operations/chat_overview.md",),
    ),
    UnitSpec(
        id="context_control",
        type="workflow",
        owner_layer="core",
        primary_manual_path="docs_manual/workflows/context_control.md",
        source_code_paths=("app/context/", "app/chat/context.py", "app/services/chat_service.py"),
        related_docs=(
            "docs_manual/workflows/context_control.md",
            "docs/FEATURES/context.md",
        ),
        related_help=("help/settings/settings_chat_context.md",),
    ),
    UnitSpec(
        id="agent_usage",
        type="workflow",
        owner_layer="application",
        primary_manual_path="docs_manual/workflows/agent_usage.md",
        source_code_paths=(
            "app/agents/",
            "app/gui/domains/operations/agent_tasks/",
            "app/services/agent_service.py",
        ),
        related_docs=(
            "docs_manual/workflows/agent_usage.md",
            "docs/FEATURES/agents.md",
        ),
        related_help=("help/operations/agents_overview.md",),
    ),
    UnitSpec(
        id="settings_usage",
        type="workflow",
        owner_layer="gui",
        primary_manual_path="docs_manual/workflows/settings_usage.md",
        source_code_paths=("app/gui/domains/settings/", "app/core/config/settings.py"),
        related_docs=(
            "docs_manual/workflows/settings_usage.md",
            "docs/FEATURES/settings.md",
        ),
        related_help=("help/settings/settings_overview.md",),
    ),
    # --- Roles ---
    UnitSpec(
        id="admin",
        type="role",
        owner_layer="documentation",
        primary_manual_path="docs_manual/roles/admin/README.md",
        source_code_paths=(),
        related_docs=("docs_manual/roles/admin/README.md",),
        related_help=("help/qa_governance/qa_overview.md",),
    ),
    UnitSpec(
        id="business",
        type="role",
        owner_layer="documentation",
        primary_manual_path="docs_manual/roles/business/README.md",
        source_code_paths=(),
        related_docs=("docs_manual/roles/business/README.md",),
        related_help=(),
    ),
    UnitSpec(
        id="entwickler",
        type="role",
        owner_layer="documentation",
        primary_manual_path="docs_manual/roles/entwickler/README.md",
        source_code_paths=("app/",),
        related_docs=(
            "docs_manual/roles/entwickler/README.md",
            "docs/DEVELOPER_GUIDE.md",
        ),
        related_help=(),
    ),
    UnitSpec(
        id="fachanwender",
        type="role",
        owner_layer="documentation",
        primary_manual_path="docs_manual/roles/fachanwender/README.md",
        source_code_paths=(),
        related_docs=(
            "docs_manual/roles/fachanwender/README.md",
            "docs/USER_GUIDE.md",
        ),
        related_help=("help/getting_started/introduction.md",),
    ),
    # --- Architecture (Handbuch + Querschnitt) ---
    UnitSpec(
        id="architecture",
        type="architecture",
        owner_layer="cross_cutting",
        primary_manual_path="docs_manual/architecture.md",
        source_code_paths=(
            "app/core/navigation/",
            "app/gui/shell/main_window.py",
        ),
        related_docs=(
            "docs_manual/architecture.md",
            "docs_manual/standards.md",
            "docs/ARCHITECTURE.md",
            "docs/SYSTEM_MAP.md",
        ),
        related_help=(),
    ),
    # --- Help system surface (resolver + topics) ---
    UnitSpec(
        id="in_app_help",
        type="help",
        owner_layer="gui",
        primary_manual_path=None,
        requires_primary_manual=False,
        source_code_paths=(
            "app/help/help_index.py",
            "app/help/manual_resolver.py",
            "app/help/help_window.py",
            "app/core/navigation/help_topic_resolver.py",
        ),
        related_docs=("docs_manual/README.md",),
        related_help=(),  # filled at build from help/**/*.md
    ),
)


def _expand_related_tests(root: Path, paths: tuple[str, ...]) -> tuple[str, ...]:
    out: list[str] = []
    for p in paths:
        if p.endswith("/"):
            d = root / p.rstrip("/")
            if d.is_dir():
                for f in sorted(d.rglob("test_*.py"))[:20]:
                    out.append(str(f.relative_to(root)).replace("\\", "/"))
        else:
            out.append(p)
    seen: set[str] = set()
    uniq: list[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return tuple(uniq)


def _exists(root: Path, rel: str) -> bool:
    p = root / rel
    return p.is_file() or p.is_dir()


def _resolve_help_globs(root: Path) -> tuple[str, ...]:
    h = root / "help"
    if not h.is_dir():
        return ()
    files = sorted(
        str(x.relative_to(root)).replace("\\", "/")
        for x in h.rglob("*.md")
        if x.is_file()
    )
    return tuple(files)


def compute_status(
    root: Path,
    spec: UnitSpec,
    related_help_effective: tuple[str, ...],
    related_tests_effective: tuple[str, ...],
) -> Status:
    if spec.requires_primary_manual:
        pm = spec.primary_manual_path
        if not pm or not _exists(root, pm):
            return "missing"

    check_paths: list[str] = []
    check_paths.extend(spec.source_code_paths)
    check_paths.extend(spec.related_docs)
    check_paths.extend(related_help_effective)
    check_paths.extend(related_tests_effective)

    if spec.id == "in_app_help" and not related_help_effective:
        return "partial"

    missing = [p for p in check_paths if p and not _exists(root, p)]
    if not missing:
        return "documented"
    return "partial"


def build_records(root: Path) -> list[dict]:
    help_all = _resolve_help_globs(root)
    records: list[dict] = []

    for spec in UNITS:
        rh = spec.related_help
        if spec.id == "in_app_help":
            rh = help_all

        rt_tuple = _expand_related_tests(root, spec.related_tests)

        status = compute_status(root, spec, rh, rt_tuple)

        rec = {
            "id": spec.id,
            "type": spec.type,
            "owner_layer": spec.owner_layer,
            "primary_manual_path": spec.primary_manual_path,
            "source_code_paths": list(spec.source_code_paths),
            "related_docs": list(spec.related_docs),
            "related_help": list(rh),
            "related_tests": list(rt_tuple),
            "status": status,
        }
        records.append(rec)

    return records


def write_json(path: Path, records: list[dict]) -> None:
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "tools/build_manual_index.py",
        "project_root_hint": ".",
        "units": records,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _md_cell(s: str, max_len: int = 56) -> str:
    t = s.replace("|", "\\|").replace("\n", " ")
    if len(t) > max_len:
        t = t[: max_len - 1] + "…"
    return t


def write_markdown(path: Path, records: list[dict]) -> None:
    lines = [
        "# Manual index",
        "",
        f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}* — `python3 tools/build_manual_index.py`",
        "",
        "| ID | Typ | Code | Doku | Help | Status |",
        "|----|-----|------|------|------|--------|",
    ]
    for r in records:
        code = ", ".join(r["source_code_paths"][:2])
        if len(r["source_code_paths"]) > 2:
            code += ", …"
        docs = ", ".join(r["related_docs"][:2])
        if len(r["related_docs"]) > 2:
            docs += ", …"
        help_s = ", ".join(r["related_help"][:1])
        if len(r["related_help"]) > 1:
            help_s += ", …"
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(r["id"], 20),
                    _md_cell(r["type"], 14),
                    _md_cell(code or "—", 56),
                    _md_cell(docs or "—", 56),
                    _md_cell(help_s or "—", 40),
                    _md_cell(r["status"], 12),
                ]
            )
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    records = build_records(PROJECT_ROOT)
    write_json(OUT_JSON, records)
    write_markdown(OUT_MD, records)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
