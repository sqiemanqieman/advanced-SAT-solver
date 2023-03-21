from .heuristics import Heuristic


class CHB(Heuristic):
    """The conflict history-based branching heuristic (CHB)"""
    def __init__(self, sentence, alpha):
        super().__init__()
        self.alpha = alpha
        self.num_conflicts = 0
        self.plays = set()
        self.last_conflict = {}
        for clause in sentence:
            for literal in clause:
                self.weights[literal] = 0
                self.last_conflict[literal] = 0

    def after_bcp(self, conflict_ante):
        multiplier = 1.0 if conflict_ante else 0.9
        for lit in self.plays:
            reward = multiplier / (self.num_conflicts - self.last_conflict[lit] + 1)
            self.weights[lit] = (1 - self.alpha) * self.weights[lit] + self.alpha * reward
        self.update_weights(self.plays)

    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals, sentence=None, assign_info=None):
        self.num_conflicts += 1
        self.alpha = max(0.06, self.alpha - 1e-6)
        for literal in learnt_clause_literals:
            self.last_conflict[literal] = self.num_conflicts
        for literal in conflict_side_literals:
            self.last_conflict[literal] = self.num_conflicts
        self.plays = {learnt_clause_literals[0]}

    def on_assign(self, literal):
        """Called when a literal is assigned or propagated.
        :param literal:
        """
        self.plays.add(literal)

    def decide(self, assigned):
        """decide which literal to be assigned next"""
        lit = super().decide(assigned)
        self.plays = {lit}
        return lit
