# src/optimizer.py
"""
Applies compile-time optimizations to the AST using a Greedy Best-First
Search algorithm. This helps simplify expressions and reduce execution cost.
"""
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from copy import deepcopy
from .ast_nodes import ASTNode, BinaryOpNode, NumberNode, BlockNode, IfNode, WhileNode, AssignmentNode, PrintNode

@dataclass(frozen=True, eq=False) # Use frozen, but define custom eq/hash based on string
class OptimizationState:
    """State for best-first search optimization."""
    ast: ASTNode
    cost: int
    depth: int
    transformations: Tuple[str, ...]

    def __lt__(self, other):
        if self.cost == other.cost:
            return self.depth < other.depth
        return self.cost < other.cost

    def __eq__(self, other):
        return isinstance(other, OptimizationState) and str(self.ast) == str(other.ast)

    def __hash__(self):
        return hash(str(self.ast))

class GreedyBestFirstOptimizer:
    """Greedy Best-First Search for AST optimization."""

    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.states_explored = 0
        self.transformations_applied = 0

    def optimize(self, ast: ASTNode) -> Tuple[ASTNode, List[str]]:
        """Apply greedy best-first search optimization."""
        initial_cost = ast.cost
        initial_state = OptimizationState(ast, initial_cost, 0, tuple())
        
        priority_queue = [initial_state]
        visited_states: Set[str] = {str(initial_state.ast)}
        best_state = initial_state

        while priority_queue:
            current_state = heapq.heappop(priority_queue)
            self.states_explored += 1

            if current_state.cost < best_state.cost:
                best_state = current_state
            
            if current_state.depth >= self.max_depth:
                continue
            
            for new_ast, transform_name in self._get_transformed_asts(current_state.ast):
                new_cost = new_ast.cost
                state_signature = str(new_ast)

                if state_signature not in visited_states:
                    if new_cost < current_state.cost: # Only consider profitable transformations
                        self.transformations_applied += 1
                        new_transformations = current_state.transformations + (transform_name,)
                        new_state = OptimizationState(new_ast, new_cost, current_state.depth + 1, new_transformations)
                        heapq.heappush(priority_queue, new_state)
                        visited_states.add(state_signature)
        
        return best_state.ast, list(best_state.transformations)

    def _get_transformed_asts(self, node: ASTNode):
        """
        A generator that recursively yields all possible single-transformation
        versions of the given AST node.
        """
        # yield transformations from children (post-order traversal)
        if isinstance(node, BlockNode):
            for i, stmt in enumerate(node.statements):
                for transformed_stmt, name in self._get_transformed_asts(stmt):
                    new_statements = node.statements[:]
                    new_statements[i] = transformed_stmt
                    yield BlockNode(new_statements), name
        elif isinstance(node, AssignmentNode):
            for new_value, name in self._get_transformed_asts(node.value):
                yield AssignmentNode(node.variable, new_value), name
        elif isinstance(node, PrintNode):
            for new_expr, name in self._get_transformed_asts(node.expression):
                yield PrintNode(new_expr), name
        elif isinstance(node, BinaryOpNode):
            for new_left, name in self._get_transformed_asts(node.left):
                yield BinaryOpNode(new_left, node.operator, node.right), name
            for new_right, name in self._get_transformed_asts(node.right):
                yield BinaryOpNode(node.left, node.operator, new_right), name
        elif isinstance(node, IfNode):
             for new_cond, name in self._get_transformed_asts(node.condition):
                yield IfNode(new_cond, node.then_branch, node.else_branch), name
        elif isinstance(node, WhileNode):
            for new_cond, name in self._get_transformed_asts(node.condition):
                yield WhileNode(new_cond, node.body), name

        # yield transformations for the node itself
        transformation_rules = [
            self._try_constant_folding,
            self._try_algebraic_simplification,
            self._try_strength_reduction,
        ]
        for rule in transformation_rules:
            transformed_node, name = rule(node)
            if transformed_node:
                yield transformed_node, name

    def _try_constant_folding(self, node: ASTNode) -> Tuple[Optional[ASTNode], str]:
        if isinstance(node, BinaryOpNode) and isinstance(node.left, NumberNode) and isinstance(node.right, NumberNode):
            try:
                op_map = {'+': float.__add__, '-': float.__sub__, '*': float.__mul__, '/': float.__truediv__, '**': float.__pow__}
                if node.operator in op_map:
                    result = op_map[node.operator](node.left.value, node.right.value)
                    return NumberNode(result), "constant_folding"
            except ZeroDivisionError:
                return None, ""
        return None, ""

    def _try_algebraic_simplification(self, node: ASTNode) -> Tuple[Optional[ASTNode], str]:
        if isinstance(node, BinaryOpNode):
            if node.operator == '+' and isinstance(node.right, NumberNode) and node.right.value == 0: return node.left, "identity_add"
            if node.operator == '+' and isinstance(node.left, NumberNode) and node.left.value == 0: return node.right, "identity_add"
            if node.operator == '*' and isinstance(node.right, NumberNode) and node.right.value == 1: return node.left, "identity_mul"
            if node.operator == '*' and isinstance(node.left, NumberNode) and node.left.value == 1: return node.right, "identity_mul"
            if node.operator == '*' and isinstance(node.right, NumberNode) and node.right.value == 0: return NumberNode(0), "mul_by_zero"
            if node.operator == '*' and isinstance(node.left, NumberNode) and node.left.value == 0: return NumberNode(0), "mul_by_zero"
        return None, ""

    def _try_strength_reduction(self, node: ASTNode) -> Tuple[Optional[ASTNode], str]:
        if isinstance(node, BinaryOpNode):
            if node.operator == '**' and isinstance(node.right, NumberNode) and node.right.value == 2:
                # USe deepcopy to ensure the nodes are distinct objects if needed later
                return BinaryOpNode(deepcopy(node.left), '*', deepcopy(node.left)), "strength_reduction_pow2"
        return None, ""

    def get_stats(self) -> Dict[str, Any]:
        return {
            'states_explored': self.states_explored,
            'transformations_applied': self.transformations_applied
        }

