#!/usr/bin/env python3
"""CLI: Smoke-Lauf für alle registrierten GUIs (Exit 0/1)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))

    parser = argparse.ArgumentParser(description="GUI smoke harness (registered GUIs)")
    parser.add_argument(
        "--no-subprocess",
        action="store_true",
        help="Nur Registry/Manifest-Checks, kein Kurzstart",
    )
    parser.add_argument(
        "--gui",
        metavar="GUI_ID",
        help="Nur diese gui_id (sonst alle registrierten)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Timeout pro GUI-Subprozess (Sekunden)",
    )
    args = parser.parse_args()

    from app.core.startup_contract import list_registered_gui_ids
    from app.gui_smoke_harness import run_all_registered_gui_smokes, run_gui_smoke

    if args.gui:
        r = run_gui_smoke(
            args.gui,
            repo_root=repo,
            run_subprocess=not args.no_subprocess,
            subprocess_timeout_s=args.timeout,
        )
        results = (r,)
    else:
        if args.no_subprocess:
            results = tuple(
                run_gui_smoke(
                    gid,
                    repo_root=repo,
                    run_subprocess=False,
                )
                for gid in sorted(list_registered_gui_ids())
            )
        else:
            results = run_all_registered_gui_smokes(
                repo_root=repo,
                run_subprocess=True,
                subprocess_timeout_s=args.timeout,
            )

    any_fail = False
    for res in results:
        print(f"=== {res.gui_id} === {'OK' if res.ok else 'FAIL'}")
        for st in res.steps:
            status = "ok" if st.ok else "FAIL"
            print(f"  [{status}] {st.name}: {st.detail}")
        if not res.ok:
            any_fail = True

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
