import unittest
from model import *
from datatypes import *
WIDTH = 10
HEIGHT = 10
N = 0

class TestAgent(unittest.TestCase):

    def setUp(self):
        self.HungerModelMock =HungerModel(N,WIDTH,HEIGHT)

    

    def tearDown(self):
        pass

    def make_insertion_dict(self):

        walk_energy=0
        br_hrane = 100

        for mem_size in range(-10,50):

            if mem_size<=0:
                self.assertRaises(SmallMemoryError)
                continue
            for p_levels in range(-10,50):
                if p_levels<=1 or (p_levels%2)!=0 or p_levels>len(HungerModel.sve_kombinacije):
                    self.assertRaises(PoisonError)
                    continue

                for br_hrane in range(-10,50):
                    if br_hrane<=0 or br_hrane<p_levels:
                        self.assertRaises(HranaError)
                        continue
                    
                    mockModel = HungerModel(N,
                                WIDTH,HEIGHT,
                                br_stepena_otrovnosti=p_levels,
                                agent_memory_size=mem_size,
                                        agent_walk_energy=walk_energy,num_of_food=br_hrane)
                    self.agent = HungryAgent(3,mockModel,mem_size,br_stepena_otrovnosti=p_levels,
                                             walk_energy=walk_energy)
                    ind = self.agent.make_insertion_dict(br_stepena_otrovnosti = p_levels, memory_size=mem_size)

                    self.assertEqual(len(ind.keys()),p_levels)

                    for k,i in ind.items():
                        self.assertGreaterEqual(i,0)
                        if (mem_size//p_levels)!=0:
                            self.assertTrue((i% (mem_size//p_levels))==0)
                            self.assertGreaterEqual(k,-p_levels//2)
                            self.assertLessEqual(k,p_levels//2)

    def test_agent_explore(self):
        pass

    def test_scrape_memory(self):
        """Treba da sabere sve instance gde se dat tuple pojavio u memoriji
        ovo mozemo da testiramo tako sto cemo dati nekoliko primera proceduralne memorije
        i nekoliko primera tuplova, i proveriti da li je dobar zbir"""
        brot = self.HungerModelMock.br_stepena_otrovnosti
        mem_size = 32
        agent = HungryAgent(3,self.HungerModelMock,memory_size=mem_size,br_stepena_otrovnosti=brot,walk_energy=0)
        #        procedural = MemoryDeque([],maxlen=mem_size)
        hr=5
        agent.procedural.insert_and_pop(0,MemoryTuple(kombinacija=KombinacijaTuple(boja="crvena",ukus="ljuto",oblik="kvadrat"),hranljivost=hr))
        rez = agent.scrape_memory(KombinacijaTuple(boja="crvena",ukus="kiselo",oblik="zvezda"))
        self.assertEqual(rez,hr)
        agent.procedural.insert_and_pop(0,MemoryTuple(kombinacija=KombinacijaTuple(boja="crvena",ukus="kiselo",oblik="kvadrat"),hranljivost=-hr))
        rez = agent.scrape_memory(KombinacijaTuple(boja="crvena",ukus="kiselo",oblik="zvezda"))
        self.assertEqual(rez,-5)

        

    def test_decide_eat(self):
        pass

    def test_eat_or_not(self):
        pass

    def test_store_in_memory(self):
        pass

    
        
            

