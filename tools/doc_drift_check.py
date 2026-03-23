#!/usr/bin/env python3
"""
Deterministic documentation drift checker: compares docs against the repository tree and key code facts.

Does not modify application logic. Read-only analysis.

Usage:
  python3 tools/doc_drift_check.py [--json PATH] [--report PATH]

Default report: docs/DOC_DRIFT_REPORT.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = PROJECT_ROOT / "docs" / "DOC_DRIFT_REPORT.md"

CODE_SCAN_ROOTS = (
    PROJECT_ROOT / "app",
    PROJECT_ROOT / "tools",
    PROJECT_ROOT / "tests",
)
MAIN_PY = PROJECT_ROOT / "main.py"

# Markdown sources (per spec)
DOC_GLOBS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "help",
    PROJECT_ROOT / "docs_manual",
)

GENERATED_DOCS = {
    "SYSTEM_MAP": PROJECT_ROOT / "docs" / "SYSTEM_MAP.md",
    "TRACE_MAP": PROJECT_ROOT / "docs" / "TRACE_MAP.md",
    "FEATURE_REGISTRY": PROJECT_ROOT / "docs" / "FEATURE_REGISTRY.md",
}

MANUAL_RESOLVER = PROJECT_ROOT / "app" / "help" / "manual_resolver.py"
SETTINGS_WORKSPACE = PROJECT_ROOT / "app" / "gui" / "domains" / "settings" / "settings_workspace.py"
SETTINGS_NAV = PROJECT_ROOT / "app" / "gui" / "domains" / "settings" / "navigation.py"
SETTINGS_ARCH_DOC = PROJECT_ROOT / "docs" / "04_architecture" / "SETTINGS_ARCHITECTURE.md"

# Conservative: paths under these doc prefixes are often historical; flag lower severity + note.
HISTORICAL_DOC_PREFIXES = (
    "docs/refactoring/",
    "docs/06_operations_and_qa/UX_",  # many legacy app/ui path mentions in implementation logs
)

# Packages at app/<name>/ considered for manual coverage (exclude tooling / generated / tiny shims).
MANUAL_COVERAGE_SKIP = frozenset(
    {
        "__pycache__",
        "gui_designer_dummy",
    }
)

# Map app top-level package -> docs_manual/modules/<m>/README.md when name differs.
MANUAL_MODULE_ALIASES: dict[str, str] = {
    "chats": "chat",
}

# Minimum .py files (recursive) under app/<pkg>/ to require a manual module README.
MANUAL_COVERAGE_MIN_PY = 12

# Populated at runtime: valid first segment under app/ (directories + known .py roots).
_APP_TOP_NAMES: set[str] | None = None


@dataclass
class Finding:
    category: str
    severity: str  # blocker | high | medium | low
    summary: str
    detail: str = ""
    source: str = ""
    notes: str = ""  # false-positive / caveat


@dataclass
class DriftResult:
    findings: list[Finding] = field(default_factory=list)

    def add(
        self,
        category: str,
        severity: str,
        summary: str,
        detail: str = "",
        source: str = "",
        notes: str = "",
    ) -> None:
        self.findings.append(
            Finding(
                category=category,
                severity=severity,
                summary=summary,
                detail=detail,
                source=source,
                notes=notes,
            )
        )

    def counts(self) -> dict[str, int]:
        out = defaultdict(int)
        for f in self.findings:
            out[f.severity] += 1
        out["total"] = len(self.findings)
        return dict(out)


def _iter_markdown_files() -> Iterable[Path]:
    skip_report = PROJECT_ROOT / "docs" / "DOC_DRIFT_REPORT.md"
    yield PROJECT_ROOT / "README.md"
    for base in (PROJECT_ROOT / "docs", PROJECT_ROOT / "help", PROJECT_ROOT / "docs_manual"):
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if "__pycache__" in p.parts:
                continue
            if p.resolve() == skip_report.resolve():
                continue
            yield p


def _is_historical_source(rel_posix: str) -> bool:
    return any(rel_posix.startswith(p) for p in HISTORICAL_DOC_PREFIXES)


def _guess_replacement(missing: str) -> str:
    if missing.startswith("app/ui/"):
        tail = missing[len("app/ui/") :]
        cand = f"app/gui/{tail}"
        if (PROJECT_ROOT / cand).exists():
            return cand
    m = re.match(r"app/gui/icons/svg/?$", missing.rstrip("/"))
    if m and (PROJECT_ROOT / "assets/icons/svg").is_dir():
        return "assets/icons/svg/"
    # Same basename elsewhere under app/
    if missing.startswith("app/") and missing.endswith(".py"):
        name = Path(missing).name
        matches = list((PROJECT_ROOT / "app").rglob(name))
        if len(matches) == 1:
            return str(matches[0].relative_to(PROJECT_ROOT)).replace("\\", "/")
    return ""


# Paths that look like repo-relative code/doc references.
_PATH_RE = re.compile(
    r"(?P<p>(?:app|tests|tools)/[a-zA-Z0-9_./\-]+(?:\.(?:py|md|yaml|yml|json|toml|txt))?)"
)
# Also: root main.py
_MAIN_RE = re.compile(r"(?<![\w/])main\.py(?![\w/])")


def _clean_candidate(raw: str) -> str | None:
    s = raw.strip().rstrip(".,;:\"'”’)]}>")
    if not s or "..." in s or "{" in s:
        return None
    if s.endswith("/**"):
        s = s[:-3]
    elif s.endswith("/*"):
        s = s[:-2]
    if "*" in s:
        return None
    if s.endswith("/") and not s.endswith("app/") and len(s) < 6:
        return None
    if "::" in s:
        s = s.split("::", 1)[0].strip()
    s = s.rstrip("(")
    return s


def _extract_paths_from_text(text: str) -> list[str]:
    found: list[str] = []
    for m in _PATH_RE.finditer(text):
        c = _clean_candidate(m.group("p"))
        if c:
            found.append(c)
    for m in _MAIN_RE.finditer(text):
        found.append("main.py")
    return found


def _extract_backtick_paths(text: str) -> list[str]:
    """Paths inside `...` (narrower than full text scan)."""
    out: list[str] = []
    for m in re.finditer(r"`([^`\n]+)`", text):
        inner = m.group(1).strip()
        if re.match(r"^(?:app|tests|tools)/", inner) or inner == "main.py":
            c = _clean_candidate(inner)
            if c:
                out.append(c)
    return out


def _extract_markdown_link_paths(text: str) -> list[str]:
    out: list[str] = []
    for m in re.finditer(r"\]\(((?:app|tests|tools)/[^)#\s]+)\)", text):
        c = _clean_candidate(m.group(1))
        if c:
            out.append(c)
    return out


def _path_exists(rel: str) -> bool:
    p = PROJECT_ROOT / rel
    if rel.endswith("/"):
        return p.is_dir()
    if p.is_file():
        return True
    if p.is_dir():
        return True
    # Doc shorthand: `app/pkg/module` meaning `module.py` or package
    if "/" in rel and not rel.endswith(
        (".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt")
    ):
        if (PROJECT_ROOT / f"{rel}.py").is_file():
            return True
        if (p / "__init__.py").is_file():
            return True
    return False


def _app_top_level_names() -> set[str]:
    global _APP_TOP_NAMES
    if _APP_TOP_NAMES is not None:
        return _APP_TOP_NAMES
    app_dir = PROJECT_ROOT / "app"
    names: set[str] = set()
    if app_dir.is_dir():
        for p in app_dir.iterdir():
            if p.name.startswith("_"):
                continue
            names.add(p.name)
            if p.is_file() and p.suffix == ".py":
                names.add(p.name[: -len(".py")])
    _APP_TOP_NAMES = names
    return names


def _looks_like_filesystem_path(cand: str) -> bool:
    """Exclude dotted module references (app/pkg/mod.symbol) and doc templates."""
    if "*" in cand or "<" in cand or ">" in cand:
        return False
    if "," in cand:
        return False
    if cand.endswith("/"):
        return True
    base = cand.rsplit("/", 1)[-1]
    if "." in base:
        return base.endswith((".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt"))
    return True


def _is_plausible_repo_path(cand: str) -> bool:
    """Drop prose false positives like `app/sachlich` (German adjective)."""
    if cand == "main.py":
        return True
    if cand.startswith("tests/") or cand.startswith("tools/"):
        return True
    if not cand.startswith("app/"):
        return False
    rest = cand[4:].rstrip("/")
    if not rest:
        return False
    if "/" in rest:
        return True
    if "." in rest:
        ext = rest.rsplit(".", 1)[-1].lower()
        if ext in ("py", "md", "yaml", "yml", "json", "toml", "txt"):
            return True
    seg = rest.split("/")[0]
    return seg in _app_top_level_names()


def _severity_for_source(rel_posix: str, in_backticks: bool) -> tuple[str, str]:
    if rel_posix == "README.md" or rel_posix.startswith("help/") or rel_posix.startswith("docs_manual/"):
        return "high", ""
    if _is_historical_source(rel_posix):
        return "low", "Possible historical / migration context; verify before changing."
    if not in_backticks:
        return "medium", "Heuristic path match (not only backticks); may be false positive."
    return "medium", ""


def _scan_app_structure() -> list[str]:
    """Match tools/generate_system_map.py _scan_app_structure."""
    app_dir = PROJECT_ROOT / "app"
    if not app_dir.exists():
        return []
    result: list[str] = []
    for p in sorted(app_dir.iterdir()):
        if p.name.startswith("_"):
            continue
        if p.is_dir():
            result.append(f"app/{p.name}/")
        elif p.suffix == ".py":
            result.append(f"app/{p.name}")
    return result


def _parse_system_map_app_block(content: str) -> list[str]:
    """Lines like '  app/foo/' inside Application Structure fence."""
    lines = content.splitlines()
    try:
        idx = lines.index("## Application Structure")
    except ValueError:
        return []
    # Next ``` opens fence
    fence = None
    for i in range(idx, min(idx + 15, len(lines))):
        if lines[i].strip() == "```":
            fence = i
            break
    if fence is None:
        return []
    out: list[str] = []
    for j in range(fence + 1, len(lines)):
        if lines[j].strip() == "```":
            break
        line = lines[j].rstrip()
        m = re.match(r"^\s{2}(app/.+)$", line)
        if m:
            out.append(m.group(1).strip())
    return out


def _extract_generated_paths(md_text: str) -> list[str]:
    """Backtick paths to app/tests/tools files from TRACE_MAP / FEATURE_REGISTRY."""
    out: list[str] = []
    for m in re.finditer(r"`((?:app|tests|tools)/[^`]+\.(?:py|md))`", md_text):
        out.append(m.group(1).strip())
    return out


def _extract_feature_registry_help_ids(text: str) -> list[str]:
    """Help column entries: | Help | `topic_id` |"""
    ids: list[str] = []
    for m in re.finditer(r"\|\s*Help\s*\|\s*`([^`]+)`\s*\|", text):
        val = m.group(1).strip()
        if val and val not in ("—", "-", "n/a", "N/A"):
            ids.append(val)
    return ids


def _help_topic_ids_on_disk() -> dict[str, Path]:
    """topic_id -> first path (help/)."""
    help_dir = PROJECT_ROOT / "help"
    out: dict[str, Path] = {}
    if not help_dir.is_dir():
        return out
    for md in help_dir.rglob("*.md"):
        try:
            raw = md.read_text(encoding="utf-8")
        except OSError:
            continue
        topic_id = None
        if raw.strip().startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml  # type: ignore

                    meta = yaml.safe_load(parts[1]) or {}
                    topic_id = meta.get("id")
                except Exception:
                    topic_id = None
        if not topic_id:
            for line in raw.splitlines()[:40]:
                if line.startswith("id:"):
                    topic_id = line.split(":", 1)[1].strip().strip("\"'")
                    break
        if not topic_id:
            topic_id = md.stem
        out.setdefault(str(topic_id), md)
    return out


def _parse_settings_category_ids_from_navigation(text: str) -> set[str]:
    ids: set[str] = set()
    for m in re.finditer(r'\("(?P<id>settings_[a-z_]+)"', text):
        ids.add(m.group("id"))
    return ids


def _parse_settings_factory_keys(text: str) -> set[str]:
    """Keys in _category_factories dict."""
    m = re.search(r"_category_factories\b.*?\=\s*\{", text, re.DOTALL)
    if not m:
        return set()
    start = text.find("{", m.start())
    if start < 0:
        return set()
    depth = 0
    i = start
    body = ""
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                body = text[start + 1 : i]
                break
        i += 1
    keys: set[str] = set()
    for km in re.finditer(r'"?(settings_[a-z_]+)"?\s*:', body):
        keys.add(km.group(1))
    return keys


def _parse_settings_arch_table_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for line in text.splitlines():
        if "`settings_" in line and "|" in line:
            for m in re.finditer(r"`(settings_[a-z_]+)`", line):
                ids.add(m.group(1))
    return ids


def _parse_manual_resolver_targets(text: str) -> tuple[set[str], set[str], set[str]]:
    """Returns (module_names, workflow_names, root_doc_names)."""
    modules: set[str] = set()
    workflows: set[str] = set()
    roots: set[str] = set()
    # "foo": ("module", "bar"),
    for m in re.finditer(
        r'"([^"]+)"\s*:\s*\(\s*"(module|workflow|root)"\s*,\s*"([^"]+)"\s*\)',
        text,
    ):
        kind, name = m.group(2), m.group(3)
        if kind == "module":
            modules.add(name)
        elif kind == "workflow":
            workflows.add(name)
        else:
            roots.add(name)
    return modules, workflows, roots


def _count_py_files(pkg: Path) -> int:
    if not pkg.is_dir():
        return 0
    n = 0
    for p in pkg.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        n += 1
    return n


def run_checks() -> DriftResult:
    r = DriftResult()
    rel = lambda p: str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")

    # --- 1) Path drift from markdown ---
    path_hits: dict[str, list[str]] = defaultdict(list)
    for md_path in _iter_markdown_files():
        rp = rel(md_path) if md_path != PROJECT_ROOT / "README.md" else "README.md"
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            r.add("missing_paths", "medium", f"Unreadable doc file: {rp}", source=rp)
            continue
        bt = set(_extract_backtick_paths(text))
        links = set(_extract_markdown_link_paths(text))
        under_docs = rp.startswith("docs/")

        cands: list[str] = []
        if under_docs:
            # Under docs/: only explicit path syntax (backticks + md links) — avoids prose false positives.
            cands.extend(bt)
            cands.extend(links)
        else:
            cands.extend(_extract_paths_from_text(text))
            cands.extend(bt)
            cands.extend(links)

        seen_file: set[str] = set()
        for cand in cands:
            if cand in seen_file:
                continue
            seen_file.add(cand)
            if not _is_plausible_repo_path(cand) or not _looks_like_filesystem_path(cand):
                continue
            if cand == "main.py":
                ok = MAIN_PY.is_file()
                if not ok:
                    r.add(
                        "missing_paths",
                        "high",
                        "main.py",
                        detail="Repository root main.py missing",
                        source=rp,
                    )
                continue
            if not (cand.startswith("app/") or cand.startswith("tests/") or cand.startswith("tools/")):
                continue
            path_hits[cand].append(rp)

    ui_missing: list[str] = []
    for cand, sources in sorted(path_hits.items()):
        if cand == "main.py":
            continue
        if _path_exists(cand):
            continue
        if not cand.endswith("/") and (PROJECT_ROOT / cand).is_dir():
            continue
        if cand.startswith("app/ui/"):
            ui_missing.append(cand)
            continue
        guess = _guess_replacement(cand)
        sample_src = sources[0]
        # docs/** uses backticks+md links only; other trees use broader extraction.
        in_backtick = (
            sample_src.startswith("docs/")
            or sample_src.startswith("docs_manual/")
            or sample_src.startswith("help/")
            or sample_src == "README.md"
        )
        sev, note = _severity_for_source(sample_src, in_backtick)
        srcs = sorted(set(sources))
        ref = ", ".join(srcs[:8]) + (" …" if len(srcs) > 8 else "")
        sug = f"`{guess}`" if guess else "—"
        extra = "" if in_backtick else " Medium/low doc tree; confirm backtick vs prose match."
        r.add(
            "missing_paths",
            sev,
            cand,
            detail=f"Referenced in: {ref}. Suggested path: {sug}",
            source=sample_src,
            notes=(note + extra).strip(),
        )

    if ui_missing:
        srcs: set[str] = set()
        for c in ui_missing:
            srcs.update(path_hits.get(c, ()))
        ref = ", ".join(sorted(srcs)[:10]) + (" …" if len(srcs) > 10 else "")
        r.add(
            "missing_paths",
            "low",
            f"app/ui/* ({len(ui_missing)} distinct paths, aggregated)",
            detail=f"Referenced in: {ref}. Real tree: `app/gui/`.",
            source=sorted(srcs)[0] if srcs else "docs/",
            notes="Migration / audit docs often retain app/ui/ paths. False positive if text is explicitly historical.",
        )
        r.add(
            "structure",
            "medium",
            "Documentation cites removed `app/ui/` filesystem tree",
            detail=f"Aggregated {len(ui_missing)} missing paths; current GUI code lives under `app/gui/`.",
            source="docs/**, docs_manual/**, help/**",
            notes="Prefer curating current-structure docs vs. retaining obsolete path lists in active manuals.",
        )

    # --- 2) Generated SYSTEM_MAP vs tree ---
    sm_path = GENERATED_DOCS["SYSTEM_MAP"]
    if sm_path.is_file():
        sm_text = sm_path.read_text(encoding="utf-8")
        listed = set(_parse_system_map_app_block(sm_text))
        actual = set(_scan_app_structure())
        missing_in_doc = sorted(actual - listed)
        stale_in_doc = sorted(listed - actual)
        for item in missing_in_doc:
            r.add(
                "generated_map",
                "medium",
                f"SYSTEM_MAP missing entry: {item}",
                "Regenerate with python3 tools/generate_system_map.py",
                source="docs/SYSTEM_MAP.md",
            )
        for item in stale_in_doc:
            r.add(
                "generated_map",
                "high",
                f"SYSTEM_MAP lists non-existent: {item}",
                "Remove or regenerate SYSTEM_MAP.md",
                source="docs/SYSTEM_MAP.md",
                notes="False positive if intentional placeholder.",
            )
    else:
        r.add("generated_map", "blocker", "docs/SYSTEM_MAP.md missing", source="docs/SYSTEM_MAP.md")

    # --- 3) TRACE_MAP / FEATURE_REGISTRY paths ---
    for label, pth in ("TRACE_MAP", GENERATED_DOCS["TRACE_MAP"]), (
        "FEATURE_REGISTRY",
        GENERATED_DOCS["FEATURE_REGISTRY"],
    ):
        if not pth.is_file():
            r.add("generated_map", "blocker", f"{label}: file missing", source=str(pth.relative_to(PROJECT_ROOT)))
            continue
        body = pth.read_text(encoding="utf-8")
        for path in sorted(set(_extract_generated_paths(body))):
            if _path_exists(path):
                continue
            guess = _guess_replacement(path)
            r.add(
                "generated_map",
                "blocker",
                f"{label} references missing path: {path}",
                f"Suggested: `{guess}`" if guess else "",
                source=str(pth.relative_to(PROJECT_ROOT)),
            )

    # --- 4) Help IDs in FEATURE_REGISTRY ---
    fr = GENERATED_DOCS["FEATURE_REGISTRY"]
    if fr.is_file():
        fr_text = fr.read_text(encoding="utf-8")
        topic_index = _help_topic_ids_on_disk()
        for hid in _extract_feature_registry_help_ids(fr_text):
            if hid not in topic_index:
                r.add(
                    "help_manual",
                    "high",
                    f"FEATURE_REGISTRY Help topic not found under help/: {hid}",
                    "Add help article with frontmatter id or regenerate registry.",
                    source="docs/FEATURE_REGISTRY.md",
                )

    # --- 5) manual_resolver targets ---
    if MANUAL_RESOLVER.is_file():
        mr_text = MANUAL_RESOLVER.read_text(encoding="utf-8")
        mods, wfs, roots = _parse_manual_resolver_targets(mr_text)
        dm = PROJECT_ROOT / "docs_manual"
        for m in sorted(mods):
            p = dm / "modules" / m / "README.md"
            if not p.is_file():
                r.add(
                    "help_manual",
                    "blocker",
                    f"manual_resolver module target missing: docs_manual/modules/{m}/README.md",
                    source="app/help/manual_resolver.py",
                )
        for w in sorted(wfs):
            p = dm / "workflows" / f"{w}.md"
            if not p.is_file():
                r.add(
                    "help_manual",
                    "blocker",
                    f"manual_resolver workflow target missing: docs_manual/workflows/{w}.md",
                    source="app/help/manual_resolver.py",
                )
        for root_doc in sorted(roots):
            p = dm / root_doc
            if not p.is_file():
                r.add(
                    "help_manual",
                    "blocker",
                    f"manual_resolver root doc missing: docs_manual/{root_doc}",
                    source="app/help/manual_resolver.py",
                )

    # --- 6) Settings structure: navigation vs factories vs arch doc ---
    if SETTINGS_NAV.is_file() and SETTINGS_WORKSPACE.is_file():
        nav_ids = _parse_settings_category_ids_from_navigation(SETTINGS_NAV.read_text(encoding="utf-8"))
        fac_ids = _parse_settings_factory_keys(SETTINGS_WORKSPACE.read_text(encoding="utf-8"))
        only_nav = sorted(nav_ids - fac_ids)
        only_fac = sorted(fac_ids - nav_ids)
        if only_nav or only_fac:
            r.add(
                "structure",
                "blocker",
                "Settings category IDs differ between navigation.py and settings_workspace.py",
                f"Only in navigation: {only_nav}; only in factories: {only_fac}",
                source="app/gui/domains/settings/",
            )
    if SETTINGS_ARCH_DOC.is_file():
        doc_ids = _parse_settings_arch_table_ids(SETTINGS_ARCH_DOC.read_text(encoding="utf-8"))
        if SETTINGS_NAV.is_file():
            nav_ids = _parse_settings_category_ids_from_navigation(SETTINGS_NAV.read_text(encoding="utf-8"))
            if doc_ids and nav_ids != doc_ids:
                r.add(
                    "structure",
                    "high",
                    "SETTINGS_ARCHITECTURE.md table IDs != navigation.py DEFAULT_CATEGORIES",
                    f"doc: {sorted(doc_ids)} vs nav: {sorted(nav_ids)}",
                    source="docs/04_architecture/SETTINGS_ARCHITECTURE.md",
                    notes="Verify table completeness if navigation was extended.",
                )

    # --- 7) Explicit numeric claims vs settings category count (conservative) ---
    settings_count = len(
        _parse_settings_factory_keys(SETTINGS_WORKSPACE.read_text(encoding="utf-8"))
        if SETTINGS_WORKSPACE.is_file()
        else set()
    )
    if settings_count:
        num_re = re.compile(
            r"\b(\d+)\s*(?:Settings-)?(?:Workspaces|Kategorien|settings\s+categories)\b",
            re.IGNORECASE,
        )
        for md_path in _iter_markdown_files():
            rp = rel(md_path) if md_path != PROJECT_ROOT / "README.md" else "README.md"
            if "SETTINGS_ARCHITECTURE" in rp or "DOC_GAP" in rp:
                continue
            try:
                t = md_path.read_text(encoding="utf-8")
            except OSError:
                continue
            for m in num_re.finditer(t):
                n = int(m.group(1))
                if 1 < n < 20 and n != settings_count and "settings" in t.lower()[:2000]:
                    # Avoid matching unrelated "3 categories" in QA docs: require nearby settings keyword line
                    span = t[max(0, m.start() - 120) : m.end() + 120].lower()
                    if "setting" not in span:
                        continue
                    r.add(
                        "structure",
                        "low",
                        f"Numeric settings claim may be stale: {n} (code has {settings_count} categories)",
                        f"Match: {m.group(0)!r}",
                        source=rp,
                        notes="Heuristic; confirm context (may refer to workspaces, not categories).",
                    )
                    break

    # --- 8) Manual module / role / workflow skeleton ---
    dm_root = PROJECT_ROOT / "docs_manual"
    if dm_root.is_dir():
        modules_dir = dm_root / "modules"
        if modules_dir.is_dir():
            for sub in sorted(modules_dir.iterdir()):
                if not sub.is_dir() or sub.name.startswith("_"):
                    continue
                readme = sub / "README.md"
                if not readme.is_file():
                    r.add(
                        "manual_coverage",
                        "medium",
                        f"docs_manual/modules/{sub.name}/ missing README.md",
                        source="docs_manual/modules/",
                    )
        roles_dir = dm_root / "roles"
        if roles_dir.is_dir():
            for sub in sorted(roles_dir.iterdir()):
                if not sub.is_dir() or sub.name.startswith("_"):
                    continue
                readme = sub / "README.md"
                if not readme.is_file():
                    r.add(
                        "manual_coverage",
                        "medium",
                        f"docs_manual/roles/{sub.name}/ missing README.md",
                        source="docs_manual/roles/",
                    )
        wf_dir = dm_root / "workflows"
        if wf_dir.is_dir():
            for md in sorted(wf_dir.glob("*.md")):
                if md.name.startswith("_"):
                    continue
                # templates are ok as non-normative
                if "template" in md.name.lower():
                    continue

    # --- 9) App packages without manual module (heuristic) ---
    app_dir = PROJECT_ROOT / "app"
    if app_dir.is_dir():
        for child in sorted(app_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            if child.name in MANUAL_COVERAGE_SKIP:
                continue
            n_py = _count_py_files(child)
            if n_py < MANUAL_COVERAGE_MIN_PY:
                continue
            mod_name = MANUAL_MODULE_ALIASES.get(child.name, child.name)
            readme = dm_root / "modules" / mod_name / "README.md"
            if not readme.is_file():
                r.add(
                    "coverage_gap",
                    "medium",
                    f"app/{child.name}/ has {n_py} Python files but no docs_manual/modules/{mod_name}/README.md",
                    source="app/",
                    notes="Heuristic threshold; add manual or lower threshold in tools/doc_drift_check.py if intentional.",
                )

    return r


def _render_report(result: DriftResult) -> str:
    c = result.counts()
    blocker = c.get("blocker", 0)
    high = c.get("high", 0)
    medium = c.get("medium", 0)
    low = c.get("low", 0)
    total = c.get("total", 0)

    lines: list[str] = [
        "# DOC DRIFT REPORT",
        "",
        f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}* — `python3 tools/doc_drift_check.py`",
        "",
        "Vergleich **Ist-Repository** (u. a. `app/`, `tests/`, `tools/`) mit **README.md**, `docs/**`, `help/**`, `docs_manual/**`. "
        "Die Codebasis gilt als maßgeblich. "
        "Unter `docs/**` werden Pfade nur aus **Backticks** und **Markdown-Links** gelesen (weniger Rauschen als Volltext). "
        "„Probable actual path“ ist deterministisch geraten (z. B. eindeutiger Basename unter `app/`, `app/ui/`→`app/gui/`, Icons→`assets/icons/svg/`); "
        "bei Unsicherheit steht „—“. Abschnitt **Details** enthält Fundstellen und False-Positive-Hinweise.",
        "",
        "## 1. Summary",
        "",
        f"- **drift_count:** {total}",
        f"- **blocker_count:** {blocker}",
        f"- **high_count:** {high}",
        f"- **medium_count:** {medium}",
        f"- **low_count:** {low}",
        "",
    ]

    def _probable_from_detail(detail: str) -> str:
        if "Suggested path:" in detail:
            rest = detail.split("Suggested path:", 1)[1].strip()
            m = re.search(r"`([^`]+)`", rest)
            if m:
                return m.group(1)
            return "—" if rest.startswith("—") else rest[:96]
        if "Real tree:" in detail:
            rest = detail.split("Real tree:", 1)[1].strip()
            m = re.search(r"`([^`]+)`", rest)
            if m:
                return m.group(1)
        return "—"

    def section(title: str, items: list[Finding], empty_msg: str) -> None:
        lines.append(title)
        lines.append("")
        if not items:
            lines.append(empty_msg)
            lines.append("")
            return
        for f in items:
            lines.append(f"- **{f.summary}**")
            if f.detail:
                lines.append(f"  - Detail: {f.detail}")
            if f.source:
                lines.append(f"  - Source: `{f.source}`")
            if f.notes:
                lines.append(f"  - Notes: {f.notes}")
        lines.append("")

    mp = [f for f in result.findings if f.category == "missing_paths"]
    lines.append("## 2. Missing Paths")
    lines.append("")
    if not mp:
        lines.append("_None._")
        lines.append("")
    else:
        lines.append(
            "| Documented path | Severity (status) | Probable actual path | First source |"
        )
        lines.append("|-----------------|-------------------|----------------------|--------------|")
        for f in sorted(mp, key=lambda x: (x.severity, x.summary)):
            prob = _probable_from_detail(f.detail)
            src = f"`{f.source}`" if f.source else "—"
            lines.append(
                f"| `{f.summary}` | {f.severity} | {prob} | {src} |"
            )
        lines.append("")
        lines.append("### Details")
        lines.append("")
        for f in sorted(mp, key=lambda x: (x.severity, x.summary)):
            lines.append(f"- **{f.summary}**")
            if f.detail:
                lines.append(f"  - {f.detail}")
            if f.source:
                lines.append(f"  - Source: `{f.source}`")
            if f.notes:
                lines.append(f"  - Notes: {f.notes}")
        lines.append("")

    cov = [f for f in result.findings if f.category == "coverage_gap"]
    man = [f for f in result.findings if f.category == "manual_coverage"]
    hm = [f for f in result.findings if f.category == "help_manual"]
    section(
        "## 3. Missing Documentation Coverage",
        sorted(cov + man + hm, key=lambda x: (x.severity, x.summary)),
        "_None._",
    )

    st = [f for f in result.findings if f.category == "structure"]
    section("## 4. Outdated Structural Claims", sorted(st, key=lambda x: (x.severity, x.summary)), "_None._")

    gen = [f for f in result.findings if f.category == "generated_map"]
    lines.append("## 5. Generated File Drift")
    lines.append("")
    lines.append("| File | Status | Notes |")
    lines.append("|------|--------|-------|")
    by_file: dict[str, list[Finding]] = defaultdict(list)
    for f in gen:
        src = f.source or "—"
        by_file[src].append(f)
    for name, p in GENERATED_DOCS.items():
        rel = str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")
        msgs = by_file.get(rel, [])
        if not p.is_file():
            lines.append(f"| `{rel}` | missing | File not present |")
        elif not msgs:
            lines.append(f"| `{rel}` | ok | — |")
        else:
            worst = sorted(msgs, key=lambda x: {"blocker": 0, "high": 1, "medium": 2, "low": 3}[x.severity])[0]
            stat = "veraltet" if worst.severity in ("blocker", "high") else "review"
            note = "; ".join(m.summary for m in msgs[:4])
            if len(msgs) > 4:
                note += " …"
            lines.append(f"| `{rel}` | {stat} | {note} |")
    lines.append("")

    fix: list[str] = []
    for f in result.findings:
        if f.category == "missing_paths" and f.summary and "Suggested path:" in f.detail:
            fix.append(f"- `{f.source}`: `{f.summary}` — {f.detail}")
        elif f.category == "generated_map" and "SYSTEM_MAP" in f.summary:
            fix.append(f"- Regenerate system map: `python3 tools/generate_system_map.py`")
        elif f.category == "generated_map" and ("TRACE_MAP" in f.summary or "FEATURE_REGISTRY" in f.summary):
            fix.append(f"- Regenerate trace/feature registry if paths moved: see `tools/generate_trace_map.py` / `tools/generate_feature_registry.py`")
        elif f.category == "help_manual":
            fix.append(f"- Fix manual/help wiring: {f.summary} (`{f.source}`)")
    # dedupe preserve order
    seen = set()
    uniq_fix = []
    for x in fix:
        if x not in seen:
            seen.add(x)
            uniq_fix.append(x)

    lines.append("## 6. Recommended Fixes")
    lines.append("")
    if uniq_fix:
        lines.extend(uniq_fix)
    else:
        lines.append("_No automated fix strings; review sections above._")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check documentation drift vs repository.")
    parser.add_argument("--json", type=Path, help="Write machine-readable findings JSON.")
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Markdown report path (default: {DEFAULT_REPORT})",
    )
    args = parser.parse_args()

    result = run_checks()
    report = _render_report(result)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.report}")

    if args.json:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "counts": result.counts(),
            "findings": [
                {
                    "category": f.category,
                    "severity": f.severity,
                    "summary": f.summary,
                    "detail": f.detail,
                    "source": f.source,
                    "notes": f.notes,
                }
                for f in result.findings
            ],
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {args.json}")

    # Exit non-zero if any blocker/high
    bad = [f for f in result.findings if f.severity in ("blocker", "high")]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
