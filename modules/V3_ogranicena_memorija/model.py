from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.batchrunner import BatchRunner
import matplotlib.pyplot as plt
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import itertools
from itertools import starmap,product

from collections import deque
class MemoryDeque(deque):
    def __init__(self,liste,maxlen):
        super().__init__(liste,maxlen)
    def insert_and_pop(self,index,what):
        try:
            self.insert(index,what)
        except IndexError:
            self.pop()
            self.insert(index,what)

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
#ustvari oni treba da se preslikavaju na broj tako da ce biti ok sve
#znaci struktura je [((plavo,zvezda,ljuto),-1),....))]
#search nece biti bas najbolji, ali sta cemo, da je dictionary, ne bismo mogli da
#---------------------------------------------------------
#|  -4      |      +4      |     -3       |      +3      |
#---------------------------------------------------------
#|    -2    |       +2     |      -1      |     +1       |
#---------------------------------------------------------
#pozicije -4 -> 0,+4->3,...
import collections
komb_tuple = collections.namedtuple("Kombinacija","boja ukus oblik")
memory_tuple = collections.namedtuple("Memorija","kombinacija hranljivost")
pozicije_u_proceduralnoj = {-4:0,
                      +4:3,
                      -3:7,
                      +3:11,
                      -2:15,
                      +2:19,
                      -1:23,
                      +1:27}
boje = ["red","yellow","green","blue"]
ukusi = ["kiselo","ljuto","gorko","slatko"]
oblici = ["zvezda","kvadrat","krug","trougao"]
sve_kombinacije= list(starmap(komb_tuple,product(boje,ukusi,oblici)))
#sve_kombinacije = list(itertools.product(boje,ukusi,oblici))
level=-5 #odmah ce se povecati kod %
food_dict = dict()
for i,k in enumerate(sve_kombinacije):
    if (i%8==0):
        print(i)
        level+=1
        if level==0:
            level+=1
    print(level)
    print (k)
    assert(level!=0)
    food_dict[k]=level
assert(len(food_dict.keys())==64)



class HungryAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.energy = 0
        self.svet = {"boje":set(),"oblici":set(),"ukusi":set()}
        self.boja = "black"
        self.size = 0.2
        self.procedural =MemoryDeque([],maxlen=32)
        self.pojedeni_otrovi=0
        self.pojedena_hrana=0
        
    def move(self):
        self.energy=-0.2
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)
        
    def store_info(self,food):
        self.svet["boje"].add(food.boja)
        self.svet["oblici"].add(food.oblik)
        self.svet["ukusi"].add(food.ukus)

        
    def eat_or_not(self,food):

        def search_memory_deque(mdeque,ktuple):
            for entry in mdeque:
                print (entry)
                if entry.kombinacija ==ktuple:
                    print ("nadjeno u memoriji!")
                    return entry
            return None
                
                
                
        eat = None
        property_tuple=komb_tuple(boja=food.boja,ukus=food.ukus,oblik=food.oblik)
        
        rezultat = search_memory_deque(self.procedural, property_tuple)
        
        if rezultat:
            eat = False if rezultat.hranljivost<0 else True
        else:
            #barf, scrape_memory
            assert(eat is None)
            hranljivost=0
            for atribut in property_tuple:
                # za svaki atribut cemo skrejpovati memoriju, u svim mogucim kombincijama(mozda da napravim poseban dict, koji broji koliko puta je koji false, koliko puta je koji True. svakako bi se brojevima svasta resilo,takodje i stepni otrova, direkno ih mogu sabirati umesto svih ifova.)
                for ktuple in self.procedural:
                    if atribut in ktuple.kombinacija:
                        hranljivost+=ktuple.hranljivost
            
            print ("HRANLJIVOST: %s" %hranljivost)
            if hranljivost>0:
                eat=True
            elif hranljivost<0:
                eat=False
            else:
                eat = True #self.random.choice([True,False])
        
            if eat:
                hranljivost=food_dict[property_tuple]
                print (hranljivost)
                poz = pozicije_u_proceduralnoj[hranljivost]
                self.procedural.insert_and_pop(poz,memory_tuple(kombinacija=property_tuple,hranljivost=hranljivost))
                #ovde smo jedino ako nismo nasli u dictu
                        
        if eat:     #na kraju gledamo jesmo li pojeli ili nismo i onda sabiramo (posto smo mozda vec na pocetku pojeli) mozda ovde u explore npr da stavimo
            self.energy+=food_dict[property_tuple] #dobicemo ili oduzecemo energiju
            if food_dict[property_tuple]<0:
                self.pojedeni_otrovi+=1
            elif food_dict[property_tuple]>0:
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
        ukupno+=len(agent.procedural)
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
