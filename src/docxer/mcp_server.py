"""MCP server: lets Claude Desktop (or any MCP client) use docxer as tools.

Runs over stdio, started by the client itself, so there is nothing to keep
running. Nothing may be printed to stdout here: it carries the protocol.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .core import DocxerError, OutputExists, create_docx, template_variables
from .core.render import load
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


def _json_input(inline: dict | None, path: str | None, name: str, required: bool):
    """Pick one of an inline JSON object or a file path.

    Returns the object (data) / object-or-Path (schema), or None if optional and
    not given. Giving both, or neither when required, is an error.
    """
    if inline is not None and path:
        raise ValueError(f"give either {name} or {name}_path, not both")
    if inline is None and not path:
        if required:
            raise ValueError(f"give {name} (inline JSON) or {name}_path (a file)")
        return None
    if inline is not None:
        return inline
    p = _path(path, f"{name}_path")
    # Data is read here so a bad file is reported at once; a schema file is read
    # by the validator.
    return load(p) if name == "data" else p


@mcp.tool()
def create_docx_file(
    template_path: str,
    data: dict | None = None,
    data_path: str | None = None,
    schema: dict | None = None,
    schema_path: str | None = None,
    output_path: str | None = None,
    overwrite: bool = False,
) -> str:
    """Fill a .docx template with JSON data and save the result.

    template_path: absolute path of the .docx template (must be a file on this
        computer).
    data / data_path: the JSON data for the template. Give exactly one: `data`
        is the JSON object itself (its top-level keys are the names the template
        uses), `data_path` is the absolute path of a JSON file.
    schema / schema_path: optional JSON Schema, as an inline object or as an
        absolute file path (not both). If given, the data is validated first and
        nothing is written when it does not match.
    output_path: absolute path of the file to write, or a folder. Default: the
        template's folder. May contain date/time tokens like {{YYYY}}-{{MM}}-{{dd}}.
    overwrite: if the output file already exists, nothing is written and an
        error says so. Ask the user whether to overwrite it; only if they say
        yes, call again with overwrite=true.
    """

    def run() -> str:
        template = _path(template_path, "template_path")
        values = _json_input(data, data_path, "data", required=True)
        schema_in = _json_input(schema, schema_path, "schema", required=False)
        output = _path(output_path, "output_path") if output_path else template.parent
        try:
            out, warnings = create_docx(
                values, template, output, schema_in, overwrite=overwrite
            )
        except OutputExists as e:
            raise ValueError(
                f"{e.path} already exists and was not changed. Ask the user whether "
                "to overwrite it, then call again with overwrite=true."
            ) from e
        return "\n".join([f"Wrote {out}"] + [f"Warning: {w}" for w in warnings])

    return _wrap(run)


@mcp.tool()
def validate_json(
    data: dict | None = None,
    data_path: str | None = None,
    schema: dict | None = None,
    schema_path: str | None = None,
) -> str:
    """Check JSON data against a JSON Schema without creating anything.

    Give exactly one of data / data_path (inline object or absolute file path)
    and exactly one of schema / schema_path. Returns "valid", or one line per
    problem with its location (like $.experience[0].start.year), so the data can
    be fixed and checked again.
    """

    def run() -> str:
        values = _json_input(data, data_path, "data", required=True)
        schema_in = _json_input(schema, schema_path, "schema", required=True)
        errors = validate(values, schema_in)
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
