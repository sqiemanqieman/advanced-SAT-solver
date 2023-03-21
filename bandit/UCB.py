import numpy as np

from heuristics import VSIDS, ERWA, RSR, LRB, CHB


class UCB:
    def __init__(self, sentence, alpha, discount, batch):
        super().__init__()
        self.AllHeuristicsChoices = ["VSIDS", "ERWA", "RSR", "LRB", "CHB"]
        self.Heuristics = [VSIDS(sentence, discount), CHB(sentence, alpha), LRB(sentence, alpha, discount, batch),
                           ERWA(sentence, alpha), RSR(sentence, alpha)]
        self.num_arms = len(self.AllHeuristicsChoices)

        self.UCB_values = np.zeros(self.num_arms)
        self.UCB_mean_rewards = np.zeros(self.num_arms)
        self.num_pulls = np.zeros(self.num_arms)

        self.round = 1  # start from 1
        self.current_heuristic_index = 0
        self.num_pulls[0] += 1

    def update_UCB_values(self, ai):
        # update UCB_values[self.current_heuristic_index]
        arm = self.current_heuristic_index
        t = self.round

        # denote the number of decisions in this run
        num_decisions = ai.num_decisions
        # denote the number of variables fixed by branching
        num_decidedVars = len(ai.decided_idxs)
        if num_decidedVars == 0:
            return
        current_reward = np.log2(num_decisions) / num_decidedVars
        self.UCB_mean_rewards[arm] = ((self.num_pulls[arm] - 1) * self.UCB_mean_rewards[arm] + current_reward) / \
                                     self.num_pulls[arm]
        self.UCB_values[arm] = self.UCB_mean_rewards[arm] + np.sqrt(4 * np.log(t) / self.num_pulls[arm])

    def change_heuristic(self, ai):


        self.update_UCB_values(ai)
        self.round += 1
        if (self.round - 1) < len(self.AllHeuristicsChoices):
            # Stabilize the algorithm by exploring each arm once at the beginning
            self.current_heuristic_index = self.round - 1
        else:
            # select the largest
            self.current_heuristic_index = np.argmax(self.UCB_values)

        self.num_pulls[self.current_heuristic_index] += 1
        return self.Heuristics[self.current_heuristic_index]
