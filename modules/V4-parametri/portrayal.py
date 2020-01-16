from model import *
from mesa.visualization.modules import CanvasGrid,ChartModule
from mesa.visualization.ModularVisualization import ModularServer

BROJ_AGENATA=100
STEPENI_OTROVNOSTI = 8
KOLICINA_ZA_SVAKU_OTROVNOST = 100 #koliko cemo od svake otrovnosti
KOLICINA_HRANE = KOLICINA_ZA_SVAKU_OTROVNOST*STEPENI_OTROVNOSTI
DIMENZIJA_TABLE = 100
WALK_ENERGY = 0
MEMORIJA_AGENATA= 32





def agent_portrayal(agent):
    portrayal= {"Shape":"circle",
                "Filled":"true",
                "Layer":1,
                "Color":agent.boja,
                "r":agent.size
                 }
    return portrayal


grid = CanvasGrid(agent_portrayal,DIMENZIJA_TABLE,DIMENZIJA_TABLE,500,500)

chart = ChartModule([{"Label": "TotalKnowledge",
                      "Color": "black"}],
                    data_collector_name='datacollector')
exp_chart = ChartModule([{"Label": "TotalExperience",
                      "Color": "black"}],
                    data_collector_name='datacollector')
life_chart = ChartModule([{"Label": "TotalEnergy",
                      "Color": "black"}],
                    data_collector_name='datacollector')

food_poison_chart = ChartModule([{"Label":"TotalFood","Color":"black"},{"Label":"TotalPoison","Color":"blue"}])
server = ModularServer(HungerModel,[grid,chart,life_chart,exp_chart,food_poison_chart],"Hunger Model",{"N":BROJ_AGENATA,"size":DIMENZIJA_TABLE,"br_hrane":KOLICINA_HRANE,"agent_walk_energy":WALK_ENERGY,"br_stepena_otrovnosti":STEPENI_OTROVNOSTI,"agent_memory_size":MEMORIJA_AGENATA})
server.port = 8523
server.launch()
