from bisect import insort
from .heuristics import Heuristic


class ERWA(Heuristic):
    """Exponential Recency Weighted Average(ERWA) algorithm."""
    def __init__(self, sentence, alpha=0.4):
        super().__init__()
        self.alpha = alpha
        self.learn_counter = 0
        self.assigned_at, self.participated_in = {}, {}
        for clause in sentence:
            for literal in clause:
                self.weights[literal] = 0.0
                self.assigned_at[literal] = 0
                self.participated_in[literal] = 0

    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals, sentence=None, assign_info=None):
        """Called after a learnt clause is generated from conflict analysis.
        :param sentence:
        :param assign_info:
        """
        self.learn_counter += 1
        self.alpha = max(0.06, self.alpha - 1e-6)
        for literal in learnt_clause_literals:
            self.participated_in[literal] += 1
        for literal in conflict_side_literals:
            self.participated_in[literal] += 1

    def on_assign(self, literal):
        """Called when a literal is assigned or propagated.
        """
        self.assigned_at[literal] = self.learn_counter
        self.participated_in[literal] = 0

    def on_unassign(self, literal):
        """Called when a literal is unassigned by backtracking or restart."""
        interval = self.learn_counter - self.assigned_at[literal]
        if interval > 0:
            reward = float(self.participated_in[literal]) / interval
            self.weights[literal] = self.alpha * reward + (1 - self.alpha) * self.weights[literal]