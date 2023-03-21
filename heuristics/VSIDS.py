from bisect import insort
from .heuristics import Heuristic


class VSIDS(Heuristic):
    """
    The variable state independent decaying sum(VSIDS) alogrithm.
    :field decay: the multiplicative decay factor
    :field vsids_scores: the state scores of each literal
    """
    def __init__(self, sentence, decay=0.95):
        super().__init__()
        self.decay = decay
        # scores = {}
        for clause in sentence:
            for literal in clause:
                self.weights[literal] = self.weights.get(literal, 0) + 1

    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals, sentence=None, assign_info=None):
        """Called after a learnt clause is generated from conflict analysis.
        :param sentence:
        :param assign_info:
        """
        self.update_weights(learnt_clause_literals)

    def update_weights(self, learned_clause):
        """Update VSIDS scores.
        note that the sorting order should be maintained"""
        increased = []
        for lit in learned_clause:
            increased.append((lit, (self.weights.pop(lit) + 1) * self.decay))
        scores = [(i[0], i[1] * self.decay) for i in self.weights.items()]
        for i in increased:
            # use binary insert method for accelerating the operation of maintaining order
            insort(scores, i, key=lambda key: key[1])
        self.weights.clear()
        self.weights.update(scores)
