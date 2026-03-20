#!/usr/bin/env python3
"""
Generate docs/SYSTEM_MAP.md – technical overview of the project.

Scans the repository and produces a structured map including:
- Application structure
- Workspaces
- Services
- Integrations
- Help topics
- Test suites

Run: python tools/generate_system_map.py
"""

from pathlib import Path
import re
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "SYSTEM_MAP.md"


def _list_dirs(parent: Path, pattern: str = "*") -> list[Path]:
    """List subdirectories matching pattern."""
    if not parent.exists():
        return []
    return sorted([p for p in parent.iterdir() if p.is_dir() and not p.name.startswith("_")])


def _list_files(parent: Path, ext: str = ".py") -> list[Path]:
    """List files with given extension."""
    if not parent.exists():
        return []
    return sorted([p for p in parent.iterdir() if p.is_file() and p.suffix == ext])


def _list_md(parent: Path) -> list[Path]:
    """List markdown files."""
    return _list_files(parent, ".md")


def _extract_classes(path: Path, base_name: str) -> list[str]:
    """Extract class names from Python file that match base_name pattern."""
    classes = []
    try:
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(rf"class\s+(\w*{re.escape(base_name)}\w*)\s*[:(]", text):
            classes.append(m.group(1))
    except Exception:
        pass
    return classes


def _scan_workspaces() -> dict[str, list[str]]:
    """Scan app/gui/domains for screens and workspaces."""
    domains = PROJECT_ROOT / "app" / "gui" / "domains"
    result: dict[str, list[str]] = {}
    if not domains.exists():
        return result

    for domain_dir in _list_dirs(domains):
        domain_name = domain_dir.name
        result[domain_name] = []

        # Screens (e.g. operations_screen.py -> OperationsScreen)
        for f in _list_files(domain_dir, ".py"):
            if f.name.startswith("_"):
                continue
            for cls in _extract_classes(f, "Screen"):
                result[domain_name].append(f"Screen: {cls}")

        # Workspaces subdir (control_center, qa_governance, runtime_debug, settings)
        workspaces_dir = domain_dir / "workspaces"
        if workspaces_dir.exists():
            for f in _list_files(workspaces_dir, ".py"):
                if f.name.startswith("_") or "base" in f.name:
                    continue
                for cls in _extract_classes(f, "Workspace"):
                    result[domain_name].append(f"  Workspace: {cls}")

        # Domain subdirs that contain workspaces (e.g. operations/chat/, operations/knowledge/)
        for sub in _list_dirs(domain_dir):
            if sub.name == "workspaces":
                continue  # Already handled above
            for f in _list_files(sub, ".py"):
                if f.name.startswith("_") or "base_" in f.name:
                    continue
                for cls in _extract_classes(f, "Workspace"):
                    if "Workspace" in cls:
                        result[domain_name].append(f"  Workspace: {cls} ({sub.name})")

    return result


def _scan_services() -> list[str]:
    """Scan app/services and app for service modules."""
    services_dir = PROJECT_ROOT / "app" / "services"
    result = []
    if services_dir.exists():
        for f in _list_files(services_dir, ".py"):
            if not f.name.startswith("_"):
                result.append(f.stem)
    # Also app-level services
    for name in ["rag", "agents", "prompts", "llm"]:
        p = PROJECT_ROOT / "app" / name
        if p.exists() and (p / "service.py").exists() or (p / "__init__.py").exists():
            result.append(name)
    return sorted(set(result))


def _scan_integrations() -> list[str]:
    """Scan app/providers and similar for integrations."""
    result = []
    providers = PROJECT_ROOT / "app" / "providers"
    if providers.exists():
        for f in _list_files(providers, ".py"):
            if not f.name.startswith("_"):
                result.append(f"providers.{f.stem}")
    # RAG uses ChromaDB
    if (PROJECT_ROOT / "app" / "rag").exists():
        result.append("ChromaDB (RAG)")
    result.append("Ollama (LLM)")
    return sorted(set(result))


