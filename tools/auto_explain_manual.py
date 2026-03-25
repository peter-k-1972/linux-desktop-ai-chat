#!/usr/bin/env python3
"""
Semi-automatic documentation stub generator: AST-only structured Markdown under docs_manual/generated/.

No narrative generation; missing facts are explicitly marked. Human remains approval instance.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "docs_manual" / "generated"

LARGE_FILE_LINES = 400
MANY_EXTERNAL_IMPORTS = 12

# Third-party / project roots for dependency heuristics (not stdlib)
_GUI_MARKERS = frozenset(
    {
        "PySide6",
        "PySide2",
        "QtWidgets",
        "QtCore",
        "QtGui",
    }
)


def _stdlib_modules() -> frozenset[str]:
    try:
        import sys

        return frozenset(getattr(sys, "stdlib_module_names", ()))
    except Exception:
        return frozenset()


_STDLIB = _stdlib_modules()


def _dotted_module_name(rel_py: str) -> str:
    p = rel_py.replace("\\", "/")
    if p.endswith(".py"):
        p = p[: -len(".py")]
    return p.replace("/", ".")


def _infer_layer(rel_posix: str) -> str:
    parts = rel_posix.strip("/").split("/")
    if len(parts) < 2 or parts[0] != "app":
        return "nicht aus Code ableitbar (kein app/-Pfad)"
    second = parts[1]
    mapping = {
        "gui": "GUI (app/gui)",
        "services": "Services (app/services)",
        "core": "Core (app/core)",
        "providers": "Providers (app/providers)",
        "context": "Context (app/context)",
        "chat": "Chat-Domain (app/chat)",
        "agents": "Agents (app/agents)",
        "rag": "RAG (app/rag)",
        "prompts": "Prompts (app/prompts)",
        "cli": "CLI (app/cli)",
        "help": "In-App-Hilfe (app/help)",
        "models": "Modelle (app/models)",
        "pipelines": "Pipelines (app.pipelines / linux-desktop-chat-pipelines)",
        "commands": "Commands (app/commands)",
        "metrics": "Metriken (app/metrics)",
        "debug": "Debug (app/debug)",
        "diagnostics": "Diagnostics (app/diagnostics)",
        "qa": "QA (app/qa)",
    }
    return mapping.get(second, f"App-Paket (app/{second}/)")


def _format_arg(arg: ast.arg) -> str:
    if arg.annotation:
        return f"{arg.arg}: {ast.unparse(arg.annotation)}"
    return arg.arg


def _signature_str(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = fn.args
    parts: list[str] = []
    n_pos = len(args.posonlyargs)
    for i, a in enumerate(args.posonlyargs):
        parts.append(_format_arg(a))
        if i < n_pos - 1:
            parts.append(", ")
        else:
            parts.append(", /, ")
    for i, a in enumerate(args.args):
        parts.append(_format_arg(a))
        if i < len(args.args) - 1 or args.vararg or args.kwonlyargs or args.kwarg:
            parts.append(", ")
    if args.vararg:
        parts.append("*" + args.vararg.arg)
        if args.kwonlyargs or args.kwarg:
            parts.append(", ")
    for i, a in enumerate(args.kwonlyargs):
        parts.append(_format_arg(a))
        if i < len(args.kwonlyargs) - 1 or args.kwarg:
            parts.append(", ")
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    sig_inner = "".join(parts)
    ret = ""
    if fn.returns:
        ret = f" -> {ast.unparse(fn.returns)}"
    return f"{fn.name}({sig_inner}){ret}"


@dataclass
class ModuleScan:
    rel_path: str
    line_count: int
    module_doc: str | None
    parse_ok: bool = True
    classes: list[str] = field(default_factory=list)
    class_first_line: dict[str, str] = field(default_factory=dict)
    top_functions: list[str] = field(default_factory=list)
    top_function_sigs: list[str] = field(default_factory=list)
    method_sigs_sample: list[tuple[str, str]] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    external_imports: list[str] = field(default_factory=list)
    gui_import_hits: list[str] = field(default_factory=list)


def _collect_imports(
    tree: ast.Module,
) -> tuple[list[str], list[str], list[str]]:
    flat: list[str] = []
    external: list[str] = []
    gui_hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                flat.append(alias.name)
                if name in _STDLIB or name == "typing":
                    continue
                external.append(alias.name)
                if name in _GUI_MARKERS or alias.name.startswith("PySide"):
                    gui_hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            mod = node.module
            root = mod.split(".")[0]
            for alias in node.names:
                full = f"{mod}.{alias.name}" if alias.name != "*" else f"{mod}.*"
                flat.append(full)
                if root in _STDLIB or root == "typing":
                    continue
                external.append(full)
                if root in _GUI_MARKERS or mod.startswith("PySide"):
                    gui_hits.append(full)
                if mod.startswith("app.gui") or mod.startswith("app.gui."):
                    gui_hits.append(full)
    # dedupe preserve order
    def dedupe(xs: Iterable[str]) -> list[str]:
        s: set[str] = set()
        o: list[str] = []
        for x in xs:
            if x not in s:
                s.add(x)
                o.append(x)
        return o

    return dedupe(flat), dedupe(external), dedupe(gui_hits)


def scan_py_file(path: Path, root: Path) -> ModuleScan | None:
    rel = path.relative_to(root)
    rel_posix = str(rel).replace("\\", "/")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    lines = text.splitlines()
    line_count = len(lines)
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return ModuleScan(
            rel_path=rel_posix,
            line_count=line_count,
            module_doc=None,
            parse_ok=False,
        )

    mod_doc = ast.get_docstring(tree, clean=True)

    classes: list[str] = []
    class_doc_line: dict[str, str] = {}
    top_funcs: list[str] = []
    top_sigs: list[str] = []
    method_samples: list[tuple[str, str]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            classes.append(node.name)
            cdoc = ast.get_docstring(node, clean=True)
            if cdoc:
                class_doc_line[node.name] = cdoc.split("\n", 1)[0].strip()
            # public methods sample (max 12 per class)
            n = 0
            for item in node.body:
                if n >= 12:
                    break
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("_") and item.name != "__init__":
                        continue
                    method_samples.append((node.name, _signature_str(item)))
                    n += 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith(
            "_"
        ):
            top_funcs.append(node.name)
            top_sigs.append(_signature_str(node))

    imp_flat, imp_ext, gui_hits = _collect_imports(tree)

    return ModuleScan(
        rel_path=rel_posix,
        line_count=line_count,
        module_doc=mod_doc,
        classes=classes,
        class_first_line=class_doc_line,
        top_functions=top_funcs,
        top_function_sigs=top_sigs,
        method_sigs_sample=method_samples,
        imports=imp_flat,
        external_imports=imp_ext,
        gui_import_hits=gui_hits,
    )


def _purpose_bullets(scan: ModuleScan) -> list[str]:
    if not scan.parse_ok:
        return ["nicht aus Code ableitbar (Syntaxfehler beim Parsen)"]
    if not scan.module_doc:
        return ["nicht aus Code ableitbar (kein Modul-Docstring)"]
    paras = [p.strip() for p in scan.module_doc.split("\n\n") if p.strip()]
    if not paras:
        return ["nicht aus Code ableitbar (leerer Modul-Docstring)"]
    first = paras[0]
    lines = [ln.strip() for ln in first.split("\n") if ln.strip()]
    if len(lines) <= 1:
        return [first[:500] + ("…" if len(first) > 500 else "")]
    return lines[:10]


def _io_sections(sigs: Sequence[str]) -> list[str]:
    lines = ["## Eingaben", ""]
    lines.append(
        "Parameternamen und Typannotationen, soweit in den erfassten Signaturen vorhanden (keine Semantik):"
    )
    lines.append("")
    if not sigs:
        lines.append(
            "- nicht aus Code ableitbar (keine öffentlichen Funktionen/Methoden im erfassten Ausschnitt)"
        )
    else:
        for s in sigs[:40]:
            lines.append(f"- `{s}`")
        if len(sigs) > 40:
            lines.append(f"- … ({len(sigs) - 40} weitere Signaturen nicht aufgelistet)")
    lines.append("")
    lines.append("## Ausgaben")
    lines.append("")
    lines.append("Rückgabetypen nur wo explizit als `-> …` annotiert; sonst nicht aus dem Stub ableitbar.")
    lines.append("")
    with_ret = [s for s in sigs if "->" in s]
    if not sigs:
        lines.append("- nicht aus Code ableitbar (keine Signaturen erfasst)")
    elif not with_ret:
        lines.append(
            "- nicht aus Code ableitbar (keine Return-Annotationen in den aufgelisteten Signaturen)"
        )
    else:
        for s in with_ret[:40]:
            lines.append(f"- `{s}`")
        if len(with_ret) > 40:
            lines.append(f"- … ({len(with_ret) - 40} weitere)")
    lines.append("")
    return lines


def _dependencies_section(scan: ModuleScan) -> list[str]:
    lines = ["## Abhängigkeiten", ""]
    if not scan.imports:
        lines.append("- nicht aus Code ableitbar (keine Import-Anweisungen erkannt)")
        lines.append("")
        return lines
    lines.append("### Alle Import-Ziele (Auszug)")
    for m in scan.imports[:35]:
        lines.append(f"- `{m}`")
    if len(scan.imports) > 35:
        lines.append(f"- … ({len(scan.imports) - 35} weitere)")
    lines.append("")
    lines.append("### Nicht-Stdlib-Importe (heuristisch)")
    if not scan.external_imports:
        lines.append("- keine (oder nur Stdlib/`typing`)")
    else:
        for m in scan.external_imports[:25]:
            lines.append(f"- `{m}`")
        if len(scan.external_imports) > 25:
            lines.append(f"- … ({len(scan.external_imports) - 25} weitere)")
    lines.append("")
    return lines


def _ui_section(scan: ModuleScan, rel_posix: str) -> list[str]:
    lines = ["## UI-Bezug", ""]
    in_gui_tree = rel_posix.startswith("app/gui/")
    parts = [f"- Paketpfad: `{rel_posix}`"]
    if in_gui_tree:
        parts.append("- **Ja:** Datei liegt unter `app/gui/`.")
    else:
        parts.append("- **Pfad:** nicht unter `app/gui/` (kein direktes GUI-Paket).")
    if scan.gui_import_hits:
        parts.append("- **Import-Hinweise (GUI-nah):**")
        for g in scan.gui_import_hits[:15]:
            parts.append(f"  - `{g}`")
        if len(scan.gui_import_hits) > 15:
            parts.append(f"  - … ({len(scan.gui_import_hits) - 15} weitere)")
    else:
        parts.append("- **Import-Hinweise:** keine PySide-/Qt- oder `app.gui`-Importe im AST erkannt.")
    lines.extend(parts)
    lines.append("")
    return lines


def _risks_section(scan: ModuleScan) -> list[str]:
    lines = ["## Risiken / offene Punkte", ""]
    items: list[str] = []
    if not scan.parse_ok:
        items.append("- **Syntaxfehler:** Datei konnte nicht geparst werden; keine vollständigen AST-Metadaten.")
    if not scan.module_doc:
        items.append("- Kein Modul-Docstring: Zweck muss manuell ergänzt werden.")
    if scan.line_count >= LARGE_FILE_LINES:
        items.append(
            f"- Modul sehr groß ({scan.line_count} Zeilen): Stub fasst nur Metadaten; Detaildoku manuell strukturieren."
        )
    if len(scan.external_imports) >= MANY_EXTERNAL_IMPORTS:
        items.append(
            f"- Viele Nicht-Stdlib-Importe ({len(scan.external_imports)}): Abhängigkeiten und Grenzen manuell prüfen."
        )
    if not scan.classes and not scan.top_functions:
        items.append(
            "- Keine öffentlichen Klassen/Funktionen auf Modulebene erkannt (nur private Namen oder leerer Stub nach Syntaxfehler)."
        )
    if not items:
        items.append("- Keine automatisch erkannten Risiko-Flags (trotzdem inhaltlich prüfen).")
    for it in items:
        lines.append(it)
    lines.append("")
    return lines


def render_markdown(scan: ModuleScan) -> str:
    rel = scan.rel_path
    dotted = _dotted_module_name(rel)
    layer = _infer_layer(rel)

    title = dotted
    out: list[str] = [
        f"# {title}",
        "",
        f"- **Datei:** `{rel}`",
        f"- **Paket/Modul (abgeleitet):** `{dotted}`",
        f"- **Layer (heuristisch):** {layer}",
        "",
        "## Zweck",
        "",
    ]
    for b in _purpose_bullets(scan):
        out.append(f"- {b}")
    out.append("")

    out.append("## Wichtige Klassen")
    out.append("")
    if not scan.classes:
        out.append("- nicht aus Code ableitbar (keine öffentlichen Klassen `^[A-Za-z]` auf Modulebene)")
    else:
        for c in scan.classes:
            extra = scan.class_first_line.get(c, "")
            if extra:
                out.append(f"- `{c}` — {extra}")
            else:
                out.append(f"- `{c}` — nicht aus Code ableitbar (kein Klassen-Docstring)")
    out.append("")

    out.append("## Wichtige Funktionen")
    out.append("")
    if not scan.top_functions:
        out.append("- nicht aus Code ableitbar (keine öffentlichen Top-Level-Funktionen)")
    else:
        for name in scan.top_functions:
            out.append(f"- `{name}`")
    out.append("")

    out.append("## Methoden (Auszug aus Klassen)")
    out.append("")
    if not scan.method_sigs_sample:
        out.append("- nicht aus Code ableitbar oder keine öffentlichen Methoden im erfassten Ausschnitt")
    else:
        for cls, sig in scan.method_sigs_sample:
            out.append(f"- Klasse `{cls}`: `{sig}`")
    out.append("")

    io_list: list[str] = []
    io_list.extend(scan.top_function_sigs)
    for c, s in scan.method_sigs_sample:
        io_list.append(f"{c}.{s}")

    out.extend(_io_sections(io_list))

    out.extend(_dependencies_section(scan))
    out.extend(_ui_section(scan, rel))
    out.extend(_risks_section(scan))

    out.append("---")
    out.append("")
    out.append(
        "*Rohling: automatisch erzeugt durch `tools/auto_explain_manual.py`; nicht als finales Handbuch verwenden.*"
    )
    out.append("")
    return "\n".join(out)


def iter_py_files(paths: Sequence[Path], root: Path) -> Iterable[Path]:
    for p in paths:
        rp = (root / p).resolve() if not p.is_absolute() else p
        if not rp.exists():
            continue
        if rp.is_file() and rp.suffix == ".py":
            yield rp
        elif rp.is_dir():
            for f in sorted(rp.rglob("*.py")):
                if "__pycache__" in f.parts:
                    continue
                yield f


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate structured Markdown stubs from Python AST metadata."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=str,
        help="Relative paths (files or dirs) from project root, e.g. app/services/chat_service.py",
    )
    parser.add_argument(
        "--all-app",
        action="store_true",
        help="Process entire app/ tree (many files).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output root (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated .md files.",
    )
    args = parser.parse_args()

    root = PROJECT_ROOT
    targets: list[Path] = []
    if args.all_app:
        targets.append(root / "app")
    for s in args.paths:
        targets.append(Path(s))

    if not targets:
        parser.error("Geben Sie mindestens einen Pfad an oder verwenden Sie --all-app.")

    out_root: Path = args.output_dir
    if not out_root.is_absolute():
        out_root = root / out_root

    written = 0
    skipped = 0
    errors = 0

    for py_path in iter_py_files(targets, root):
        try:
            rel = py_path.relative_to(root)
        except ValueError:
            continue
        rel_posix = str(rel).replace("\\", "/")
        if not rel_posix.endswith(".py"):
            continue

        scan = scan_py_file(py_path, root)
        if scan is None:
            errors += 1
            continue

        md_rel = rel_posix[: -len(".py")] + ".md"
        out_path = out_root / md_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists() and not args.force:
            skipped += 1
            continue

        body = render_markdown(scan)
        out_path.write_text(body, encoding="utf-8")
        written += 1

    print(f"Written: {written}, skipped (exists): {skipped}, scan errors: {errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
