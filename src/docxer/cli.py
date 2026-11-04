from __future__ import annotations

import argparse
import json
import shutil
import sys
from importlib import resources
from pathlib import Path

from jinja2 import TemplateError

from .naming import DEFAULT_OUTPUT, format_name
from .render import render

EXAMPLE_FILES = ("input.example.json", "template.example.docx")

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
    sub = ap.add_subparsers(dest="command", metavar="<command>", parser_class=Parser)

    ex = sub.add_parser(
        "examples",
        help="copy the example JSON and template DOCX",
        description="Copy input.example.json and template.example.docx.",
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
        "-o",
        "--output",
        type=Path,
        metavar="<output-docx-file>",
        help=f"output file (default: {DEFAULT_OUTPUT})",
    )
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


def cmd_create(json_file: Path, template_file: Path, output: Path | None) -> int:
    if not json_file.is_file():
        print(f"Error: JSON file not found: {json_file}", file=sys.stderr)
        return 1
    if not template_file.is_file():
        print(f"Error: template not found: {template_file}", file=sys.stderr)
        return 1
    if template_file.suffix.lower() != ".docx":
        print(f"Error: template must be a .docx file: {template_file}", file=sys.stderr)
        return 1
    out = Path(format_name(str(output or DEFAULT_OUTPUT)))
    if out.is_dir():
        out = out / Path(format_name(DEFAULT_OUTPUT)).name
    try:
        warnings = render(json_file, template_file, out)
    except json.JSONDecodeError as e:
        print(f"Error: {json_file} is not valid JSON: {e}", file=sys.stderr)
        return 1
    except TemplateError as e:
        print(f"Error in template {template_file}: {e}", file=sys.stderr)
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
    if args.command == "create":
        try:
            return cmd_create(args.json_file, args.template_file, args.output)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
