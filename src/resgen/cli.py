from __future__ import annotations

import argparse
import json
import shutil
import sys
from importlib import resources
from pathlib import Path

from pydantic import ValidationError

from .models import Resume
from .naming import DEFAULT_OUTPUT, format_name
from .render import format_errors, render

EXAMPLE_FILES = ("input.example.json", "template.example.docx")


class Parser(argparse.ArgumentParser):
    """Argument parser with friendlier warnings for missing parameters."""

    def error(self, message: str):
        self.print_usage(sys.stderr)
        print(f"\nError: {message}", file=sys.stderr)
        print(f"Run '{self.prog} --help' to see all options.", file=sys.stderr)
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    ap = Parser(
        prog="resgen",
        description="Generate a Word CV (.docx) from a JSON file and a .docx template.",
    )
    sub = ap.add_subparsers(dest="command", metavar="<command>", parser_class=Parser)

    sub.add_parser("help", help="show this help, or help for a command")
    sub.choices["help"].add_argument("topic", nargs="?", metavar="<command>")

    ex = sub.add_parser(
        "examples",
        help="copy the example input JSON and template DOCX",
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
        help="create a CV .docx from a JSON file and a template",
        description="Create a CV .docx from a JSON file and a .docx template.",
    )
    cr.add_argument("json_file", metavar="<json-file>", type=Path, help="CV data")
    cr.add_argument(
        "template_file", metavar="<template-docx-file>", type=Path, help="Word template"
    )
    cr.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="<output-docx-file>",
        help=f"output file (default: {DEFAULT_OUTPUT}); "
        "date/time tokens like {{YYYY}} {{MM}} {{dd}} {{HH}} {{mm}} {{ss}} work",
    )

    sub.add_parser("schema", help="print the JSON Schema of the input and exit")
    return ap


def cmd_examples(dest: Path) -> int:
    src = resources.files("resgen") / "examples"
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
        render(json_file, template_file, out)
    except ValidationError as e:
        print(f"Invalid input:\n{format_errors(e)}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: {json_file} is not valid JSON: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    if args.command in (None, "help"):
        topic = getattr(args, "topic", None)
        if topic:
            choices = ap._subparsers._group_actions[0].choices
            if topic not in choices:
                ap.error(f"unknown command '{topic}'")
            choices[topic].print_help()
        else:
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
    if args.command == "schema":
        print(json.dumps(Resume.model_json_schema(), indent=2))
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
