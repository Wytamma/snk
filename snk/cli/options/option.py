from dataclasses import dataclass
from typing import Any


@dataclass
class Option:
    name: str
    original_key: str
    default: Any
    updated: bool
    help: str
    type: Any
    required: bool