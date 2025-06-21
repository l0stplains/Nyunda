"""
Defines the Token data structure used by the lexer and parser.
"""
from dataclasses import dataclass

@dataclass
class Token:
    """Represents a token with its type, value, and position in the source code."""
    type: str
    value: str
    line: int
    column: int

