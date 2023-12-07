from mesa import Model
from agent import PopAgent, Belief
from simpleScheduler import SimpleActivation
import random


class KnowledgeModel(Model):
    """A model with some number of agents."""

    def __init__(self, network, sharingMode, sharetime, delay, singleSource=False, samePartition=True):
        self.mode = sharingMode
        self.G = network
        self.num_agents = self.G.number_of_nodes()
        self.schedule = SimpleActivation(self)
        self.delay = delay
        self.singleSource = singleSource
        self.samePartition = samePartition

        # Create agents
        for i in range(self.num_agents):
            neighbors = list(self.G.neighbors(i))
            a = PopAgent(unique_id=i, model=self, neighbors=neighbors, sharetime=sharetime)

            if i == 0:
                # Give Agent 0 Method_A information
                a.belief = Belief.Method_A
                self.agentZero = a
            if (i == 1) and (self.delay == 0) and self.samePartition is None and self.singleSource:
                # Give Agent 1 true information
                a.belief = Belief.Method_B
            if (i == 2) and (self.delay == 0) and self.samePartition is None and self.singleSource:
                # Give Agent 2 Method_C information
                a.belief = Belief.Method_C
                
            self.schedule.add(a)

        if (self.delay == 0) and (self.samePartition is not None or not self.singleSource):
            self.addMethod_B()
            
        if (self.delay == 0) and (self.samePartition is not None or not self.singleSource):
            self.addMethod_C()

    def addMethod_B(self):
        """Add Method_B belief to random agent."""
        if self.singleSource:
            a = self.agentZero
        elif self.samePartition is None:
            a = random.choice(self.schedule.agents)
        elif 'partition' in self.G.graph.keys() and self.samePartition:
            if (self.delay == 0):
                num = random.choice(list(self.G.graph['partition'][0])[1:])  # retraction source != Method_A source
            else:
                num = random.choice(list(self.G.graph['partition'][0]))
            a = self.schedule.agents[num]
        elif 'partition' in self.G.graph.keys() and not self.samePartition:
            num = random.choice(list(self.G.graph['partition'][1]))
            a = self.schedule.agents[num]
        else:
            a = random.choice(self.schedule.agents)
        a.setBelief(Belief.Method_B)
        
        
    def addMethod_C(self):
        """Add Method_C belief to random agent."""
        if self.singleSource:
            a = self.agentZero
        elif self.samePartition is None:
            a = random.choice(self.schedule.agents)
        elif 'partition' in self.G.graph.keys() and self.samePartition:
            if (self.delay == 0):
                num = random.choice(list(self.G.graph['partition'][0])[1:])  # retraction source != Method_A source
            else:
                num = random.choice(list(self.G.graph['partition'][0]))
            a = self.schedule.agents[num]
        elif 'partition' in self.G.graph.keys() and not self.samePartition:
            num = random.choice(list(self.G.graph['partition'][1]))
            a = self.schedule.agents[num]
        else:
            a = random.choice(self.schedule.agents)
        a.setBelief(Belief.Method_C)

    def step(self):
        """Advance the model by one step."""
        if (self.delay > 0) and (self.schedule.time == self.delay):
            self.addMethod_B()

        self.schedule.step()

    def logs(self):
        """Get agents' belief, interaction and pair history, respectively."""
        return self.schedule.logs()
