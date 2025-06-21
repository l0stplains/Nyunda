"""
The Interpreter, the main engine that executes the AST. It walks the tree
and evaluates nodes, managing variable state and control flow. It can be
configured to use a Dynamic Programming evaluator or a standard recursive one.
"""
from typing import Dict, Any
from .ast_nodes import (
    ASTNode, NumberNode, StringNode, VariableNode, BinaryOpNode, AssignmentNode,
    IfNode, WhileNode, PrintNode, BlockNode
)
from .evaluator import DPExpressionEvaluator

class NyundaInterpreter:
    """Executes an AST, with optional support for DP evaluation."""

    def __init__(self, use_dp: bool = True):
        """
        Initializes the interpreter.

        Args:
            use_dp: If True, uses the memoized DP evaluator. 
                    If False, uses a standard recursive evaluator.
        """
        self.variables: Dict[str, Any] = {}
        self.use_dp = use_dp
        self.dp_evaluator = DPExpressionEvaluator() if self.use_dp else None
        self.execution_count = 0

    def interpret(self, ast: ASTNode) -> Any:
        """Interpret Nyunda code from an AST, handling runtime errors."""
        try:
            return self.execute(ast)
        except Exception as e:
            print(f"Runtime Error: {e}")
            return None

    def evaluate_expression(self, node: ASTNode) -> Any:
        """Evaluates an expression node, using DP if enabled."""
        if self.use_dp and self.dp_evaluator:
            return self.dp_evaluator.evaluate_with_dp(node, self.variables)
        return self._evaluate_recursively(node)

    def _evaluate_recursively(self, node: ASTNode) -> Any:
        """A simple, non-memoized recursive evaluator as a fallback."""
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, VariableNode):
            if node.name not in self.variables:
                raise NameError(f"Variable '{node.name}' is not defined.")
            return self.variables[node.name]
        elif isinstance(node, BinaryOpNode):
            left = self._evaluate_recursively(node.left)
            right = self._evaluate_recursively(node.right)
            op_map = {
                '+': lambda a, b: a + b, '-': lambda a, b: a - b,
                '*': lambda a, b: a * b, '/': lambda a, b: a / b,
                '%': lambda a, b: a % b, '**': lambda a, b: a ** b,
                '==': lambda a, b: a == b, '!=': lambda a, b: a != b,
                '<': lambda a, b: a < b, '>': lambda a, b: a > b,
                '<=': lambda a, b: a <= b, '>=': lambda a, b: a >= b,
            }
            if node.operator in op_map:
                try:
                    # Allow string concatenation with '+'
                    if node.operator == '+' and (isinstance(left, str) or isinstance(right, str)):
                        return str(left) + str(right)
                    return op_map[node.operator](left, right)
                except TypeError:
                    raise TypeError(f"Unsupported operand types for {node.operator}: '{type(left).__name__}' and '{type(right).__name__}'")
                except ZeroDivisionError:
                    raise ZeroDivisionError("Division by zero.")
            else:
                raise ValueError(f"Unknown operator: {node.operator}")
        else:
            raise ValueError(f"Cannot evaluate non-expression node type: {type(node).__name__}")

    def execute(self, node: ASTNode) -> Any:
        """Execute an AST node by dispatching to the correct method."""
        self.execution_count += 1
        method_name = f'execute_{type(node).__name__}'
        executor = getattr(self, method_name, self.generic_executor)
        return executor(node)

    def execute_NumberNode(self, node: NumberNode) -> Any:
        return self.evaluate_expression(node)
        
    def execute_StringNode(self, node: StringNode) -> Any:
        return self.evaluate_expression(node)

    def execute_VariableNode(self, node: VariableNode) -> Any:
        return self.evaluate_expression(node)

    def execute_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        return self.evaluate_expression(node)

    def execute_AssignmentNode(self, node: AssignmentNode) -> Any:
        value = self.evaluate_expression(node.value)
        self.variables[node.variable] = value
        return value

    def execute_IfNode(self, node: IfNode) -> Any:
        condition = self.evaluate_expression(node.condition)
        result = None
        if condition:
            for stmt in node.then_branch:
                result = self.execute(stmt)
        elif node.else_branch:
            for stmt in node.else_branch:
                result = self.execute(stmt)
        return result

    def execute_WhileNode(self, node: WhileNode) -> Any:
        result = None
        while self.evaluate_expression(node.condition):
            for stmt in node.body:
                result = self.execute(stmt)
        return result

    def execute_PrintNode(self, node: PrintNode) -> Any:
        value = self.evaluate_expression(node.expression)
        print(value)
        return value

    def execute_BlockNode(self, node: BlockNode) -> Any:
        result = None
        for stmt in node.statements:
            result = self.execute(stmt)
        return result

    def generic_executor(self, node: ASTNode):
        """Fallback for unhandled node types."""
        raise TypeError(f"No execute method for node type {type(node).__name__}")

    def get_dp_stats(self) -> Dict[str, Any]:
        """Get statistics from the dynamic programming evaluator."""
        if self.dp_evaluator:
            return self.dp_evaluator.get_stats()
        return {} # Return empty dict if DP is disabled

