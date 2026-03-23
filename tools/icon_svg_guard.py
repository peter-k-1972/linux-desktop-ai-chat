#!/usr/bin/env python3
"""
Validiert UI-SVGs gegen ICON_STYLE_GUIDE.md (Outline, currentColor, 24×24).

Aufruf:
  python3 tools/icon_svg_guard.py [pfad_zu_icons_root]

Standardpfad: resources/icons/
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = {"svg": "http://www.w3.org/2000/svg"}
HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RGB_RE = re.compile(r"\brgb\s*\(")
URL_RE = re.compile(r"\burl\s*\(", re.I)


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def validate_svg_file(path: Path) -> list[str]:
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return [f"{path}: leer"]

    if URL_RE.search(raw):
        errors.append(f"{path}: url() / Gradient-Verdacht")

    raw_lower = raw.lower()
    for bad in (
        "<lineargradient",
        "<radialgradient",
        "<pattern ",
        "<pattern>",
        "<mask ",
        "<mask>",
        "<image ",
        "<image>",
        "<feblend",
        "<fecolormatrix",
        "<fecomponenttransfer",
        "<fecomposite",
        "<feconvolvematrix",
        "<fediffuselighting",
        "<fedisplacementmap",
        "<fedistantlight",
        "<fedropshadow",
        "<feflood",
        "<fefunca",
        "<fegaussianblur",
        "<feimage",
        "<femerge",
        "<femorphology",
        "<feoffset",
        "<fepointlight",
        "<fespecularlighting",
        "<fespotlight",
        "<fetile",
        "<feturbulence",
    ):
        if bad in raw_lower:
            errors.append(f"{path}: verbotenes Element/Filter ({bad.strip('<')})")

    if "href=\"data:" in raw or "href='data:" in raw or "xlink:href=\"data:" in raw:
        errors.append(f"{path}: eingebettete data:-Ressource")

    if RGB_RE.search(raw):
        errors.append(f"{path}: rgb() — nur currentColor erlaubt")

    for m in HEX_COLOR_RE.finditer(raw):
        errors.append(f"{path}: harte Farbe {m.group(0)}")

    if "opacity" in raw.lower() and "opacity=\"1\"" not in raw.replace(" ", ""):
        # opacity=0.4 etc.
        if re.search(r'opacity\s*=\s*"(?!1(\.0*)?")[^"]+', raw):
            errors.append(f"{path}: opacity ≠ 1 nicht erlaubt")

    if "filter:" in raw or "<filter" in raw:
        errors.append(f"{path}: filter / Schatten nicht erlaubt")

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"{path}: XML-Parsefehler: {e}"]

    root = tree.getroot()
    if _local_name(root.tag).lower() != "svg":
        errors.append(f"{path}: Root ist kein svg")
        return errors

    vb = (root.get("viewBox") or "").strip()
    if vb != "0 0 24 24":
        errors.append(f"{path}: viewBox ist «{vb}», erwartet 0 0 24 24")

    sw = (root.get("stroke-width") or "").strip()
    if sw and sw != "1.5":
        errors.append(f"{path}: Root stroke-width «{sw}», erwartet 1.5")

    fill_root = (root.get("fill") or "").strip().lower()
    if fill_root and fill_root != "none":
        errors.append(f"{path}: Root fill muss none sein, ist «{fill_root}»")

    stroke_root = (root.get("stroke") or "").strip().lower()
    if stroke_root != "currentcolor":
        errors.append(f"{path}: Root stroke muss currentColor sein, ist «{stroke_root}»")

    for el in root.iter():
        fill = (el.get("fill") or "").strip().lower()
        if not fill or fill in ("none", "transparent"):
            continue
        if fill == "currentcolor":
            continue
        errors.append(f"{path}: verbotenes fill=«{el.get('fill')}» auf <{_local_name(el.tag)}>")

        stroke = (el.get("stroke") or "").strip().lower()
        if stroke and stroke not in ("none", "currentcolor"):
            errors.append(f"{path}: stroke=«{el.get('stroke')}» auf <{_local_name(el.tag)}>")

        sw_el = (el.get("stroke-width") or "").strip()
        if sw_el and sw_el != "1.5":
            errors.append(
                f"{path}: stroke-width «{sw_el}» auf <{_local_name(el.tag)}> — nur Root 1.5 oder weglassen (erben)"
            )

    return errors


def validate_tree(root: Path) -> list[str]:
    all_err: list[str] = []
    for p in sorted(root.rglob("*.svg")):
        all_err.extend(validate_svg_file(p))
    return all_err


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SVG QA für resources/icons")
    ap.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Wurzelverzeichnis (default: resources/icons unter Projektroot)",
    )
    args = ap.parse_args(argv)
    root = Path(args.path) if args.path else Path(__file__).resolve().parent.parent / "resources" / "icons"
    if not root.is_dir():
        print(f"Kein Verzeichnis: {root}", file=sys.stderr)
        return 2
    err = validate_tree(root)
    if err:
        for e in err:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {root} ({len(list(root.rglob('*.svg')))} SVGs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
