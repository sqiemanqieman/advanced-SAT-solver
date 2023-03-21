import numpy as np


class MLR:
    """Machine Learning-based Restart algorithm"""

    def __init__(self):
        self.α, self.ε, self.β1, self.β2 = 0.001, 1e-8, 0.9, 0.999
        self.conflicts, self.conflicts_since_last_restart = 0, 0
        self.t, self.μ, self.m2 = 0, 0, 0
        self.prev_lbd1, self.prev_lbd2, self.prev_lbd3 = 0, 0, 0
        self.θ, self.m, self.v = np.zeros(7), np.zeros(7), np.zeros(7)

    def after_conflict(self, learnt_clause_literals, assign_info=None):
        """Called after a learnt clause is generated from conflict analysis.
        :param sentence:
        :param assign_info:
        """
        self.conflicts += 1
        self.conflicts_since_last_restart += 1
        next_lbd = self._lbd(learnt_clause_literals, assign_info)
        δ = next_lbd - self.μ
        self.μ += δ / self.conflicts
        Δ = next_lbd - self.μ
        self.m2 += Δ * δ
        if self.conflicts > 3:
            self.t += 1
            features = self._feature_vec()
            predict = np.dot(self.θ, features)
            error = predict - next_lbd
            g = error * features
            self.m = self.β1 * self.m + (1 - self.β1) * g
            self.v = self.β2 * self.v + (1 - self.β2) * g * g
            m_hat = self.m / (1 - self.β1 ** self.t)
            v_hat = self.v / (1 - self.β2 ** self.t)
            self.θ -= self.α * m_hat / (v_hat ** 0.5 + self.ε)
        self.prev_lbd3, self.prev_lbd2, self.prev_lbd1 = self.prev_lbd2, self.prev_lbd1, next_lbd

    def after_bcp(self, conflict_ante):
        """Called after a conflict is detected during BCP
        :param conflict_ante:"""
        need_restart = False
        if not conflict_ante and self.conflicts > 3 and self.conflicts_since_last_restart > 0:
            sigma = (self.m2 / (self.conflicts - 1)) ** 0.5
            features = self._feature_vec()
            if np.dot(self.θ, features) > self.μ + 3.08 * sigma:
                self.conflicts_since_last_restart = 0
                need_restart = True
        return need_restart

    def _lbd(self, clause, assign_info):
        """Calculate the LBD of a clause"""
        mi, ma = float("inf"), 0
        for lit in clause:
            level = assign_info.level(-lit)
            mi = min(mi, level)
            ma = max(ma, level)
        return ma - mi + 1

    def _feature_vec(self):
        return np.array([1, self.prev_lbd1, self.prev_lbd2, self.prev_lbd3,
                         self.prev_lbd1 * self.prev_lbd2, self.prev_lbd1 * self.prev_lbd3,
                         self.prev_lbd2 * self.prev_lbd3])

