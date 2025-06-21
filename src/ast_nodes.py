"""
Defines the structure of the Abstract Syntax Tree (AST).

Each node represents a part of the code's structure and includes a cost
calculation to estimate its execution complexity.
"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Optional

# AST Node Definitions

@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes with cost tracking."""
    cost: int = field(default=0, init=False)

    def __post_init__(self):
        self.cost = self.calculate_cost()

    @abstractmethod
    def calculate_cost(self) -> int:
        """Calculate execution cost of this node."""
        pass

@dataclass
class NumberNode(ASTNode):
    """Node for numeric literals."""
    value: float

    def calculate_cost(self) -> int:
        return 1

@dataclass
class StringNode(ASTNode):
    """Node for string literals."""
    value: str

    def calculate_cost(self) -> int:
        # Cost for a string is minimal for now.
        return 1

@dataclass
class VariableNode(ASTNode):
    """Node for variable identifiers."""
    name: str

    def calculate_cost(self) -> int:
        return 2

@dataclass
class BinaryOpNode(ASTNode):
    """Node for binary operations (e.g., +, *, ==)."""
    left: ASTNode
    operator: str
    right: ASTNode

    def calculate_cost(self) -> int:
        left_cost = getattr(self.left, 'cost', 0)
        right_cost = getattr(self.right, 'cost', 0)
        op_costs = {
            '**': 20, '*': 8, '/': 10, '%': 12, '+': 3, '-': 3,
            '==': 4, '!=': 4, '<': 4, '>': 4, '<=': 4, '>=': 4
        }
        return left_cost + right_cost + op_costs.get(self.operator, 5)

@dataclass
class AssignmentNode(ASTNode):
    """Node for variable assignments."""
    variable: str
    value: ASTNode

    def calculate_cost(self) -> int:
        return 5 + getattr(self.value, 'cost', 0)

@dataclass
class IfNode(ASTNode):
    """Node for conditional 'if-else' statements."""
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None

    def calculate_cost(self) -> int:
        cost = 15 + getattr(self.condition, 'cost', 0)
        cost += sum(getattr(stmt, 'cost', 0) for stmt in self.then_branch)
        if self.else_branch:
            cost += sum(getattr(stmt, 'cost', 0) for stmt in self.else_branch)
        return cost

@dataclass
class WhileNode(ASTNode):
    """Node for 'while' loops."""
    condition: ASTNode
    body: List[ASTNode]

    def calculate_cost(self) -> int:
        # Estimate loop cost (condition + body) * estimated iterations
        condition_cost = getattr(self.condition, 'cost', 0)
        body_cost = sum(getattr(stmt, 'cost', 0) for stmt in self.body)
        return (condition_cost + body_cost) * 10  # Assume 10 iterations, idk, im kinda near deadline

@dataclass
class PrintNode(ASTNode):
    """Node for 'print' statements."""
    expression: ASTNode

    def calculate_cost(self) -> int:
        return 8 + getattr(self.expression, 'cost', 0)

@dataclass
class BlockNode(ASTNode):
    """Node representing a block of statements."""
    statements: List[ASTNode]

    def calculate_cost(self) -> int:
        return sum(getattr(stmt, 'cost', 0) for stmt in self.statements)

