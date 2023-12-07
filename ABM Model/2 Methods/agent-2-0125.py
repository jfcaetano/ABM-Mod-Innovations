from mesa import Agent
from belief import Belief, Mode
import pandas as pd

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


    def tick(self):
        """Increment clock by 1."""
        self.clock += 1
        self.beliefTime += 1

    def isSharing(self):
        """Check if agent is still sharing own belief."""
        return self.beliefTime <= self.shareTime

    def setBelief(self, belief):
        """Set agent's belief."""
        self.belief = belief
        self.beliefTime = 0

    def update(self, other):
        """Update agent's own beliefs"""

        # Convert self to Method_A belief
        if self.belief == Belief.Neutral and other.belief == Belief.Method_A:
            self.setBelief(Belief.Method_A)
            
                
        if self.belief == Belief.Neutral and other.belief == Belief.Method_B:
            self.setBelief(Belief.Method_B)

        # Convert self to Method_B belief
            
        if self.belief == Belief.Method_B and other.belief == Belief.Method_A and self.beliefTime > 20 and self.beliefTime < 200:
            self.setBelief(Belief.Method_A)
            
        if self.belief == Belief.Neutral and other.belief == Belief.Method_A and self.beliefTime > 20 and self.beliefTime < 200:
            self.setBelief(Belief.Method_A)

        if self.belief == Belief.Method_A and other.belief == Belief.Method_B  and self.beliefTime > 200:
            self.setBelief(Belief.Method_B)
            
        if self.belief == Belief.Neutral and other.belief == other.belief == Belief.Method_B and self.beliefTime > 200:
            self.setBelief(Belief.Method_B)
            

    def step(self, interlocutor):
        """Interact with interlocutor, updating own beliefs."""
        self.update(interlocutor)
