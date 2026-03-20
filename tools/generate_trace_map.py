#!/usr/bin/env python3
"""
Generate docs/TRACE_MAP.md – traceability map connecting Workspace, Code, Services, Help, Tests, QA.

Run: python3 tools/generate_trace_map.py
"""

from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "TRACE_MAP.md"


def _list_dirs(parent: Path) -> list[Path]:
    if not parent.exists():
        return []
    return sorted([p for p in parent.iterdir() if p.is_dir() and not p.name.startswith("_")])


def _list_files(parent: Path, ext: str = ".md") -> list[Path]:
    if not parent.exists():
        return []
    return sorted([p for p in parent.iterdir() if p.is_file() and p.suffix == ext])


def _parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
        if text.strip().startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                import yaml
                return yaml.safe_load(parts[1]) or {}
    except Exception:
        pass
    return {}


def _scan_help() -> list[tuple[str, str]]:
    """(topic_id, path)"""
    help_dir = PROJECT_ROOT / "help"
    result = []
    if not help_dir.exists():
        return result
    for md in help_dir.rglob("*.md"):
        rel = md.relative_to(help_dir)
        meta = _parse_frontmatter(md)
        topic_id = meta.get("id") or md.stem
        result.append((topic_id, str(rel).replace("\\", "/")))
    return sorted(result, key=lambda x: x[1])


def _scan_workspace_to_help() -> list[tuple[str, str]]:
    """(workspace_id, topic_id) from help articles with workspace frontmatter."""
    help_dir = PROJECT_ROOT / "help"
    result = []
    if not help_dir.exists():
        return result
    for md in help_dir.rglob("*.md"):
        meta = _parse_frontmatter(md)
        ws = meta.get("workspace")
        if ws:
            topic_id = meta.get("id") or md.stem
            result.append((ws, topic_id))
    return sorted(result, key=lambda x: (x[0], x[1]))


def _scan_workspaces_to_code() -> list[tuple[str, str]]:
    """(workspace_id, code_path)"""
    domains = PROJECT_ROOT / "app" / "gui" / "domains"
    result = []
    if not domains.exists():
        return result
    for domain_dir in _list_dirs(domains):
        domain_name = domain_dir.name
        # Screens
        for f in (domain_dir / "workspaces").iterdir() if (domain_dir / "workspaces").exists() else []:
            if f.suffix == ".py" and not f.name.startswith("_"):
                result.append((f"{domain_name}/{f.stem}", f"app/gui/domains/{domain_name}/workspaces/{f.name}"))
        # Direct workspace dirs (e.g. operations/chat)
        for sub in _list_dirs(domain_dir):
            if sub.name == "workspaces":
                continue
            for f in _list_files(sub, ".py"):
                if not f.name.startswith("_"):
                    result.append((f"{domain_name}/{sub.name}", f"app/gui/domains/{domain_name}/{sub.name}/{f.name}"))
    return result


def _scan_services() -> list[str]:
    services_dir = PROJECT_ROOT / "app" / "services"
    result = []
    if services_dir.exists():
        for f in services_dir.iterdir():
            if f.is_file() and f.suffix == ".py" and not f.name.startswith("_"):
                result.append(f"app/services/{f.name}")
    return sorted(result)


def _scan_tests() -> list[tuple[str, int]]:
    result = []
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        return result
    for sub in _list_dirs(tests_dir):
        count = len(list(sub.rglob("test_*.py")))
        if count > 0:
            result.append((f"tests/{sub.name}", count))
    return sorted(result, key=lambda x: -x[1])


def _scan_qa_artifacts() -> list[str]:
    qa_dir = PROJECT_ROOT / "docs" / "qa"
    result = []
    if not qa_dir.exists():
        return result
    for f in qa_dir.iterdir():
        if f.is_file() and f.suffix in (".md", ".json"):
            result.append(f.name)
    return sorted(result)[:30]  # Limit for readability


def generate() -> str:
    lines = [
        "# Trace Map – Linux Desktop Chat",
        "",
        f"*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "Run `python tools/generate_trace_map.py` to regenerate.",
        "",
        "Connects: **Workspace** → **Code** → **Services** → **Help** → **Tests** → **QA/audits**",
        "",
        "---",
        "",
        "## 1. Workspace → Code",
        "",
        "| Workspace | Code Path |",
        "|-----------|-----------|",
    ]
    for ws, code in _scan_workspaces_to_code()[:40]:
        lines.append(f"| {ws} | `{code}` |")
    if len(_scan_workspaces_to_code()) > 40:
        lines.append(f"| ... | ({len(_scan_workspaces_to_code()) - 40} more) |")
    lines.extend(["", "## 2. Services", ""])
    for s in _scan_services():
        lines.append(f"- `{s}`")
    # Workspace → Help
    ws_help = _scan_workspace_to_help()
    lines.extend(["", "## 3. Workspace → Help", ""])
    lines.append("| Workspace | Help Topic |")
    lines.append("|-----------|------------|")
    for ws, tid in ws_help:
        lines.append(f"| `{ws}` | `{tid}` |")
    if not ws_help:
        lines.append("- *(No workspace→help mapping yet)*")
    lines.extend(["", "## 4. Help Topics", ""])
    for tid, path in _scan_help():
        lines.append(f"- `help/{path}`")
    if not _scan_help():
        lines.append("- *(No help articles yet)*")
    lines.extend(["", "## 5. Test Suites", ""])
    for name, count in _scan_tests():
        lines.append(f"- `{name}/` — {count} test modules")
    lines.extend(["", "## 6. QA / Audits (docs/qa)", ""])
    for qa in _scan_qa_artifacts():
        lines.append(f"- `docs/qa/{qa}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    content = generate()
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
