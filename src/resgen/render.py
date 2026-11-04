from __future__ import annotations

import json
from pathlib import Path

from docxtpl import DocxTemplate
from pydantic import ValidationError

from .models import Resume

PRESENT = {"month": "Present", "year": ""}
EMPTY = {"month": "", "year": ""}


def load(path: Path) -> Resume:
    return Resume.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _fmt(d: dict | None) -> str:
    return f"{d['month']} {d['year']}".strip() if d else ""


def _context(resume: Resume) -> dict:
    ctx = resume.model_dump(mode="json")
    for section in ("education", "experience", "volunteering"):
        for item in ctx[section]:
            # "dates": "Mar 2021 - Present"; empty when there is no start date,
            # so templates can hide the line with {%p if x.dates %}.
            start, end = _fmt(item["start"]), _fmt(item["end"]) or "Present"
            item["dates"] = f"{start} \u2013 {end}" if start else ""
            # Templates that print month/year directly never see null.
            item["start"] = item["start"] or EMPTY
            item["end"] = item["end"] or PRESENT
    for item in ctx["certification"]:
        item["dates"] = _fmt(item["date"])
        item["date"] = item["date"] or EMPTY
    return ctx


def render(data_path: Path, template_path: Path, out_path: Path) -> None:
    resume = load(data_path)
    doc = DocxTemplate(str(template_path))
    doc.render(_context(resume))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))


def format_errors(err: ValidationError) -> str:
    return "\n".join(
        f"  {'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in err.errors()
    )
