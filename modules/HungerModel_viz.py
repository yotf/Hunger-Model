from HungerModel import *
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


grid = CanvasGrid(agent_portrayal,10,10,500,500)

chart = ChartModule([{"Label": "TotalKnowledge",
                      "Color": "black"}],
                    data_collector_name='datacollector')
server = ModularServer(HungerModel,[grid,chart],"Hunger Model",
                      {"N":20,"width":10,"height":10,"num_of_food":64})
server.port = 8521
server.launch()
