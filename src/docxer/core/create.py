from __future__ import annotations

from pathlib import Path

from .errors import DocxerError
from .naming import DEFAULT_OUTPUT, format_name
from .render import render, template_variables
from .schema import validate

__all__ = ["DocxerError", "create_docx", "template_variables"]


def create_docx(
    data: dict,
    template: Path,
    output: Path | None = None,
    schema: Path | None = None,
    source: str = "the data",
) -> tuple[Path, list[str]]:
    """Validate (if a schema is given), then fill the template.

    Returns the written path and warnings. `source` names the data in error
    messages. `output` may contain date/time tokens, and may be a folder.
    """
    if schema is not None:
        errors = validate(data, schema)
        if errors:
            lines = "".join(f"\n  {e}" for e in errors)
            raise DocxerError(f"{source} does not match {schema}:{lines}")
    try:
        out = Path(format_name(str(output or DEFAULT_OUTPUT)))
    except ValueError as e:
        raise DocxerError(str(e)) from e
    if out.is_dir():
        out = out / Path(format_name(DEFAULT_OUTPUT)).name
    warnings = render(data, template, out)
    return out, warnings
