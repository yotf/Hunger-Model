from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.batchrunner import BatchRunner
import matplotlib.pyplot as plt
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import itertools
from collections import deque
from itertools import starmap,product
import collections
from datatypes import *


class FoodAgent(Agent):
    def __init__(self,unique_id,model,boja,ukus,oblik):
        super().__init__(unique_id,model)
        self.boja = boja
        self.oblik = oblik
        self.ukus = ukus
        self.size = 0.5
    def step(self):
        pass


class HungryAgent(Agent):
    def __init__(self,unique_id,model,memory_size,br_stepena_otrovnosti,walk_energy):
        super().__init__(unique_id,model)
        self.energy = 0

        assert(walk_energy>=0)
        self.walk_energy=walk_energy
        self.svet = {"boje":set(),"oblici":set(),"ukusi":set()}
        self.boja = "black"
        self.size = 0.2
        self.memory_size=memory_size
        self.procedural =MemoryDeque([],maxlen=memory_size)
        self.pojedeni_otrovi=0
        self.pojedena_hrana=0

        self.insertion_dict = self.make_insertion_dict(
            br_stepena_otrovnosti= br_stepena_otrovnosti,
            memory_size=memory_size
        )
        
    def move(self):
        """The agents will move in a random direction and lose specified energy"""
        self.energy-=self.walk_energy
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)
        
    def store_info(self,food):
        self.svet["boje"].add(food.boja)
        self.svet["oblici"].add(food.oblik)
        self.svet["ukusi"].add(food.ukus)
        
    def make_insertion_dict(self,br_stepena_otrovnosti,memory_size):
        vel_podeoka = memory_size//br_stepena_otrovnosti
        poz = dict()
        pozicija = 0

        for i in range(-(br_stepena_otrovnosti//2),0):
            poz[i]=pozicija
            pozicija+=vel_podeoka
            poz[-i]=pozicija
            pozicija+=vel_podeoka
        return poz


    def scrape_memory(self,property_tuple):
        """Gleda da li je se bilo koja od atributa
                u tuplu atributa nalazi u proceduralnoj memoriji"""
        hranljivost=0
        for atribut in property_tuple:
            for ktuple in self.procedural:
                if atribut in ktuple.kombinacija:
                    hranljivost+=ktuple.hranljivost
        # print ("HRANLJIVOST: %s" %hranljivost)
        return hranljivost 

    def decide_eat(self,property_tuple):
        """Odlucuje da li ce pojesti objekat"""
        eat = None
        rezultat = self.procedural.search_memory(property_tuple)
        if rezultat:
            eat = False if rezultat.hranljivost<0 else True
#            print ("Nadjena hranljivost je " + str(rezultat.hranljivost))
        else:
            assert(eat is None)
            pretp_hranljivost = self.scrape_memory(property_tuple)
#            print ("Pretpostavljena hranljivost je " + str(pretp_hranljivost))
            eat = True if pretp_hranljivost>=0 else False
        return eat


        
    def eat_or_not(self,food):
        """Pojede ili preskoci objekat koji je nasao"""

        property_tuple=KombinacijaTuple(boja=food.boja,ukus=food.ukus,oblik=food.oblik)
        eat = self.decide_eat(property_tuple)
        if eat:
            hranljivost=self.model.food_dict[property_tuple]
            self.store_in_memory(hranljivost,property_tuple)
            self.energy+=self.model.food_dict[property_tuple] #dobicemo ili oduzecemo energiju
            self.log_food_or_poision(self.model.food_dict[property_tuple])
            #print (self.procedural)
        else:
#            print ("Nothing here!!")
            pass

    def store_in_memory(self,hranljivost,property_tuple):
        """Stavlja u memoriju,svaki put kada pojede nesto, ako nije vec u memoriji
        ako je vec u memoriji, onda osvezi memoriju. Tj. ako pojede nesto cega se vec seca, tj. hranljivo je """
        rezultat = self.procedural.search_memory(property_tuple)
        if rezultat:
            self.procedural.remove(rezultat)
        poz = self.insertion_dict[hranljivost]
        self.procedural.insert_and_pop(poz,MemoryTuple(kombinacija=property_tuple,hranljivost=hranljivost))
        assert(len(self.procedural)<=self.memory_size)
        
    def log_food_or_poision(self,hranljivost):
        """Zapisuje da li smo pojeli otrov ili hranu"""
        if hranljivost<0:
            self.pojedeni_otrovi+=1
        elif hranljivost>0:
            self.pojedena_hrana+=1
        
        
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
        
        
    
class HungerModel(Model):
    """A model with some number of agents."""
    # boje = ["red","yellow","green","blue"]
    # ukusi = ["kiselo","ljuto","gorko","slatko"]
    # oblici = ["zvezda","kvadrat","krug","trougao"]
    boje = range(0,100)
    ukusi = range(0,100)
    oblici = range(0,100)
    sve_kombinacije= list(starmap(KombinacijaTuple,product(boje,ukusi,oblici)))
    def __init__(self,N,size,br_hrane_po_stepenu,br_stepena_otrovnosti,agent_memory_size=32,agent_walk_energy=0.2):
        import math
        br_hrane = br_hrane_po_stepenu*br_stepena_otrovnosti
        self.kombinacije = self.sve_kombinacije[:br_hrane]
        self.check_input(agent_memory_size,br_stepena_otrovnosti,br_hrane)

        self.food_dict = self.raspodeli_hranu(self.kombinacije,br_stepena_otrovnosti,br_hrane_po_stepenu)
        if br_hrane>len(self.kombinacije): #moramo napraviti duplikate
            dodatak= [self.random.choice(self.kombinacije) for i in range(br_hrane-len(self.kombinacije))]
            assert(len(dodatak)==br_hrane-len(self.sve_kombinacije))
            self.kombinacije = self.sve_kombinacije + dodatak
        self.br_stepena_otrovnosti=br_stepena_otrovnosti
        self.num_agents = N
        self.num_food = br_hrane
        self.grid = MultiGrid(size,size,True)
        self.schedule= RandomActivation(self)
        self.running = True
        for i in range(self.num_agents):
            a = HungryAgent(i,self,memory_size=agent_memory_size,br_stepena_otrovnosti=br_stepena_otrovnosti,walk_energy=agent_walk_energy)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
            
        for i in range(self.num_food):
            kombinacija = self.kombinacije[i]
            id_offset = i+1000
            f = FoodAgent(id_offset,self, kombinacija[0],kombinacija[1],kombinacija[2])
            self.schedule.add(f)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(f,(x,y))
            
        self.datacollector = DataCollector(
        model_reporters = {"TotalKnowledge":compute_knowledge,"TotalEnergy":total_energy,"TotalExperience":measure_experience,"TotalFood":total_pojedena_hrana,"TotalPoison":total_pojedeni_otrovi,"AverageEnergyPerCapita":average_energy_per_capita})
  #      agent_reporters = {"Knowledge":"knowledge"})

    def check_input(self,agent_memory_size,br_stepena_otrovnosti,br_hrane):
        if agent_memory_size<=0:
            raise SmallMemoryError("Agent memory must be positive!")
        if br_stepena_otrovnosti<=1 or (br_stepena_otrovnosti%2)!=0:
            raise PoisonError("Broj stepena otrovnosti mora biti paran i pozitivan!")
        #ovih num_of_food random bira TODO
        if br_hrane<=0:
            raise HranaError("Nedovoljan broj hrane/otrova")
        if br_hrane<br_stepena_otrovnosti:
             raise HranaError("Manje hrane od stepena otrovnosti!!")
        if br_stepena_otrovnosti>len(self.sve_kombinacije):
            raise PoisonError("Ima vise stepena otrovnosti nego hrane!!")
        
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        
    def raspodeli_hranu(self,kombinacije,br_stepena_otrovnosti,br_hrane_po_stepenu):
        """Od svih mogucih kombinacija hrane, on ih svrstava po otrovnosti. znaci ako imamo 64 hrane i 8 nivoa otrovnosti svaki nivo ce imati 8 stvari"""
        from math import ceil
        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]
        food_dict = dict()
        chunks_kombinacija = list(chunks(kombinacije,br_hrane_po_stepenu))
        nivo = -br_stepena_otrovnosti//2
        
        for (i,chunk) in enumerate(chunks_kombinacija):

            if nivo==0:
                nivo+=1
            for tpl in chunk:
                food_dict[tpl] = nivo
            nivo+=1
        assert(len(food_dict.keys())==len(kombinacije))
        return food_dict

def izdvoji_agente(model):
    return [a for a in model.schedule.agents if isinstance(a,HungryAgent)]

def compute_knowledge(model):
    """Ukupno znanje svih HungryAgenata"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in  agents:
        for key,value in agent.svet.items():
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
        ukupno+=len(agent.procedural)
    return ukupno

def total_energy(model):
    """Meri energiju svih agenata"""
    agents = izdvoji_agente(model)
    ukupno = 0
    for agent in agents:
        ukupno+=agent.energy
        
    return ukupno

def average_energy_per_capita(model):
    num_agents = len(izdvoji_agente(model))
    avg_energy = total_energy(model)/num_agents
    return avg_energy
                     
    
if __name__=="__main__":
    m = HungerModel(10,10,10,br_stepena_otrovnosti=18)
    
