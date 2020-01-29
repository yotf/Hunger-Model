from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

class Cell(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        


class CancerCell(Cell):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.color = "black"


class CancerStemCell(Cell):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.color = "red"


class CureAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.color = "yellow"

    def step(self):
        self.move()
        self.eat_or_not()

    def move(self):
        """The agents will move in a random direction and lose specified energy"""
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center = False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)

    def eat_or_not(self):
        from numpy.random import choice
        cells = [f for f in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(f,Cell)]
        for c in cells:
            eat = choice([True,False],1,p=[0.2,0.8])
            if eat:
                print("EATEN") #TODO da li umre svaki put kad pokusa uopste?? 
                self.model.grid.remove_agent(c)
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
            



class CancerModel(Model):
    def __init__(self,cancer_cells_number,cure_number):
        import math
        def percentage(percent, whole):
            return (percent * whole) / 100.0
        grid_size = math.ceil(math.sqrt(cancer_cells_number*4))
        self.grid = MultiGrid(grid_size,grid_size,False) #TODO proveri da ne ide okolo,
        #MOZDA TREBA SINGLEGRID????????
        poss = self.generate_cancer_cell_positions(grid_size,cancer_cells_number)
        num_CSC = math.ceil(percentage(1,cancer_cells_number))
        pos_CSC = [self.random.choice(poss) for i in range(num_CSC)]
        self.schedule = RandomActivation(self)
        self.running = True
        print(pos_CSC)
        for i in range(cancer_cells_number):
            pos = poss[i]
            c = CancerStemCell(i,self) if pos in pos_CSC else CancerCell(i,self)
            self.grid.place_agent(c,pos)

        for i in range(cure_number):
            offset = 1000
            #pos = self.grid.find_empty()
            pos = (0,0)
            a = CureAgent(i+offset,self)
            self.grid.place_agent(a,pos)
            self.schedule.add(a)

    def generate_cancer_cell_positions(self,grid_size,cancer_cells_number):
        center = grid_size//2
        poss = [(center,center)]
        for pos in poss:
            poss+=(self.grid.get_neighborhood(pos,moore=True,include_center=False))
            if len(set(poss))>=cancer_cells_number:
                poss = list(set(poss))
                break
        return poss
    def step(self):
        self.schedule.step()
        



