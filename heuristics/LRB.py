from .RSR import RSR


class LRB(RSR):
    """The learning rate branching(LRB) algorithm.
    It extends RSR algorithm by considering the locality."""
    def __init__(self, sentence, alpha=0.4, discount=0.95, batch=10):
        super().__init__(sentence, alpha)
        self.discount = discount
        self.batch = batch
        self.counter = 0
        self.recorder = {}

    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals, sentence=None, assign_info=None):
        """Called after a learnt clause is generated from conflict analysis."""
        super().after_conflict_analysis(learnt_clause_literals, conflict_side_literals, sentence, assign_info)
        for lit in learnt_clause_literals:
            self.recorder[lit] = self.recorder.get(lit, 0) + 1
        self.counter += 1
        if self.counter % self.batch == 0:
            self._reorder()

    def _reorder(self):
        for lit in self.weights:
            self.weights[lit] = self.weights[lit] * self.discount ** (self.batch - self.recorder.get(lit, 0))
        self.ema = dict(sorted(self.weights.items(), key=lambda i: i[1]))
        self.recorder = {}
