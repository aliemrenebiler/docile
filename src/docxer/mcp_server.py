"""MCP server: lets Claude Desktop (or any MCP client) use docxer as tools.

Runs over stdio, started by the client itself, so there is nothing to keep
running. Nothing may be printed to stdout here: it carries the protocol.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .core import DocxerError, create_docx, template_variables
from .core.schema import validate

mcp = FastMCP(
    "docxer",
    instructions=(
        "Create Word documents from JSON data and a .docx template. Typical flow: "
        "get_template_variables to see what the template needs, get_examples for the "
        "expected JSON shape, then create_docx_file. All file paths must be absolute."
    ),
)


def _path(value: str, what: str) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        raise ValueError(f"{what} must be an absolute path, got: {value}")
    return p


def _wrap(fn):
    """Run fn, turning docxer errors into plain tool errors."""
    try:
        return fn()
    except DocxerError as e:
        raise ValueError(str(e)) from e


@mcp.tool()
def create_docx_file(
    data: dict,
    template_path: str,
    output_path: str | None = None,
    schema_path: str | None = None,
) -> str:
    """Fill a .docx template with data and save the result.

    data: the JSON object for the template (its top-level keys are the names the
        template uses).
    template_path: absolute path of the .docx template.
    output_path: absolute path of the file to write, or a folder. Default: the
        template's folder. May contain date/time tokens like {{YYYY}}-{{MM}}-{{dd}}.
    schema_path: optional absolute path of a JSON Schema. If given, the data is
        validated first and nothing is written when it does not match.
    """

    def run() -> str:
        template = _path(template_path, "template_path")
        output = _path(output_path, "output_path") if output_path else template.parent
        schema = _path(schema_path, "schema_path") if schema_path else None
        out, warnings = create_docx(data, template, output, schema)
        return "\n".join([f"Wrote {out}"] + [f"Warning: {w}" for w in warnings])

    return _wrap(run)


@mcp.tool()
def validate_json(data: dict, schema_path: str) -> str:
    """Check data against a JSON Schema file without creating anything.

    Returns "valid", or one line per problem with its location (like
    $.experience[0].start.year), so the data can be fixed and checked again.
    """

    def run() -> str:
        errors = validate(data, _path(schema_path, "schema_path"))
        return "valid" if not errors else "\n".join(errors)

    return _wrap(run)


@mcp.tool()
def get_template_variables(template_path: str) -> list[str]:
    """List the top-level names a .docx template uses, i.e. the keys the data needs."""
    return _wrap(lambda: template_variables(_path(template_path, "template_path")))


@mcp.tool()
def get_examples() -> dict:
    """Return the example input JSON and example JSON Schema that ship with docxer."""
    base = resources.files("docxer") / "examples"
    return {
        name: json.loads((base / name).read_text(encoding="utf-8"))
        for name in ("input.example.json", "schema.example.json")
    }


def run() -> int:
    mcp.run(transport="stdio")
    return 0
