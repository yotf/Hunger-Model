from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

def compute_gine(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)


class MoneyAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.wealth = 1
        
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)
    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates)>1:
            other=self.random.choice(cellmates)
            self.wealth-=1
            other.wealth+=1


        
    def step(self):
       # print (self.unique_id)
       # print("Imam:%s dinara" %self.wealth)
        self.move()
        if self.wealth>0:
            self.give_money()
        #moze da komunicira sa okruzenjem i da saznaje o drugim bicima
        
        
class MoneyModel(Model):
    """A model with some number of agents."""
    def __init__(self,N,width,height):
        self.num_agents = N
        self.grid = MultiGrid(width,height,True)
        self.schedule= RandomActivation(self)
        self.running = True
        for i in range(self.num_agents):
            a = MoneyAgent(i,self)
            self.schedule.add(a)
            
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
            
        self.datacollector = DataCollector(
        model_reporters = {"Gini":compute_gine}, #prosledice automacki
        agent_reporters = {"Wealth":"wealth"})
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
