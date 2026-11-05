from __future__ import annotations

import json
from pathlib import Path

from docxtpl import DocxTemplate
from jinja2 import TemplateError

from .errors import DocxerError


def load(path: Path) -> dict:
    """Read a JSON file that holds an object."""
    if not path.is_file():
        raise DocxerError(f"JSON file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise DocxerError(f"{path} is not valid JSON: {e}") from e
    if not isinstance(data, dict):
        raise DocxerError(f"{path} must contain a JSON object at the top level")
    return data


def open_template(path: Path) -> DocxTemplate:
    if not path.is_file():
        raise DocxerError(f"template not found: {path}")
    if path.suffix.lower() != ".docx":
        raise DocxerError(f"template must be a .docx file: {path}")
    try:
        return DocxTemplate(str(path))
    except Exception as e:  # python-docx raises several types for bad files
        raise DocxerError(f"cannot open template {path}: {e}") from e


def template_variables(template_path: Path) -> list[str]:
    """Top-level names the template uses, sorted."""
    doc = open_template(template_path)
    try:
        return sorted(doc.get_undeclared_template_variables())
    except TemplateError as e:
        raise DocxerError(f"error in template {template_path}: {e}") from e


def render(data: dict, template_path: Path, out_path: Path) -> list[str]:
    """Fill the template with the data. Returns warnings (may be empty)."""
    doc = open_template(template_path)
    try:
        # Top-level names the template uses but the data does not provide.
        missing = sorted(doc.get_undeclared_template_variables() - data.keys())
        doc.render(data)
    except TemplateError as e:
        raise DocxerError(f"error in template {template_path}: {e}") from e
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return [f"template uses '{name}', but the data has no such key" for name in missing]
