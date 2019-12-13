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
otrovi = sve_kombinacije[:len(sve_kombinacije)//2]
hrana = sve_kombinacije[len(sve_kombinacije)//2:]
assert(len(otrovi)==len(hrana))
assert(len(sve_kombinacije)==64)



class HungryAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.energy = 0
        self.svet = {"boje":set(),"oblici":set(),"ukusi":set()}
        self.boja = "black"
        self.size = 0.2
        self.procedural =dict()
        self.pojedeni_otrovi=0
        self.pojedena_hrana=0
        
    def move(self):
        self.energy=-1
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)
        
    def store_info(self,food):
        self.svet["boje"].add(food.boja)
        self.svet["oblici"].add(food.oblik)
        self.svet["ukusi"].add(food.ukus)

        
    def eat_or_not(self,food):
        #boja,ukus,oblik
        eat = None
        property_tuple=(food.boja,food.ukus,food.oblik)
        try:
            #remember
            eat = self.procedural[property_tuple] #posto je True false
        except KeyError:
            #barf, scrape_memory
            assert(eat is None)
            food_count, poison_count = 0,0
            for atribut in property_tuple:
                # za svaki atribut cemo skrejpovati memoriju, u svim mogucim kombincijama(mozda da napravim poseban dict, koji broji koliko puta je koji false, koliko puta je koji True. svakako bi se brojevima svasta resilo,takodje i stepni otrova, direkno ih mogu sabirati umesto svih ifova.)
                for key in self.procedural:
                    if atribut in key:
                        #ako smo nasli atribut u proceduralnoj, onda gledamo kakvi su bili ishodi
                        if not self.procedural[key]:
                            poison_count+=1
                        elif self.procedural[key]:
                            food_count+=1
                        else:
                            assert(False)
            print (food_count,poison_count)
            if food_count>poison_count:
                eat=True
            elif food_count<poison_count:
                eat=False
            else:
                eat = True #self.random.choice([True,False])
                
            if eat:
                if property_tuple in otrovi:
                    self.energy-=2
                    self.pojedeni_otrovi=+1
                    self.procedural[property_tuple] = False
                if property_tuple in hrana:
                    self.pojedena_hrana+=1
                    self.energy+=5
                    self.procedural[property_tuple] = True
                
               
        
        
    def explore(self):
        """Ide negde i gleda na sta je nagazio"""
        foods = [f for f in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(f,FoodAgent)]
        for food in foods:
            self.store_info(food)
            self.eat_or_not(food)
            
        

    def step(self):
       # print (self.unique_id)
       # print("Imam:%s dinara" %self.wealth)
        self.move()
        self.explore()
        #moze da komunicira sa okruzenjem i da saznaje o drugim bicima
        
def izdvoji_agente(model):
    return [a for a in model.schedule.agents if isinstance(a,HungryAgent)]

def compute_knowledge(model):
    """Ukupno znanje svih HungryAgenata"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in  agents:
        for key,value in agent.svet.items():
            assert(len(value)<=4)
            ukupno+=len(value)
    return ukupno

def total_pojedeni_otrovi(model):
    """Vraca broj ukupnih pojedenih otrova"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.pojedeni_otrovi
    return ukupno

def total_pojedena_hrana(model):
    """Vraca broj ukupnih pojedenih otrova"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.pojedena_hrana
    return ukupno

def measure_experience(model):
    """Ukupno iskustvo"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=len(agent.procedural.keys())
    return ukupno

def total_energy(model):
    """Meri energiju svih agenata"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.energy
        
    return ukupno
        
    
class HungerModel(Model):
    """A model with some number of agents."""
    def __init__(self,N,width,height,num_of_food=64):
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
        model_reporters = {"TotalKnowledge":compute_knowledge,"TotalEnergy":total_energy,"TotalExperience":measure_experience,"TotalFood":total_pojedena_hrana,"TotalPoison":total_pojedeni_otrovi})
  #      agent_reporters = {"Knowledge":"knowledge"})
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
