import numpy as np
import random

class KnowledgeTracer:
    def __init__(self):
        # BKT Parameters: P(initial), P(learn), P(guess), P(slip)
        self.skills = {
            "counting": {"p_know": 0.3, "p_learn": 0.1, "p_guess": 0.2, "p_slip": 0.1},
            "addition": {"p_know": 0.2, "p_learn": 0.05, "p_guess": 0.2, "p_slip": 0.1},
            "subtraction": {"p_know": 0.1, "p_learn": 0.05, "p_guess": 0.2, "p_slip": 0.1}
        }

    def update(self, skill, is_correct):
        """Updates the probability of mastery based on the child's response."""
        s = self.skills.get(skill, self.skills["counting"])
        pk = s["p_know"]
        
        if is_correct:
            # Likelihood of knowing given a correct answer
            p_know_given_obs = (pk * (1 - s["p_slip"])) / (pk * (1 - s["p_slip"]) + (1 - pk) * s["p_guess"])
        else:
            # Likelihood of knowing given an incorrect answer
            p_know_given_obs = (pk * s["p_slip"]) / (pk * s["p_slip"] + (1 - pk) * (1 - s["p_guess"]))
        
        # Transition to learned state
        new_pk = p_know_given_obs + (1 - p_know_given_obs) * s["p_learn"]
        self.skills[skill]["p_know"] = np.clip(new_pk, 0, 1)
        return self.skills[skill]["p_know"]

    def get_next_difficulty(self, skill):
        """Returns recommended difficulty (1-10) based on mastery."""
        pk = self.skills.get(skill, {"p_know": 0})["p_know"]
        if pk < 0.3: return random.randint(1, 3)
        if pk < 0.7: return random.randint(4, 7)
        return random.randint(8, 10)