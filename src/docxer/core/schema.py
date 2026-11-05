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


def validate(data: dict, schema_path: Path) -> list[str]:
    """Check data against a JSON Schema file. Returns error lines (empty = valid).

    Raises DocxerError if the schema file is missing or is not a valid schema.
    """
    if not schema_path.is_file():
        raise DocxerError(f"schema not found: {schema_path}")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise DocxerError(f"{schema_path} is not valid JSON: {e}") from e
    cls = validators.validator_for(schema, default=Draft202012Validator)
    try:
        cls.check_schema(schema)
    except SchemaError as e:
        raise DocxerError(f"{schema_path} is not a valid JSON Schema: {e.message}")
    errors = sorted(cls(schema).iter_errors(data), key=lambda e: list(e.absolute_path))
    return [f"{_where(e.absolute_path)}: {e.message}" for e in errors]
