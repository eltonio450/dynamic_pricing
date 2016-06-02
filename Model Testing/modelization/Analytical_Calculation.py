import math
import time
from modelization.engine.State_Map import State_Map

class Analytical_Calculation(object):
    """description of class"""
    def __init__(self):
        self.parametersReady = False
        self.distributionReady = True
        self.ready = False
        self.finished = False

    def setParameters(self, min_price, max_price, n_prices, n_parts, n_periods, max_sales = 0, gamma = 0.95, verbose = False):
        if max_sales is not 0:
            self.max_sales = max_sales
        else:
            self.max_sales = n_parts
        self.gamma = gamma
        self.min_price = min_price
        self.max_price = max_price
        self.n_prices = n_prices
        self.n_parts = n_parts
        self.n_periods = n_periods
        self.parametersReady = True
        self.verbose = verbose
        self.ready = self.distributionReady
        self.PRICE_LIST = range(self.min_price, self.max_price, int((self.max_price - self.min_price)/self.n_prices))
        

    def setDistribution(self, distribution):
        self.distribution = distribution
        self.distributionReady = True
        self.ready = self.parametersReady

class Analytical_Calculation_With_Coefficients(Analytical_Calculation):
    """description of class"""
    def __init__(self):
        self.parametersReady = False
        self.distributionReady = True
        self.ready = False
        self.finished = False


    def run(self, verbose = False):
        self.verbose = verbose
        if not self.ready:
            raise("Simulation not ready: missing parameters or distribution")

        if(self.verbose): print("Generation of the states...")
        start = time.time()
        self.G = State_Map(self.max_sales, self.n_periods, self.n_parts)
        end = time.time()
        if(self.verbose):print("Generation time: "+ str(end - start))

        start = time.time()
        self.calculateValues()
        self.calculatePrices()
        end = time.time()

    def setCoefficients(self, H):
        self.H = H

    def calculateBestPrice(self, s1):
        pass
                           
    def calculateValues(self):
        for item in self.G.stateList:
            value = self.H[0]
            i = 1 #premiere piece
            j = 0 #premiere coordonnes du tuple
            while i <= self.n_parts:
                for k in range(0,item.tuple[j]):
                    value += self.H[i]*math.pow(self.gamma,j)
                    i+=1
                j+=1  
                      
            item.value = value  
    
    def calculatePrices(self):
        self.distribution.generateTransitionProbabilities(self.PRICE_LIST)
        self.rewardDict = self.distribution.generateRewardDict(self.PRICE_LIST)
        for item in self.G.stateList:
             
             item.price = self.calculatePrice(item)

    def calculatePrice(self, s1):
        nexts = s1.get_children_reduced_tuples(self.max_sales)
        nextsList = []
        for i in nexts:
            nextsList.append(self.G.stateList[self.G.stateDict[i]])
        earnings = {}
        for p in self.PRICE_LIST:
            earnings[p] = self.rewardDict[s1.get_inventory(), p]
            for s in nextsList:
                earnings[p] = earnings[p] + self.gamma*s.value*self.distribution.getTransitionProbability(p, s1, s, self.G)
        
        p_max = self.PRICE_LIST[0] 
        for p in self.PRICE_LIST:
            if earnings[p] > earnings[p_max]:
                p_max = p
        return p_max