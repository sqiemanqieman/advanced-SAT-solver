from .ERWA import ERWA


class RSR(ERWA):
    """ERWA with Reason Side Rate (RSR) extension."""
    def __init__(self, sentence, alpha=0.4):
        self.reasoned_in = {}
        super().__init__(sentence, alpha)
        for lit in self.participated_in:
            self.reasoned_in[lit] = 0

    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals, sentence=None, assign_info=None):
        """Called after a learnt clause is generated from conflict analysis.
        :param sentence:
        :param assign_info:
        :param assign_info:
        """
        super().after_conflict_analysis(learnt_clause_literals, conflict_side_literals)
        U = set()
        for lit in learnt_clause_literals:
            idx = assign_info.assigned_idxs[-lit]
            ante = assign_info.antes[idx]
            if ante is not None:
                clause = sentence[ante]
                U.update(clause)
        U -= set(learnt_clause_literals)
        for lit in U:
            self.reasoned_in[lit] += 1

    def on_assign(self, literal):
        """Called when a literal is assigned or propagated.
        """
        super().on_assign(literal)
        self.reasoned_in[literal] = 0

    def on_unassign(self, literal):
        """Called when a literal is unassigned by backtracking or restart."""
        interval = self.learn_counter - self.assigned_at[literal]
        if interval > 0:
            reward = float(self.participated_in[literal]) / interval
            rsr = float(self.reasoned_in[literal]) / interval
            self.weights[literal] = self.alpha * (reward + rsr) + (1 - self.alpha) * self.weights[literal]

