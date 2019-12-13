from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.batchrunner import BatchRunner
import matplotlib.pyplot as plt
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import itertools

class FoodAgent(Agent):
    def __init__(self,unique_id,model,boja,ukus,oblik):
        super().__init__(unique_id,model)
        self.boja = boja
        self.oblik = oblik
        self.ukus = ukus
        self.size = 0.5
    def step(self):
        pass

#ako imamo 10X10 tablu, imamo ukupno 64 kombinacije
boje = ["red","yellow","green","blue"]
ukusi = ["kiselo","ljuto","gorko","slatko"]
oblici = ["zvezda","kvadrat","krug","trougao"]
sve_kombinacije = list(itertools.product(boje,ukusi,oblici))
assert(len(sve_kombinacije)==64)



class HungryAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        #self.energy = 0
        self.knowledge = 0
        self.svet = {"boje":set(),"oblici":set(),"ukusi":set()}
        self.boja = "black"
        self.size = 0.2
        #self.wealth = 1
        #self.dlakav = dlakav
        
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)
        
    def store_info(self,food):
        self.svet["boje"].add(food.boja)
        self.svet["oblici"].add(food.oblik)
        self.svet["ukusi"].add(food.ukus)
        k = 0
        for key,value in self.svet.items():
            assert(len(value)<=4)
            k+=len(value)
        self.knowledge = k

        
        
        
    def explore(self):
        """Ide negde i gleda na sta je nagazio"""
        foods = [f for f in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(f,FoodAgent)]
        for food in foods:
            self.store_info(food)

    def step(self):
       # print (self.unique_id)
       # print("Imam:%s dinara" %self.wealth)
        self.move()
        self.explore()
        #moze da komunicira sa okruzenjem i da saznaje o drugim bicima
        

def compute_knowledge(model):
    """Ukupno znanje svih HungryAgenata"""
    agenti = model.schedule.agents
    ukupno = 0
    for agent in  [a for a  in agenti if isinstance(a,HungryAgent)]:
        ukupno+=agent.knowledge
    return ukupno
    
        
    
class HungerModel(Model):
    """A model with some number of agents."""
    def __init__(self,N,width,height,num_of_food=10):
        self.num_agents = N
        self.num_food = num_of_food
        self.grid = MultiGrid(width,height,True)
        self.schedule= RandomActivation(self)
        self.running = True
        for i in range(self.num_agents):
            a = HungryAgent(i,self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
            
        for i in range(self.num_food):
            kombinacija = sve_kombinacije[i]
            id_offset = i+1000
            f = FoodAgent(id_offset,self, kombinacija[0],kombinacija[1],kombinacija[2])
            self.schedule.add(f)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(f,(x,y))
            
            
        self.datacollector = DataCollector(
        model_reporters = {"TotalKnowledge":compute_knowledge}) #prosledice automacki
  #      agent_reporters = {"Knowledge":"knowledge"})
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
