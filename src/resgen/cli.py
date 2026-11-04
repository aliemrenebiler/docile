from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from .models import Resume
from .render import format_errors, render
from .settings import (
    INPUT_DIR,
    OUTPUT_DIR,
    SETTINGS_PATH,
    TEMPLATE_DIR,
    format_name,
    load_settings,
)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="resgen", description="Render a CV .docx from JSON."
    )
    ap.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="input JSON file (default: data/inputs/<input_name>.json)",
    )
    ap.add_argument(
        "-o", "--output", type=Path, help="output file (overrides settings)"
    )
    ap.add_argument("-t", "--template", type=Path, help="template (overrides settings)")
    ap.add_argument("-s", "--settings", type=Path, default=SETTINGS_PATH)
    ap.add_argument(
        "--schema", action="store_true", help="print the JSON Schema and exit"
    )
    args = ap.parse_args()

    if args.schema:
        print(json.dumps(Resume.model_json_schema(), indent=2))
        return 0
    try:
        settings = load_settings(args.settings)
        input_path = args.input or INPUT_DIR / f"{settings.input_name}.json"
        template = args.template or TEMPLATE_DIR / f"{settings.template_name}.docx"
        output = args.output or OUTPUT_DIR / (
            format_name(settings.output_name) + ".docx"
        )
        render(input_path, template, output)
    except ValidationError as e:
        print(f"Invalid input:\n{format_errors(e)}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
