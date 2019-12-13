import unittest
from model import *
from datatypes import *
WIDTH = 10
HEIGHT = 10
N = 0

class TestAgent(unittest.TestCase):

    def setUp(self):
        pass
    

    def tearDown(self):
        pass
    

    def test_make_insertion_dict(self):

        walk_energy=0
        br_hrane = 100

        for mem_size in range(-100,100):

            if mem_size<=0:
                self.assertRaises(SmallMemoryError)
                continue
            for p_levels in range(-100,100):
                if p_levels<=1 or (p_levels%2)!=0 or p_levels>len(HungerModel.sve_kombinacije):
                    self.assertRaises(PoisonError)
                    continue

                for br_hrane in range(-100,100):
                    print(p_levels,mem_size,br_hrane)
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

        mockModel = HungerModel(N,
                                WIDTH,HEIGHT,
                                )
        
        sve_kombinacije = HungerModel.sve_kombinacije

        for komb in sve_kombinacije:
            food = FoodAgent(3,mockModel,boja=komb.boja,ukus=komb.ukus,oblik=komb.oblik)

            

