#!/usr/bin/env python3
from __future__ import annotations

import re


TASK_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def validate_task_name(name: str) -> None:
    if not TASK_NAME_RE.fullmatch(name):
        raise ValueError(
            "task_name must start with a letter or number and contain only "
            "letters, numbers, underscores, or hyphens"
        )
    device_name = name.split(".", 1)[0].upper()
    if device_name in WINDOWS_RESERVED_NAMES:
        raise ValueError(f"task_name uses a Windows reserved device name: {device_name}")
