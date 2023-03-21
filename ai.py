"""Implementation of the assignment information data structure."""


class AssignInfo:
    """
    A struct used for recording the assignment information
    """
    def __init__(self):
        self.assignments = []
        self.antes = []
        self.decided_idxs = []
        self.assigned = set()
        self.assigned_idxs = {}
        self.num_decisions = 0

    def on_assign(self, lit, ante):
        self.assignments.append(lit)
        self.antes.append(ante)
        self.assigned_idxs.update({lit: len(self.assigned)})
        self.assigned.add(lit)

    def analyse_conflict(self, sentence, conflict_ante):
        """Analyze the conflict with first-UIP clause learning.
        Resolve conflict clause with its last assigned literal's ante-clause until only one literal having the highest
        level in conflict clause.
        Learned clause returned should be in decreasing order of the assignment, which means the latest assigned literal
        is in the head. This will facilitate the later call of add_learned_clause(...)"""
        backtrack_level, learned_clause, conflict_side_literals = None, [], []
        if self._conflict_clause_level_is_0(conflict_ante):
            return -1, learned_clause, conflict_side_literals
        # get the highest level's assignments
        ass = dict([(self.assignments[i], self.antes[i]) for i in
                    range(len(self.assigned) - 1, self.decided_idxs[-1] - 1, -1)])
        conflict_ante = set(conflict_ante)  # use set to accelerate
        highest_level_literals = [-literal for literal in ass if -literal in conflict_ante]
        while len(highest_level_literals) > 1:
            conflict_side_literals.append(highest_level_literals[0])
            conflict_ante = self._resolve(conflict_ante, sentence[ass[-highest_level_literals[0]]])
            highest_level_literals = [-literal for literal in ass if -literal in conflict_ante]
        if len(highest_level_literals) == 1:
            learned_clause = sorted(conflict_ante, key=lambda key: self.level(-key), reverse=True)
            backtrack_level = 0 if len(learned_clause) == 1 else self.level(-learned_clause[1])
        return backtrack_level, learned_clause, conflict_side_literals

    def backtrack(self, level):
        """backtrack to the level"""
        unassigned_literals = self.assignments[self.decided_idxs[level]:]
        self.assignments = self.assignments[:self.decided_idxs[level]]
        self.antes = self.antes[:self.decided_idxs[level]]
        for literal in unassigned_literals:
            self.assigned_idxs.pop(literal)
            self.assigned.remove(literal)
        self.decided_idxs = self.decided_idxs[:level]
        return unassigned_literals

    def level(self, literal):
        """compute level of an assigned literal"""
        index = self.assigned_idxs[literal]
        for i in range(len(self.decided_idxs)):
            if index < self.decided_idxs[i]:
                return i
        return len(self.decided_idxs)

    def clear(self):
        self.assignments = []
        self.antes = []
        self.decided_idxs = []
        self.assigned = set()
        self.assigned_idxs = {}
        self.num_decisions = 0

    def _resolve(self, clause1, clause2):
        """resolve two clause, one is conflict clause, another is unit clause, the result is conflict clause"""
        clause1.update(clause2)
        clause = set([l for l in clause1 if -l not in clause1])
        return clause

    def _conflict_clause_level_is_0(self, clause):
        """compute the level of a conflict clause --- the highest level of all literals' negations in clause"""
        return all([self.level(-literal) == 0 for literal in clause])


