"""
The Lexer, responsible for breaking the source code into a stream of tokens.
It uses regex for pattern matching and handles Sundanese keywords.
"""
import re
from typing import List
from .token import Token

class NyundaLexer:
    """Regex-based lexer with Sunda language keywords."""

    def __init__(self):
        # Sunda to English keyword mapping
        self.sunda_keywords = {
            # TODO: benerin kosa kata, blud i forgor sundanese
            'upami': 'if',
            'lamun': 'elif',
            'sanes': 'else',
            'bari': 'while',
            'cetak': 'print',
            'jeung': 'and',
            'atawa': 'or',
            'henteu': 'not',
            'leres': 'true',
            'palsu': 'false'
        }

        # Token patterns (order matters for precedence)
        self.token_patterns = [
            ('NUMBER', r'\d+(\.\d+)?'),
            ('STRING', r'"[^"]*"'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('POWER', r'\*\*'),
            ('EQ', r'=='),
            ('NEQ', r'!='),
            ('LTE', r'<='),
            ('GTE', r'>='),
            ('ASSIGN', r'='),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('MODULO', r'%'),
            ('LT', r'<'),
            ('GT', r'>'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('SEMICOLON', r';'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t]+'),
            ('COMMENT', r'#[^\n]*'),
        ]

        # Compile regex patterns for efficiency
        self.compiled_patterns = [
            (name, re.compile(pattern)) for name, pattern in self.token_patterns
        ]

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize input text using regex patterns."""
        tokens = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            column = 1
            pos = 0

            while pos < len(line):
                matched = False
                for token_type, pattern in self.compiled_patterns:
                    match = pattern.match(line, pos)
                    if match:
                        value = match.group(0)

                        # Skip whitespace and comments
                        if token_type not in ['WHITESPACE', 'COMMENT']:
                            # Translate Sunda keywords
                            if token_type == 'IDENTIFIER' and value in self.sunda_keywords:
                                value = self.sunda_keywords[value]
                                token_type = 'KEYWORD'
                            
                            tokens.append(Token(token_type, value, line_num, column))

                        pos = match.end()
                        column += len(value)
                        matched = True
                        break

                if not matched:
                    raise SyntaxError(f"Invalid character '{line[pos]}' at line {line_num}, column {column}")
        
        return tokens

