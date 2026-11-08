"""Uninstall: remove the installed docile binary."""

from __future__ import annotations

import sys
from pathlib import Path

CLAUDE_NOTE = (
    "If you added docile to Claude Desktop, remove its entry in Settings -> "
    "Desktop App -> Extensions -> Local MCP Servers -> Edit Config."
)


def run_uninstall(yes: bool = False) -> int:
    if not getattr(sys, "frozen", False):
        print(
            "Error: this docile was not installed from a release binary, so it "
            "cannot remove itself. If you installed it with pip, run:\n"
            "  pip uninstall docile",
            file=sys.stderr,
        )
        return 1
    target = Path(sys.executable).resolve()
    if not yes:
        if not sys.stdin.isatty():
            print("Error: use -y to uninstall without a prompt.", file=sys.stderr)
            return 1
        answer = input(f"Remove {target}? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Cancelled, docile was not removed.", file=sys.stderr)
            return 1
    try:
        target.unlink()
    except PermissionError:
        print(f"Error: no permission to remove {target}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        pass
    print(f"Removed {target}")
    print(CLAUDE_NOTE)
    return 0
