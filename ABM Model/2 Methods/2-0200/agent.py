import pandas as pd
from mesa import Agent
from belief import Belief, Mode

# Load thresholds from CSV
csv_file = 'Highest_PR_Method_80-2P.csv'
df = pd.read_csv(csv_file)

# Extract thresholds from the DataFrame
def get_threshold(df, choice):
    value = df.loc[df['Choice'] == choice, 'Time']
    return value.iloc[0]

NEUTRAL_TO_METHOD_A_THRESHOLD = get_threshold(df, 'A')
METHOD_A_TO_METHOD_B_THRESHOLD = get_threshold(df, 'B')

class PopAgent(Agent):
    """An Agent with some initial knowledge."""

    def __init__(self, unique_id, model, neighbors, sharetime):
        super().__init__(unique_id, model)

        # Default params
        self.belief = Belief.Neutral
        self.neighbors = neighbors  # list of agent's neighbours
        self.clock = 0  # internal timer (absolute time)
        self.beliefTime = 0  # time current belief has been held
        self.shareTime = sharetime   # time limit within which new beliefs are shared
        self.belief_transitions = []  # track belief transitions

    def tick(self):
        """Increment clock by 1."""
        self.clock += 1
        self.beliefTime += 1

    def isSharing(self):
        """Check if agent is still sharing own belief."""
        return self.beliefTime <= self.shareTime

    def setBelief(self, belief):
        """Set agent's belief and log the transition."""
        if self.belief != belief:
            transition = (self.clock, self.belief, belief)
            self.belief_transitions.append(transition)
        self.belief = belief
        self.beliefTime = 0

    def update(self, other):
        """Update agent's own beliefs"""
        if self.belief == Belief.Neutral and other.belief == Belief.Method_A:
            self.setBelief(Belief.Method_A)
        if self.belief == Belief.Neutral and other.belief == Belief.Method_B:
            self.setBelief(Belief.Method_B)




        if self.belief == Belief.Method_B and other.belief == Belief.Method_A and NEUTRAL_TO_METHOD_A_THRESHOLD < self.beliefTime <= METHOD_A_TO_METHOD_B_THRESHOLD:
            self.setBelief(Belief.Method_A)
        if self.belief == Belief.Neutral and other.belief == Belief.Method_A and NEUTRAL_TO_METHOD_A_THRESHOLD < self.beliefTime <= METHOD_A_TO_METHOD_B_THRESHOLD:
            self.setBelief(Belief.Method_A)
            
        if self.belief == Belief.Method_A and other.belief == Belief.Method_B and self.beliefTime > METHOD_A_TO_METHOD_B_THRESHOLD:
            self.setBelief(Belief.Method_B)
        if self.belief == Belief.Neutral and other.belief == Belief.Method_B and self.beliefTime > METHOD_A_TO_METHOD_B_THRESHOLD:
            self.setBelief(Belief.Method_B)
            


    def step(self, interlocutor):
        """Interact with interlocutor, updating own beliefs."""
        self.update(interlocutor)

# Sample usage
if __name__ == "__main__":
    # Create a model and agents here for testing
    pass