def _scan_help_topics() -> list[str]:
    """Scan help/ for articles."""
    help_dir = PROJECT_ROOT / "help"
    result = []
    if not help_dir.exists():
        return result
    for md in help_dir.rglob("*.md"):
        rel = md.relative_to(help_dir)
        result.append(str(rel).replace("\\", "/"))
    return sorted(result)


def _scan_tests() -> dict[str, list[str]]:
    """Scan tests/ for test structure."""
    tests_dir = PROJECT_ROOT / "tests"
    result: dict[str, list[str]] = {}
    if not tests_dir.exists():
        return result
    for sub in _list_dirs(tests_dir):
        count = len(list(sub.rglob("test_*.py")))
        if count > 0:
            result[sub.name] = count
    return dict(sorted(result.items(), key=lambda x: -x[1]))


def _scan_app_structure() -> list[str]:
    """Top-level app structure."""
    app_dir = PROJECT_ROOT / "app"
    if not app_dir.exists():
        return []
    result = []
    for p in sorted(app_dir.iterdir()):
        if p.name.startswith("_"):
            continue
        if p.is_dir():
            result.append(f"app/{p.name}/")
        elif p.suffix == ".py":
            result.append(f"app/{p.name}")
    return result


def _scan_top_level() -> list[str]:
    """Top-level repository layout."""
    result = []
    for name in ["app", "docs", "help", "tests", "scripts", "tools", "assets", "archive", "examples", "static"]:
        p = PROJECT_ROOT / name
        if p.exists():
            result.append(f"{name}/")
    return result


def generate() -> str:
    """Generate SYSTEM_MAP.md content."""
    lines = [
        "# System Map – Linux Desktop Chat",
        "",
        f"*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "Run `python3 tools/generate_system_map.py` to regenerate.",
        "",
        "---",
        "",
        "## Top-Level Layout",
        "",
        "```",
    ]
    for item in _scan_top_level():
        lines.append(f"  {item}")
    lines.extend(["```", "", "## Application Structure", "", "```"])
    for item in _scan_app_structure():
        lines.append(f"  {item}")
    lines.extend(["```", ""])

    # Workspaces
    workspaces = _scan_workspaces()
    lines.append("## Workspaces")
    lines.append("")
    for domain, items in workspaces.items():
        lines.append(f"### {domain.replace('_', ' ').title()}")
        lines.append("")
        for item in items[:15]:  # Limit per domain
            lines.append(f"- {item}")
        if len(items) > 15:
            lines.append(f"- ... ({len(items) - 15} more)")
        lines.append("")

    # Services
    lines.append("## Services")
    lines.append("")
    for s in _scan_services():
        lines.append(f"- `{s}`")
    lines.append("")

    # Integrations
    lines.append("## Integrations")
    lines.append("")
    for i in _scan_integrations():
        lines.append(f"- {i}")
    lines.append("")

    # Help content directories
    help_dir = PROJECT_ROOT / "help"
    if help_dir.exists():
        lines.append("## Help Content (help/)")
        lines.append("")
        for sub in sorted(help_dir.iterdir()):
            if sub.is_dir():
                count = len(list(sub.glob("*.md")))
                lines.append(f"- `help/{sub.name}/` — {count} articles")
        lines.append("")

    # Help topics (flat list)
    help_topics = _scan_help_topics()
    lines.append("## Help Topics")
    lines.append("")
    if help_topics:
        for h in help_topics:
            lines.append(f"- `help/{h}`")
    else:
        lines.append("- *(No help articles yet – run Phase 4–5)*")
    lines.append("")

    # Tests
    lines.append("## Test Suites")
    lines.append("")
    for name, count in _scan_tests().items():
        lines.append(f"- `tests/{name}/` — {count} test modules")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    content = generate()
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
