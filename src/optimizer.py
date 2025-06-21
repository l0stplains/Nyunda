"""
Applies compile-time optimizations to the AST using a Greedy Best-First
Search algorithm. This helps simplify expressions and reduce execution cost.
"""
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from .ast_nodes import ASTNode, BinaryOpNode, NumberNode

@dataclass
class OptimizationState:
    """State for best-first search optimization."""
    ast: ASTNode
    cost: int
    depth: int
    transformations: List[str] = field(default_factory=list)

    def __lt__(self, other):
        return self.cost < other.cost

class GreedyBestFirstOptimizer:
    """Greedy Best-First Search for AST optimization."""

    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.states_explored = 0
        self.transformations_applied = 0

    def optimize(self, ast: ASTNode) -> Tuple[ASTNode, List[str]]:
        """Apply greedy best-first search optimization."""
        initial_cost = ast.cost
        initial_state = OptimizationState(ast, initial_cost, 0, [])
        
        # Priority queue for best-first search
        priority_queue = [initial_state]
        visited_states: Set[str] = set()
        best_state = initial_state

        while priority_queue and len(priority_queue) < 100:  # Limit search space, 100 is large large enough i guess
            current_state = heapq.heappop(priority_queue)
            self.states_explored += 1
            
            state_sig = self._get_state_signature(current_state.ast)
            if state_sig in visited_states:
                continue
            visited_states.add(state_sig)

            if current_state.cost < best_state.cost:
                best_state = current_state
            
            if current_state.depth >= self.max_depth:
                continue
            
            successors = self._generate_successors(current_state)
            for successor in successors:
                heapq.heappush(priority_queue, successor)
        
        return best_state.ast, best_state.transformations

    def _get_state_signature(self, ast: ASTNode) -> str:
        """Generate signature for AST state to avoid cycles."""
        return str(hash(str(ast)))

    def _generate_successors(self, state: OptimizationState) -> List[OptimizationState]:
        """Generate successor states by applying transformations."""
        successors = []
        
        transformations = [
            self._try_constant_folding,
            self._try_algebraic_simplification,
            self._try_strength_reduction,
            self._try_commutative_reorder,
        ]

        for transform_func in transformations:
            # We need to traverse the AST to apply transformations at every level
            new_ast, transform_name = self._apply_transform_recursively(state.ast, transform_func)
            if new_ast is not None and transform_name:
                new_cost = new_ast.cost
                if new_cost < state.cost:
                    new_transformations = state.transformations + [transform_name]
                    successor = OptimizationState(
                        new_ast, new_cost, state.depth + 1, new_transformations
                    )
                    successors.append(successor)
                    self.transformations_applied += 1
        
        return successors

    def _apply_transform_recursively(self, node, transform_func):
        """Helper to apply a transformation function throughout the AST."""
        # First, try to transform the node itself
        transformed_node, name = transform_func(node)
        if transformed_node:
            return transformed_node, name

        # If the node itself isn't transformed, recurse
        if isinstance(node, BinaryOpNode):
            new_left, left_name = self._apply_transform_recursively(node.left, transform_func)
            if new_left: return BinaryOpNode(new_left, node.operator, node.right), left_name

            new_right, right_name = self._apply_transform_recursively(node.right, transform_func)
            if new_right: return BinaryOpNode(node.left, node.operator, new_right), right_name

        # Other node types with children (IfNode, WhileNode, etc.) can be handled here
        
        return None, ""

    def _try_commutative_reorder(self, ast: ASTNode) -> Tuple[Optional[ASTNode], str]:
        """Try reordering commutative operations if it reduces cost."""
        if isinstance(ast, BinaryOpNode) and ast.operator in ['+', '*', '==', '!=']:
            if ast.right.cost < ast.left.cost:
                new_ast = BinaryOpNode(ast.right, ast.operator, ast.left)
                return new_ast, "commutative_reorder"
        return None, ""

    def _try_constant_folding(self, ast: ASTNode) -> Tuple[Optional[ASTNode], str]:
        """Evaluate constant expressions at compile time."""
        if isinstance(ast, BinaryOpNode):
            if isinstance(ast.left, NumberNode) and isinstance(ast.right, NumberNode):
                try:
                    op_map = {
                        '+': lambda a, b: a + b, '-': lambda a, b: a - b,
                        '*': lambda a, b: a * b, '/': lambda a, b: a / b,
                        '**': lambda a, b: a ** b
                    }
                    if ast.operator in op_map:
                        result = op_map[ast.operator](ast.left.value, ast.right.value)
                        return NumberNode(result), "constant_folding"
                except ZeroDivisionError:
                    return None, ""
        return None, ""

    def _try_algebraic_simplification(self, ast: ASTNode) -> Tuple[Optional[ASTNode], str]:
        """Apply algebraic identities."""
        if isinstance(ast, BinaryOpNode):
            # x + 0 = x
            if ast.operator == '+' and isinstance(ast.right, NumberNode) and ast.right.value == 0:
                return ast.left, "add_zero_elimination"
            if ast.operator == '+' and isinstance(ast.left, NumberNode) and ast.left.value == 0:
                return ast.right, "add_zero_elimination"
            
            # x * 1 = x
            if ast.operator == '*' and isinstance(ast.right, NumberNode) and ast.right.value == 1:
                return ast.left, "mul_one_elimination"
            if ast.operator == '*' and isinstance(ast.left, NumberNode) and ast.left.value == 1:
                return ast.right, "mul_one_elimination"

            # x * 0 = 0
            if ast.operator == '*' and isinstance(ast.right, NumberNode) and ast.right.value == 0:
                return NumberNode(0), "mul_zero_elimination"
            if ast.operator == '*' and isinstance(ast.left, NumberNode) and ast.left.value == 0:
                return NumberNode(0), "mul_zero_elimination"
        return None, ""

    def _try_strength_reduction(self, ast: ASTNode) -> Tuple[Optional[ASTNode], str]:
        """Replace expensive operations with cheaper ones."""
        if isinstance(ast, BinaryOpNode):
            # x ** 2 -> x * x
            if ast.operator == '**' and isinstance(ast.right, NumberNode) and ast.right.value == 2:
                return BinaryOpNode(ast.left, '*', ast.left), "power_to_multiply"
            
            # x * 2 -> x + x
            if ast.operator == '*' and isinstance(ast.right, NumberNode) and ast.right.value == 2:
                return BinaryOpNode(ast.left, '+', ast.left), "multiply_to_add"
        return None, ""

    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        return {
            'states_explored': self.states_explored,
            'transformations_applied': self.transformations_applied
        }

