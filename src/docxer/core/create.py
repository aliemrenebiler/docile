from __future__ import annotations

from pathlib import Path

from .errors import DocxerError, OutputExists
from .naming import DEFAULT_OUTPUT, format_name
from .render import render, template_variables
from .schema import validate

__all__ = ["DocxerError", "OutputExists", "create_docx", "template_variables"]


def create_docx(
    data: dict,
    template: Path,
    output: Path | None = None,
    schema: Path | dict | None = None,
    source: str = "the data",
    overwrite: bool = False,
) -> tuple[Path, list[str]]:
    """Validate (if a schema is given, as a file or an object), then fill the template.

    Returns the written path and warnings. `source` names the data in error
    messages. `output` may contain date/time tokens, and may be a folder.
    Raises OutputExists if the output file exists and `overwrite` is False;
    nothing is written then.
    """
    if schema is not None:
        errors = validate(data, schema)
        if errors:
            lines = "".join(f"\n  {e}" for e in errors)
            name = schema if isinstance(schema, Path) else "the schema"
            raise DocxerError(f"{source} does not match {name}:{lines}")
    try:
        out = Path(format_name(str(output or DEFAULT_OUTPUT)))
    except ValueError as e:
        raise DocxerError(str(e)) from e
    if out.is_dir():
        out = out / Path(format_name(DEFAULT_OUTPUT)).name
    if out.exists() and not overwrite:
        raise OutputExists(out)
    warnings = render(data, template, out)
    return out, warnings
