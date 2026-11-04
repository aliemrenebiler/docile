from __future__ import annotations

import json
from pathlib import Path

from docxtpl import DocxTemplate


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object at the top level")
    return data


def render(data_path: Path, template_path: Path, out_path: Path) -> list[str]:
    """Fill the template with the JSON data. Returns warnings (may be empty)."""
    data = load(data_path)
    doc = DocxTemplate(str(template_path))
    # Top-level names the template uses but the JSON does not provide.
    missing = sorted(doc.get_undeclared_template_variables() - data.keys())
    doc.render(data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return [f"template uses '{name}', but the JSON has no such key" for name in missing]
