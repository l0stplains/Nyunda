"""
Handles expression evaluation using Dynamic Programming with memoization
to avoid re-computing results for identical subproblems.
"""
from typing import Dict, Any
from .ast_nodes import ASTNode, NumberNode, StringNode, VariableNode, BinaryOpNode

class DPExpressionEvaluator:
    """Dynamic Programming approach for expression evaluation with memoization."""

    def __init__(self):
        # Memoization table for subexpression results
        self.memo_table: Dict[str, Any] = {}
        self.subproblem_count = 0
        self.cache_hits = 0

    def get_expression_key(self, node: ASTNode, variables: Dict[str, Any]) -> str:
        """Generate unique key for expression + variable state."""
        var_state = frozenset(variables.items())
        expr_repr = self._get_node_repr(node)
        return f"{expr_repr}|{hash(var_state)}"

    def _get_node_repr(self, node: ASTNode) -> str:
        """Get string representation of AST node for memoization key."""
        if isinstance(node, NumberNode):
            return f"NUM({node.value})"
        elif isinstance(node, StringNode):
            # Hash the value to prevent overly long keys
            return f"STR({hash(node.value)})"
        elif isinstance(node, VariableNode):
            return f"VAR({node.name})"
        elif isinstance(node, BinaryOpNode):
            left_repr = self._get_node_repr(node.left)
            right_repr = self._get_node_repr(node.right)
            return f"BIN({left_repr},{node.operator},{right_repr})"
        else:
            return str(type(node).__name__)

    def evaluate_with_dp(self, node: ASTNode, variables: Dict[str, Any]) -> Any:
        """Evaluate expression using dynamic programming."""
        key = self.get_expression_key(node, variables)

        # Check if we've already computed this subproblem
        if key in self.memo_table:
            self.cache_hits += 1
            return self.memo_table[key]

        self.subproblem_count += 1

        # Compute result
        if isinstance(node, NumberNode):
            result = node.value
        elif isinstance(node, StringNode):
            result = node.value
        elif isinstance(node, VariableNode):
            if node.name not in variables:
                raise NameError(f"Variable '{node.name}' is not defined")
            result = variables[node.name]
        elif isinstance(node, BinaryOpNode):
            # Recursively evaluate subexpressions (overlapping subproblems)
            left = self.evaluate_with_dp(node.left, variables)
            right = self.evaluate_with_dp(node.right, variables)
            
            op_map = {
                '+': lambda a, b: a + b, '-': lambda a, b: a - b,
                '*': lambda a, b: a * b, '/': lambda a, b: a / b,
                '%': lambda a, b: a % b, '**': lambda a, b: a ** b,
                '==': lambda a, b: a == b, '!=': lambda a, b: a != b,
                '<': lambda a, b: a < b, '>': lambda a, b: a > b,
                '<=': lambda a, b: a <= b, '>=': lambda a, b: a >= b,
            }
            if node.operator in op_map:
                result = op_map[node.operator](left, right)
            else:
                raise ValueError(f"Unknown operator: {node.operator}")
        else:
            raise ValueError(f"Cannot evaluate node type: {type(node)}")

        # Memoize result
        self.memo_table[key] = result
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get DP statistics."""
        hit_rate = (self.cache_hits / max(1, self.subproblem_count)) * 100
        return {
            'subproblems_solved': self.subproblem_count,
            'cache_hits': self.cache_hits,
            'memo_table_size': len(self.memo_table),
            'hit_rate': f"{hit_rate:.2f}%"
        }

