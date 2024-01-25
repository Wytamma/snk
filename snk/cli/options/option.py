from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Option:
    name: str
    original_key: str
    default: Any
    updated: bool
    help: str
    type: Any
    required: bool
    short: Optional[str]
    flag: str
    short_flag: Optional[str]
    hidden: bool = False
    from_annotation: bool = False
