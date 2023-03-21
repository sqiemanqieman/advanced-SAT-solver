"""
heuristics.py
define some algorithm/policy to decide which literal to be assigned next.
"""
from bisect import insort
from abc import ABC, abstractmethod


class Heuristic(ABC):
    """The abstract base class for all heuristic branching algorithm of CDCL SAT solver"""
    def __init__(self):
        """Initialize the weights for all literals
        It needs to be keep in ascending order"""
        self.weights = {}

    def decide(self, assigned):
        """Used to decide which **literal** to be assigned next
        always choose the literal with the highest weight"""
        for literal in reversed(self.weights):
            if literal not in assigned and -literal not in assigned:
                return literal
        return None

    def after_bcp(self, conflict_ante):
        """Called after a BCP operation.
        :param conflict_ante: the conflict clause if there is a conflict, None otherwise
        """
        pass

    @abstractmethod
    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals, sentence=None, assign_info=None):
        """Called after a learnt clause is generated from conflict analysis.
        :param sentence:
        :param assign_info:
        """
        pass

    def on_assign(self, literal):
        """Called when a literal is assigned or propagated.
        :param literal:
        """

    def on_unassign(self, literal):
        """Called when a literal is unassigned by backtracking or restart."""
        pass

    def update_weights(self, literals):
        """Rearrange order of literals whose weight changed, maintain them in ascending order."""
        need_adjust_order = []
        for lit in literals:
            need_adjust_order.append((lit, self.weights.pop(lit)))
        weight = list(self.weights.items())
        for i in need_adjust_order:
            insort(weight, i, key=lambda key: key[1])
        self.weights.clear()
        self.weights.update(weight)
