"""MCP server: lets Claude Desktop (or any MCP client) use docile as tools.

Runs over stdio, started by the client itself, so there is nothing to keep
running. Nothing may be printed to stdout here: it carries the protocol.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .core import DocileError, OutputExists, create_docx, template_variables
from .core.render import load
from .core.schema import validate

mcp = FastMCP(
    "docile",
    instructions=(
        "Render Word documents from JSON data and a .docx template. Typical flow: "
        "get_template_variables to see what the template needs, get_examples for the "
        "expected JSON shape, then render_docx. All file paths must be absolute."
    ),
)


def _path(value: str, what: str) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        raise ValueError(f"{what} must be an absolute path, got: {value}")
    return p


def _wrap(fn):
    """Run fn, turning docile errors into plain tool errors."""
    try:
        return fn()
    except DocileError as e:
        raise ValueError(str(e)) from e


def _data_input(data: dict | None, data_path: str | None) -> dict:
    """Pick one of inline JSON data or a JSON file path."""
    if data is not None and data_path:
        raise ValueError("give either data or data_path, not both")
    if data is None and not data_path:
        raise ValueError("give data (inline JSON) or data_path (a file)")
    if data is not None:
        return data
    return load(_path(data_path, "data_path"))


@mcp.tool()
def render_docx(
    template_path: str,
    data: dict | None = None,
    data_path: str | None = None,
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
    schema_path: optional absolute path of a JSON Schema file on this computer.
        If given, the data is validated first and nothing is written when it
        does not match.
    output_path: absolute path of the file to write, or a folder. Default: the
        template's folder. May contain date/time tokens like {{YYYY}}-{{MM}}-{{dd}}.
    overwrite: if the output file already exists, nothing is written and an
        error says so. Ask the user whether to overwrite it; only if they say
        yes, call again with overwrite=true.
    """

    def run() -> str:
        template = _path(template_path, "template_path")
        values = _data_input(data, data_path)
        schema = _path(schema_path, "schema_path") if schema_path else None
        output = _path(output_path, "output_path") if output_path else template.parent
        try:
            out, warnings = create_docx(
                values, template, output, schema, overwrite=overwrite
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
    schema_path: str,
    data: dict | None = None,
    data_path: str | None = None,
) -> str:
    """Check JSON data against a JSON Schema file without creating anything.

    schema_path: absolute path of the JSON Schema file on this computer.
    data / data_path: give exactly one (inline JSON object or absolute file path).
    Returns "valid", or one line per problem with its location (like
    $.experience[0].start.year), so the data can be fixed and checked again.
    """

    def run() -> str:
        values = _data_input(data, data_path)
        errors = validate(values, _path(schema_path, "schema_path"))
        return "valid" if not errors else "\n".join(errors)

    return _wrap(run)


@mcp.tool()
def get_template_variables(template_path: str) -> list[str]:
    """List the top-level names a .docx template uses, i.e. the keys the data needs."""
    return _wrap(lambda: template_variables(_path(template_path, "template_path")))


@mcp.tool()
def get_examples() -> dict:
    """Return the example input JSON and example JSON Schema that ship with docile."""
    base = resources.files("docile") / "examples"
    return {
        name: json.loads((base / name).read_text(encoding="utf-8"))
        for name in ("input.example.json", "schema.example.json")
    }


def _reject_unknown_args() -> None:
    """Make every tool fail on arguments it does not have.

    FastMCP drops unknown arguments silently, so a typo such as `schema=` would
    skip validation without a word. Forbidding extras turns that into an error.
    """
    for tool in mcp._tool_manager.list_tools():
        model = tool.fn_metadata.arg_model
        model.model_config["extra"] = "forbid"
        model.model_rebuild(force=True)


_reject_unknown_args()


def run() -> int:
    mcp.run(transport="stdio")
    return 0
