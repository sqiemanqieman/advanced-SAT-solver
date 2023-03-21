from time import time


class NiVER:
    """Preprocess based on Non Increasing VER (NiVER)"""

    def __init__(self, sentence, num_vars, flag, ple=False):
        self.sentence = sentence
        self.num_vars = num_vars
        self.l2c_all, self.num_lit, self.valid_clause_index = self._init_watch()
        self.removed_clause = []    # clauses removed during preprocessing
        self.flag = flag    # degree of preprocess
        self.ple = ple  # pure literal eliminate or not
        self.time_for_preprocess = 0  # seconds used for preprocessing

    def preprocess(self):
        """The main part for preprocess with NiVER algorithm."""
        start_time = time()
        if self.ple:
            self.pure_literal_elimination()
        while True:
            entry = False
            for var in range(1, self.num_vars + 1):
                if len(self.l2c_all[var]) == 0 or len(self.l2c_all[-var]) == 0:
                    continue
                R_clause_set = []
                new_num_lit = 0
                old_num_lit = self.num_lit[var] + self.num_lit[-var]
                for P_idx in self.l2c_all[var]:
                    for N_idx in self.l2c_all[-var]:
                        resolvent = self.learn_resolvent(P_idx, N_idx, var)
                        if len(resolvent) == 0:
                            return None
                        if not self.judge_tautology(resolvent) and not self.judge_exist(resolvent):
                            new_num_lit += len(resolvent)
                            R_clause_set.append(resolvent)
                            if new_num_lit > old_num_lit:
                                break
                    if new_num_lit > old_num_lit:
                        break

                if old_num_lit >= new_num_lit:
                    self.removed_clause.append((var, self.clause_of_var(var)))
                    self.remove_c(var)
                    self.remove_c(-var)
                    current_idx = len(self.sentence)
                    for clause in R_clause_set:
                        self.valid_clause_index.add(current_idx)
                        self.sentence.append(clause)
                        for lit in clause:
                            self.l2c_all[lit].append(current_idx)
                            self.num_lit[lit] += len(clause)
                        current_idx += 1
                    if self.flag:
                        entry = True
            if not entry:
                break
        if self.ple:
            self.pure_literal_elimination()
        self.time_for_preprocess = time() - start_time
        return self.valid_sentence()

    def pure_literal_elimination(self):
        """Eliminate pure literals."""
        for var in range(1, self.num_vars + 1):
            if len(self.l2c_all[var]) == 0 and len(self.l2c_all[-var]) != 0:
                self.removed_clause.append((var, self.clause_of_var(var)))
                self.remove_c(-var)
            if len(self.l2c_all[-var]) == 0 and len(self.l2c_all[var]) != 0:
                self.removed_clause.append((var, self.clause_of_var(var)))
                self.remove_c(var)

    def _init_watch(self):
        """Initialize the l2c_all, num_lit and valid_clause_index."""
        l2c_all = {}    # literal -> clause
        num_lit = []    # literal -> number of literals
        valid_index = set()     # indexes of valid clauses
        for i in range(-self.num_vars, self.num_vars + 1):
            l2c_all[i] = []
            num_lit.append(0)
        for idx, clause in enumerate(self.sentence):
            valid_index.add(idx)
            for lit in clause:
                l2c_all[lit].append(idx)
                num_lit[lit] += len(clause)
        return l2c_all, num_lit, valid_index

    def learn_resolvent(self, P_idx, N_idx, var):
        """Eliminate the Variable numbered var, and return the resolvent."""
        P_clause = list(self.sentence[P_idx])
        N_clause = list(self.sentence[N_idx])
        P_clause.remove(var)
        N_clause.remove(-var)
        resolvent = list(set(P_clause + N_clause))
        return resolvent

    def judge_tautology(self, clause):
        """Determine whether a clause is a tautology."""
        for lit in clause:
            if -lit in clause:
                return True
        return False

    def judge_exist(self, clause):
        """Determine whether a clause has already existed in sentence."""
        existed_clause = []
        for lit in clause:
            for c_idx in self.l2c_all[lit]:
                c = set(self.sentence[c_idx])
                existed_clause.append(c)
        if set(clause) in existed_clause:
            return True
        else:
            return False

    def clause_of_var(self, var):
        """Return the list of the clauses that will be eliminated."""
        clause_list = []
        for c_idx in self.l2c_all[var]:
            clause_list.append(self.sentence[c_idx])
        for c_idx in self.l2c_all[-var]:
            clause_list.append(self.sentence[c_idx])
        return clause_list

    def remove_c(self, var):
        """Remove clauses including literal var from sentence."""
        tmp_idx_set = set(self.l2c_all[var])
        for c_idx in tmp_idx_set:
            self.valid_clause_index.remove(c_idx)
            clause = self.sentence[c_idx]
            for lit in clause:
                self.l2c_all[lit].remove(c_idx)
                self.num_lit[lit] -= len(clause)

    def valid_sentence(self):
        """Return the valid sentence."""
        final_sentence = []
        for idx in self.valid_clause_index:
            final_sentence.append(self.sentence[idx])
        return final_sentence

    def after_assignment(self, result):
        """Assign values to elements eliminated during preprocessing after assignment."""
        if result is None: return None
        res = set(result)
        for i in range(1, self.num_vars+1):
            if i not in res and -i not in res:
                res.add(i)

        while len(self.removed_clause) != 0:
            lit, clause_list = self.removed_clause.pop()
            for clause in clause_list:
                flag = True
                for l in clause:
                    if abs(l) != abs(lit) and l in res:
                        flag = False
                        break
                if flag:
                    for l in clause:
                        if abs(l) == abs(lit):
                            if lit in res:
                                res.remove(lit)
                            elif -lit in res:
                                res.remove(-lit)
                            res.add(l)
                            break
        return list(res)