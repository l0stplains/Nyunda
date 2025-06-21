# src/parser.py
"""
The Parser, which consumes tokens from the Lexer and builds an AST.
It uses recursive descent and handles operator precedence.
"""
from typing import List, Optional
from .token import Token
from .ast_nodes import (
    ASTNode, BlockNode, NumberNode, VariableNode, BinaryOpNode,
    AssignmentNode, IfNode, WhileNode, PrintNode, StringNode
)

class NyundaParser:
    """Parser that builds an Abstract Syntax Tree (AST) from tokens."""

    def __init__(self):
        self.tokens: List[Token] = []
        self.pos = 0

    def parse(self, tokens: List[Token]) -> ASTNode:
        """Parse tokens into an AST."""
        self.tokens = [t for t in tokens if t.type != 'NEWLINE']
        self.pos = 0
        return self.parse_program()

    def current_token(self) -> Optional[Token]:
        """Get current token without consuming it."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type: str = None) -> Token:
        """Consume and return current token, with optional type validation."""
        if self.pos >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")
        
        token = self.tokens[self.pos]
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type} but got {token.type} '{token.value}'")
        
        self.pos += 1
        return token

    def parse_program(self) -> BlockNode:
        """Parse an entire program into a block of statements."""
        statements = []
        while self.current_token():
            statements.append(self.parse_statement())
        return BlockNode(statements)

    def parse_block(self) -> List[ASTNode]:
        """Parse a block of code enclosed in braces."""
        self.consume('LBRACE')
        statements = []
        while self.current_token() and self.current_token().type != 'RBRACE':
            statements.append(self.parse_statement())
        self.consume('RBRACE')
        return statements

    def parse_statement(self) -> ASTNode:
        """Parse a single statement."""
        token = self.current_token()
        if not token:
            raise SyntaxError("Expected statement but found end of file.")
        
        if token.type == 'KEYWORD':
            if token.value == 'if':
                return self.parse_if()
            elif token.value == 'while':
                return self.parse_while()
            elif token.value == 'print':
                return self.parse_print()
        elif token.type == 'IDENTIFIER':
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'ASSIGN':
                return self.parse_assignment()
        
        # If it's not a known statement, it must be a standalone expression
        return self.parse_expression()

    def parse_if(self) -> IfNode:
        """Parse an 'if-else' statement."""
        self.consume('KEYWORD')  # consume 'if'
        condition = self.parse_expression()
        then_branch = self.parse_block()
        else_branch = None
        if self.current_token() and self.current_token().type == 'KEYWORD' and self.current_token().value == 'else':
            self.consume('KEYWORD') # consume 'else'
            else_branch = self.parse_block()
        return IfNode(condition, then_branch, else_branch)

    def parse_while(self) -> WhileNode:
        """Parse a 'while' loop."""
        self.consume('KEYWORD') # consume 'while'
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_print(self) -> PrintNode:
        """Parse a 'print' statement."""
        self.consume('KEYWORD') # consume 'print'
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('RPAREN')
        return PrintNode(expr)

    def parse_assignment(self) -> AssignmentNode:
        """Parse an assignment statement."""
        var_name = self.consume('IDENTIFIER').value
        self.consume('ASSIGN')
        value = self.parse_expression()
        return AssignmentNode(var_name, value)

    def parse_expression(self) -> ASTNode:
        """Parse an expression (entry point for expression parsing)."""
        return self.parse_comparison()

    def _parse_binary_op(self, parse_next_level, op_types) -> ASTNode:
        """Generic helper for parsing binary operations with precedence."""
        left = parse_next_level()
        while self.current_token() and self.current_token().type in op_types:
            op = self.consume().value
            right = parse_next_level()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_comparison(self) -> ASTNode:
        """Parse comparison operators (==, !=, <, >, etc.)."""
        return self._parse_binary_op(self.parse_addition, ['EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'])

    def parse_addition(self) -> ASTNode:
        """Parse addition and subtraction."""
        return self._parse_binary_op(self.parse_multiplication, ['PLUS', 'MINUS'])

    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication, division, and modulo."""
        return self._parse_binary_op(self.parse_power, ['MULTIPLY', 'DIVIDE', 'MODULO'])

    def parse_power(self) -> ASTNode:
        """Parse the power operator (**)."""
        return self._parse_binary_op(self.parse_primary, ['POWER'])

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions (literals, variables, parentheses)."""
        token = self.consume()
        
        if token.type == 'NUMBER':
            return NumberNode(float(token.value))
        elif token.type == 'STRING':
            # The token value includes quotes, so we strip them.
            return StringNode(token.value[1:-1])
        elif token.type == 'IDENTIFIER':
            return VariableNode(token.value)
        elif token.type == 'LPAREN':
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token in expression: {token.type} '{token.value}'")

