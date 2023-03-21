from time import time

from heuristics import init_heuristic
from restart import init_restart_policy
from bandit import init_bandit
from ai import AssignInfo
from preprocess import init_preprocess_policy


class CDCL:
    """The conflict driven clause learning algorithm(`CDCL`) for `SAT` solver."""

    def __init__(self, sentence, num_vars, assignment_algorithm, alpha, discount, batch, rp=None, bandit=None, pp=None):
        """To simplify the use of data structures, `sentence` is a list of lists where each list
        is a clause. Each clause is a list of literals, where a literal is a signed integer.
        `assignment` is also a list of literals in the order of their assignment.
        """
        # Initialize data structures.
        self.preprocessor = init_preprocess_policy(pp, sentence, num_vars)
        self.sentence = self.preprocessor.preprocess() if self.preprocessor is not None else sentence
        self.num_vars = num_vars
        self.c2l_watch, self.l2c_watch = self._init_watch()
        self.ai = AssignInfo()  # assignment information
        self.bandit = init_bandit(self.sentence, alpha, discount, batch, bandit)
        self.assignment_algorithm = assignment_algorithm
        self.rp = init_restart_policy(rp)  # restart policy
        self.heuristic = init_heuristic(assignment_algorithm, self.sentence, alpha, discount, batch) \
            if self.bandit is None else self.bandit.Heuristics[0]  # heuristic algorithm

    def solve(self):
        """Solve the CNF sentence, which is the only interface for users."""
        preprocess_time = self.preprocessor.time_for_preprocess if self.preprocessor is not None else 0
        if self.sentence is None:
            return None, preprocess_time, 0
        solve_time = time()
        solution = self._calculate()
        while solution == 'restart':  # only when specified restart policy, may solution be 'restart'
            solution = self._restart()
        solve_time = time() - solve_time
        solution = solution if self.preprocessor is None else self.preprocessor.after_assignment(solution)
        return solution, preprocess_time, solve_time

    def _calculate(self):
        """The main calculation part for CDCL algorithm."""
        conflict_ante = self._bcp()
        if conflict_ante: return None  # indicate UNSAT
        need_restart = self._after_bcp(conflict_ante)
        if need_restart: return 'restart'
        while len(self.ai.assigned) < self.num_vars:  # Main loop.
            assigned_lit = self.heuristic.decide(self.ai.assigned)
            self.ai.num_decisions += 1  # count the number of decisions
            if not assigned_lit: return self.ai.assignments  # all assigned(found a solution), return solution
            self._handle_assign(assigned_lit, None, True)
            conflict_ante = self._bcp()
            need_restart = self._after_bcp(conflict_ante)
            if need_restart: return 'restart'
            while conflict_ante:  # conflict occurs, learn conflict.
                backtrack_level, learnt_clause, conflict_side_literals = self._analyze_conflict(conflict_ante)
                if backtrack_level < 0: return None
                self._after_conflict_analysis(learnt_clause, conflict_side_literals)
                self._backtrack(backtrack_level)
                conflict_ante = self._bcp(True)
                need_restart = self._after_bcp(conflict_ante)
                if need_restart: return 'restart'
        return self.ai.assignments  # indicate SAT

    def _restart(self):
        """Restart the solver"""
        if self.bandit is not None:
            self.heuristic = self.bandit.change_heuristic(self.ai)
        self.ai.clear()
        self.c2l_watch, self.l2c_watch = self._init_watch()
        return self._calculate()

    def _bcp(self, is_backtrack=False):
        """Boolean constraint propagation with 2 watched literals per clause."""
        i = len(self.ai.assigned) - 1
        if is_backtrack:
            i += 1
            self._handle_backtrack()
        if not self.ai.assigned:  # first time to run bcp
            i = 0
            conflict_clause = self._handle_first_time_to_run()
            if conflict_clause: return conflict_clause
        while i < len(self.ai.assigned):  # iterate all new assignments
            handle_lit = -self.ai.assignments[i]
            watch_clauses, idx = self.l2c_watch.get(handle_lit, []), 0
            while idx < len(watch_clauses):  # iterate all clause
                clause_idx = watch_clauses[idx]
                l0, l1 = self.c2l_watch[clause_idx]
                satisfied = self._check_satisfied(l0, l1)
                if satisfied:
                    idx += 1
                    continue
                propagated, is_unit_or_conflict = self._propagate_watch_on_clause(handle_lit, clause_idx)
                if not propagated: idx += 1
                if is_unit_or_conflict:
                    conflict_clause = self._handle_unit_or_conflict(clause_idx, l0, l1, handle_lit)
                    if conflict_clause: return conflict_clause
            i += 1
        return None  # indicate no conflict; other return the antecedent of the conflict

    def _after_conflict_analysis(self, learnt_clause, conflict_side_literals):
        """After conflict analysis, maintain relevant data structure"""
        self._add_learned_clause(learnt_clause)
        self.heuristic.after_conflict_analysis(learnt_clause, conflict_side_literals, self.sentence, self.ai)
        if self.rp:
            self.rp.after_conflict(learnt_clause, self.ai)

    def _after_bcp(self, conflict_ante):
        """After bcp, maintain relevant data structure"""
        self.heuristic.after_bcp(conflict_ante)
        if self.rp:
            return self.rp.after_bcp(conflict_ante)

    def _handle_assign(self, lit, ante=None, is_decide=False):
        """Assign a literal. maintain relevant data structure
        """
        if is_decide:
            self.ai.decided_idxs.append(len(self.ai.assigned))
        self.ai.on_assign(lit, ante)
        self.heuristic.on_assign(lit)

    def _init_watch(self):
        """Initialize the watched literal data structure."""
        c2l_watch, l2c_watch = {}, {}  # c2l_watch: clause to literal watch, l2c_watch: literal to clause watch
        for i in range(len(self.sentence)):
            c2l_watch[i] = [self.sentence[i][0]]
            l2c_watch[self.sentence[i][0]] = l2c_watch.get(self.sentence[i][0], []) + [i]
            if len(self.sentence[i]) > 1:
                c2l_watch[i].append(self.sentence[i][1])
                l2c_watch[self.sentence[i][1]] = l2c_watch.get(self.sentence[i][1], []) + [i]
        return c2l_watch, l2c_watch

    def _propagate_watch_on_clause(self, lit, clause_idx):
        """propagate watching literal on a clause(sentence[clause_idx]).
        try to find a new literal to replace currently watching literal(lit)"""
        propagated, is_unit_or_conflict = False, True
        for literal in self.sentence[clause_idx]:  # o.s. checking for all literal in clause
            # if having satisfied literal, check next clause
            if literal in self.ai.assigned:
                is_unit_or_conflict = False
                break
            # if having any literal whose negation unassigned, adjust watching literals for this clause,
            # o.w., this clause is unit or conflict
            if literal not in self.c2l_watch[clause_idx] and -literal not in self.ai.assigned:
                self._change_watch_to(clause_idx, lit, literal)
                is_unit_or_conflict = False
                propagated = True
                break
        return propagated, is_unit_or_conflict

    def _change_watch_to(self, clause_idx, old_lit, new_lit):
        """change watching literal from old_lit to new_lit on clause(sentence[clause_idx])"""
        self.c2l_watch[clause_idx].remove(old_lit)
        self.l2c_watch[old_lit].remove(clause_idx)
        self.c2l_watch[clause_idx].append(new_lit)
        self.l2c_watch[new_lit] = self.l2c_watch.get(new_lit, []) + [clause_idx]

    def _check_satisfied(self, l0, l1):
        """check if clause already sat or already has two validate literals watching"""
        satisfied = False
        if any([l0 in self.ai.assigned, l1 in self.ai.assigned]) or all(
                [-l0 not in self.ai.assigned, -l1 not in self.ai.assigned]):
            satisfied = True
        return satisfied

    def _handle_backtrack(self):
        """when the bcp is rerun after a conflict backtracking, add the newly learned unit clause's literal
        to the assignment
        """
        self._handle_assign(self.c2l_watch[len(self.sentence) - 1][0], len(self.sentence) - 1)

    def _handle_first_time_to_run(self):
        """handle run bcp for the first time, handle all clauses with only 1 literal"""
        for clause_idx, literals in self.c2l_watch.items():
            if len(literals) == 1:  # unit clause
                if -literals[0] in self.ai.assigned:
                    return list(self.sentence[clause_idx])
                if literals[0] not in self.ai.assigned:
                    self._handle_assign(literals[0], clause_idx)
        return None

    def _handle_unit_or_conflict(self, clause_idx, l0, l1, handle_lit):
        """handle unit clause or conflict clause"""
        another = l0 if l0 != handle_lit else l1
        if -another in self.ai.assigned:  # conflicted clause
            return list(self.sentence[clause_idx])
        self._handle_assign(another, clause_idx)
        return None

    def _analyze_conflict(self, conflict_ante):
        """analyze conflict clause and return the learned clause"""
        return self.ai.analyse_conflict(self.sentence, conflict_ante)

    def _backtrack(self, level):
        """Backtrack by deleting assigned variables.
        keep all assigned literals with level <= backtrack_level"""
        unassigned_lits = self.ai.backtrack(level)
        for lit in unassigned_lits:
            self.heuristic.on_unassign(lit)
        self.heuristic.update_weights(unassigned_lits)

    def _add_learned_clause(self, learned_clause):
        """Add learned clause to the sentence and update watch.
        learned_clause is unit and in decreasing order of assignment. We choose to watch the first literal which
        is the only one satisfiable. This can promise least check of this clause for later rerun `bcp(...)` """
        i = len(self.sentence)
        self.sentence.append(learned_clause)
        lit = learned_clause[0]
        self.c2l_watch[i] = [lit]
        self.l2c_watch.update({lit: self.l2c_watch.get(lit, []) + [i]})
        if len(learned_clause) > 1:
            lit = learned_clause[1]
            self.c2l_watch[i].append(lit)
            self.l2c_watch.update({lit: self.l2c_watch.get(lit, []) + [i]})
