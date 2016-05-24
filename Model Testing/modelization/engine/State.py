from collections import deque
from configuration import parameters as P
import copy

class State:
    """description of class"""
    """Ce que l'on veut avec un etat, c'est attribuer un prix au produit.""" 
    succList = None
    predList = None



    def __init__(self, tuple, value = 0):
        self.tuple = tuple
        self.value = value
        self.price = 0
        self.stationary_probability = 0
        self.stationary_lambda = 0
        self.stationary_bo_cost = 0
        self.index = 0
        
        self.list_predecessors = []
        self.list_successors = []
        





    def __eq__(self, other):
        if isinstance(other, State):
            return self.tuple==other.tuple    
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    """def __hash__(self):
        if(isinstance(self, State)):
            value = 0x345678
            for item in self.tuple:
                value = eval(hex((int(1000003) * value) & 0xFFFFFFFF)[:-1])
            value = value ^ len(self.tuple)
        if value == -1:
            value = -2
            return value
        else:
            return 0 """

    def __str__(self):
        return "S=" + str(self.tuple) + ", V=" + str(int(self.value))+", lam=" + str(self.stationary_lambda) +", p=" + str(int(self.price)) + ", SP=" + str(self.stationary_probability) + ", BO=" + str(int(self.stationary_bo_cost))


    def set_successors(self, succList): succList = succList

    def set_predecessors(self, predList):
        predList = predList
    
    def get_successors(self):
        return self.succList

    def get_predecessors(self):
        return self.predList
        

    def value_to_other_state(self, state):
        pass
        
    def get_inventory(self):
        return self.tuple[0]

    def get_last_period_sales(self):
        return self.tuple[-1]

    #def guess_successors(self):
    #    res = []
    #    for i in range(0,min(P.MAX_PER_WEEK,self.stock)+1):
    #        new_repair_queue = copy.deepcopy(self.repair_queue)
    #        new_repair_queue.append(i)
    #        res.append(State(self.stock + new_repair_queue.popleft() - i , new_repair_queue))
    #    return res

    #def guess_predecessors(self):
    #    res = []
    #    for i in range(0,min(P.MAX_PER_WEEK,self.stock)+1):
    #        new_repair_queue = copy.deepcopy(self.repair_queue)
    #        new_repair_queue.append(i)
    #        res.appendleft(State(self.stock + new_repair_queue.pop() - i , new_repair_queue))
    #    return res

    def print(self):
        print(str(self))