from __future__ import annotations

import argparse
import json
import shutil
import sys
from importlib import resources
from pathlib import Path

from . import __version__
from .core import DocxerError, create_docx
from .core.naming import DEFAULT_OUTPUT
from .core.render import load
from .update import run_update

EXAMPLE_FILES = ("input.example.json", "template.example.docx", "schema.example.json")

TOKEN_HELP = """\
date/time tokens for -o (write them inside double braces),
shown for January 1 2000, 13:00:00:
  {{YYYY}}  year, 4 digits (2000)      {{HH}}  hour, 24h (13)
  {{YY}}    year, 2 digits (00)        {{hh}}  hour, 12h (01)
  {{MMMM}}  month name (January)       {{mm}}  minute (00)
  {{MMM}}   short month name (Jan)     {{ss}}  second (00)
  {{MM}}    month number (01)          {{a}}   AM/PM (PM)
  {{dd}}    day (01)

example: -o "Jane-Doe_CV_{{YYYY}}-{{MM}}-{{dd}}.docx"  ->  Jane-Doe_CV_2000-01-01.docx
"""


class Parser(argparse.ArgumentParser):
    """Argument parser with friendlier warnings for missing parameters."""

    def __init__(self, *args, **kwargs):
        # Wider option column, so descriptions stay next to their option.
        kwargs.setdefault(
            "formatter_class",
            lambda prog: argparse.RawDescriptionHelpFormatter(
                prog, max_help_position=36
            ),
        )
        super().__init__(*args, **kwargs)

    def error(self, message: str):
        self.print_usage(sys.stderr)
        print(f"\nError: {message}", file=sys.stderr)
        print(f"Run '{self.prog} --help' to see all options.", file=sys.stderr)
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    ap = Parser(
        prog="docxer",
        description="Generate a Word document (.docx) from JSON data and a .docx template.",
        epilog="Run 'docxer <command> -h' for the options of a command.",
    )
    ap.add_argument(
        "-V", "--version", action="version", version=f"docxer {__version__}"
    )
    sub = ap.add_subparsers(dest="command", metavar="<command>", parser_class=Parser)

    ex = sub.add_parser(
        "examples",
        help="copy the example JSON, template DOCX and schema",
        description="Copy input.example.json, template.example.docx and schema.example.json.",
    )
    ex.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("."),
        metavar="<folder>",
        help="folder to copy the files to (default: current folder)",
    )

    cr = sub.add_parser(
        "create",
        help="create a .docx from a JSON file and a template",
        description="Create a .docx from a JSON file and a .docx template.",
        epilog=TOKEN_HELP,
    )
    cr.add_argument(
        "json_file", metavar="<json-file>", type=Path, help="data for the template"
    )
    cr.add_argument(
        "template_file", metavar="<template-docx-file>", type=Path, help="Word template"
    )
    cr.add_argument(
        "-s",
        "--schema",
        type=Path,
        metavar="<schema-json-file>",
        help="JSON Schema to validate the JSON against first (optional)",
    )
    cr.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="<output-docx-file>",
        help=f"output file (default: {DEFAULT_OUTPUT})",
    )
    sub.add_parser(
        "mcp",
        help="run as an MCP server for Claude Desktop (stdio)",
        description="Run docxer as an MCP server over stdio. Claude Desktop starts "
        "this itself; see the README for the config.",
    )
    up = sub.add_parser(
        "update",
        help="update docxer to the latest release",
        description="Download the latest release and replace this docxer with it.",
    )
    up.add_argument("--check", action="store_true", help="only check, do not install")
    return ap


def cmd_examples(dest: Path) -> int:
    src = resources.files("docxer") / "examples"
    dest.mkdir(parents=True, exist_ok=True)
    status = 0
    for name in EXAMPLE_FILES:
        target = dest / name
        if target.exists():
            print(f"Skipped {target} (already exists)", file=sys.stderr)
            status = 1
            continue
        with resources.as_file(src / name) as f:
            shutil.copyfile(f, target)
        print(f"Wrote {target}")
    return status


def cmd_create(
    json_file: Path,
    template_file: Path,
    output: Path | None,
    schema_file: Path | None = None,
) -> int:
    try:
        data = load(json_file)
        out, warnings = create_docx(
            data, template_file, output, schema_file, source=str(json_file)
        )
    except DocxerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)
    print(f"Wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    if args.command is None:
        ap.print_help()
        return 0
    if args.command == "examples":
        return cmd_examples(args.output)
    if args.command == "update":
        return run_update(args.check)
    if args.command == "mcp":
        from .mcp_server import run

        return run()
    if args.command == "create":
        return cmd_create(args.json_file, args.template_file, args.output, args.schema)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
