from dataclasses import dataclass


@dataclass
class Option:
    name: str
    original_key: str
    default: any
    updated: bool
    help: str
    type: str
    required: bool