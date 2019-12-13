from HungerModelV2 import *
from mesa.visualization.modules import CanvasGrid,ChartModule
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    portrayal= {"Shape":"circle",
                "Filled":"true",
                "Layer":1,
                "Color":agent.boja,
                "r":agent.size
                 }
    return portrayal


grid = CanvasGrid(agent_portrayal,20,20,500,500)

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
server = ModularServer(HungerModel,[grid,chart,life_chart,exp_chart,food_poison_chart],"Hunger Model",{"N":20,"width":20,"height":20,"num_of_food":64})
server.port = 8521
server.launch()
