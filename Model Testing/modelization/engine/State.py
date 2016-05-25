from collections import deque
from configuration import parameters as P
import copy

class State:
    """description of class"""
    """Ce que l'on veut avec un etat, c'est attribuer un prix au produit.""" 
    def __init__(self, tuple, value = 0):
        self.tuple = tuple
        self.value = value
        self.price = 0
        self.stationary_probability = 0
        self.stationary_lambda = 0
        self.stationary_bo_cost = 0
        self.index = 0

    def __eq__(self, other):
        if isinstance(other, State):
            return self.tuple==other.tuple    
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __str__(self):
        return "S=" + str(self.tuple) + ", V=" + str(int(self.value))+", lam=" + str(self.stationary_lambda) +", p=" + str(int(self.price)) + ", SP=" + str(self.stationary_probability) + ", BO=" + str(int(self.stationary_bo_cost))
        
    def get_inventory(self):
        return self.tuple[0]

    def get_last_period_sales(self):
        return self.tuple[-1]

    def child(self, sales):
        if sales <= self.get_inventory():
            return self.tuple[2::]+(sales,)
        else:
            raise("Impossible transition")