from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# Supported tokens inside {{ }} in output_name.
_TOKENS = {
    "YYYY": "%Y",  # 2026
    "YY": "%y",    # 26
    "MMMM": "%B",  # November
    "MMM": "%b",   # Nov
    "MM": "%m",    # 11
    "dd": "%d",    # 04
    "HH": "%H",    # 00-23
    "hh": "%I",    # 01-12
    "mm": "%M",    # minutes
    "ss": "%S",    # seconds
    "a": "%p",     # AM/PM
}
_TAG = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template_name: str = "cv"  # data/templates/<template_name>.docx
    input_name: str = "me"  # data/inputs/<input_name>.json
    output_name: str = "CV_{{YYYY}}-{{MM}}-{{dd}}_{{HH}}-{{mm}}-{{ss}}"


TEMPLATE_DIR = Path("data/templates")
INPUT_DIR = Path("data/inputs")
SETTINGS_PATH = Path("data/settings.json")
OUTPUT_DIR = Path("data/outputs")


def load_settings(path: Path) -> Settings:
    if not path.exists():
        return Settings()
    return Settings.model_validate(json.loads(path.read_text(encoding="utf-8")))


def format_name(pattern: str, now: datetime | None = None) -> str:
    now = now or datetime.now()

    def sub(m: re.Match) -> str:
        tok = m.group(1)
        if tok not in _TOKENS:
            raise ValueError(
                f"unknown token {{{{{tok}}}}} in output_name; "
                f"supported: {', '.join(_TOKENS)}"
            )
        return now.strftime(_TOKENS[tok])

    return _TAG.sub(sub, pattern)
