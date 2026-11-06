from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, validators
from jsonschema.exceptions import SchemaError

from .errors import DocxerError


def _where(path) -> str:
    """JSON path like $.education[0].start for an error location."""
    out = "$"
    for part in path:
        out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out


def load_schema(path: Path) -> dict:
    """Read a JSON Schema file. Raises DocxerError if it is missing or not JSON."""
    if not path.is_file():
        raise DocxerError(f"schema not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise DocxerError(f"{path} is not valid JSON: {e}") from e


def validate(data: dict, schema: Path | dict) -> list[str]:
    """Check data against a JSON Schema, given as a file or as an object.

    Returns error lines (empty = valid). Raises DocxerError if the schema file
    is missing or the schema is not a valid JSON Schema.
    """
    label = str(schema) if isinstance(schema, Path) else "the schema"
    if isinstance(schema, Path):
        schema = load_schema(schema)
    cls = validators.validator_for(schema, default=Draft202012Validator)
    try:
        cls.check_schema(schema)
    except SchemaError as e:
        raise DocxerError(f"{label} is not a valid JSON Schema: {e.message}")
    errors = sorted(cls(schema).iter_errors(data), key=lambda e: list(e.absolute_path))
    return [f"{_where(e.absolute_path)}: {e.message}" for e in errors]
