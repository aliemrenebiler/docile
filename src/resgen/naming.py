from __future__ import annotations

import re
from datetime import datetime

# Date/time tokens usable inside {{ }} in the output path.
_TOKENS = {
    "YYYY": "%Y",  # 2026
    "YY": "%y",  # 26
    "MMMM": "%B",  # November
    "MMM": "%b",  # Nov
    "MM": "%m",  # 11
    "dd": "%d",  # 04
    "HH": "%H",  # 00-23
    "hh": "%I",  # 01-12
    "mm": "%M",  # minutes
    "ss": "%S",  # seconds
    "a": "%p",  # AM/PM
}
_TAG = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")

DEFAULT_OUTPUT = "tmp/cv_{{YYYY}}-{{MM}}-{{dd}}_{{HH}}-{{mm}}-{{ss}}.docx"


def format_name(pattern: str, now: datetime | None = None) -> str:
    now = now or datetime.now()

    def sub(m: re.Match) -> str:
        tok = m.group(1)
        if tok not in _TOKENS:
            raise ValueError(
                f"unknown token {{{{{tok}}}}} in output path; "
                f"supported: {', '.join(_TOKENS)}"
            )
        return now.strftime(_TOKENS[tok])

    return _TAG.sub(sub, pattern)
