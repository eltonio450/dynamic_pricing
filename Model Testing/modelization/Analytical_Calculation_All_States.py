import math
import time
from modelization.engine.State_Map import State_Map

class Analytical_Calculation_All_States(object):
    """description of class"""
    def __init__(self):
        pass

    def setParameters(self, min_price, max_price, n_prices, n_parts, n_periods, max_sales = 0, gamma = 0.95):
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
        self.PRICE_LIST = range(self.min_price, self.max_price, int((self.max_price - self.min_price)/self.n_prices))
        

    def setDistribution(self, distribution):
        self.distribution = distribution

    def generateStateMap(self, verbose = False):
        if(verbose): print("Generation of the states...")
        start = time.time()
        self.G = State_Map(self.max_sales, self.n_periods, self.n_parts)
        end = time.time()
        if(verbose):print("Generation time: "+ str(end - start))

    def run(self, verbose = False):
        start = time.time()

        self.calculateValues()
        self.calculatePrices()
        end = time.time()

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
            earnings[p] = self.rewardDict[min(s1.get_inventory(),self.max_sales), p]
            for s in nextsList:
                earnings[p] = earnings[p] + self.gamma*s.value*self.distribution.getTransitionProbability(p, s1, s, self.G)
        
        p_max = self.PRICE_LIST[0] 
        for p in self.PRICE_LIST:
            if earnings[p] > earnings[p_max]:
                p_max = p
        return p_max

class Exponential_Approximation(Analytical_Calculation_All_States):
    """description of class"""
    def __init__(self):
        self.parametersReady = False
        self.distributionReady = True
        self.ready = False
        self.finished = False

    def setCoefficients(self, H):
        self.H = H

    def calculateValues(self):
        if(self.n_parts != 0):
            for item in self.G.stateList:
                j = 0 #premiere coordonnes du tuple
                value = 0
                i = 1
                while i <= self.n_parts:
                    for k in range(0,item.tuple[j]):
                        value += self.H[i]*math.pow(self.gamma,j)
                        i+=1
                    j+=1  
                item.value = value
        else:
            for item in self.G.stateList:
                item.value = 0
    
    

class Continuous_Approximation(Analytical_Calculation_All_States):
    
    def __init__(self):
        self.value_approximations = {}
        self.prices_approximations = {}
        self.rewardDict = None

    def setApproximateValues(self, value_dict):
        self.value_approximations[0] = value_dict
        self.prices_approximations[0] = {}
        self.calculatePricesFixedDepth(0)

    def setDepth(self, depth):
        self.depth = depth
        self.prices_approximations[0] = {}
        for i in range(1, depth+1):
            self.value_approximations[i] = {}
            self.prices_approximations[i] = {}

    def calculatePricesFixedDepth(self, depth):
        if self.rewardDict is None:
            self.distribution.generateTransitionProbabilities(self.PRICE_LIST)
            self.rewardDict = self.distribution.generateRewardDict(self.PRICE_LIST)

        for i in self.value_approximations[depth].keys():
            self.prices_approximations[depth][i] = self.approximatePrice(self.G.stateList[i], self.value_approximations[depth])

    def approximatePrice(self, s1, value_approx):
        nexts = s1.get_children_reduced_tuples(self.max_sales)
        nextsList = []
        for tuples in nexts:
            nextsList.append(self.G.stateList[self.G.stateDict[tuples]])
        
        earnings = {}
        
        for p in self.PRICE_LIST:
            earnings[p] = self.rewardDict[min(s1.get_inventory(),self.max_sales), p]
            for s in nextsList:
                earnings[p] = earnings[p] + self.gamma*value_approx[s.index]*self.distribution.getTransitionProbability(p, s1, s, self.G)
  
        p_max = self.PRICE_LIST[0] 
        for p in self.PRICE_LIST:
            if earnings[p] > earnings[p_max]:
                p_max = p
        return p_max

    def calculateValuesAllDepth(self):
        i = 1
        while i <= self.depth:
            self.calculateValuesFixedDepth(i) 
            self.calculatePricesFixedDepth(i)
            i+=1

    def calculateValuesFixedDepth(self, depth):
        if depth >= 0:
            for i in range(0, len(self.G.stateList)):
                self.value_approximations[depth][i] = self.approximateValue(self.G.stateList[i], depth)


    def approximateValue(self, state, depth):
        if self.n_parts == 0:
            return 0
        if state.get_inventory() == 0:
            return_time = state.get_first_return_time()
            futur_state = self.G.getStateFromTuple(state.get_shifted_tuple(return_time))
            if futur_state.index not in self.value_approximations[depth].keys():
                self.approximateValue(futur_state, depth)
            return self.gamma**return_time * self.value_approximations[depth][futur_state.index]
        else:
            price = self.prices_approximations[depth-1][state.index]
            new_value = self.rewardDict[min(state.get_inventory(),self.max_sales), price]
            nexts = state.get_children_reduced_tuples(self.max_sales)
            nextsList = []
            for i in nexts:
                nextsList.append(self.G.getStateFromReducedTuple(i))
            for s in nextsList:
                new_value = new_value + self.gamma*self.value_approximations[depth-1][s.index]*self.distribution.getTransitionProbability(price, state, s, self.G)
            return new_value

    def calculateValues(self):
        self.calculateValuesAllDepth()
        for item in self.G.stateList:
            item.value = self.value_approximations[self.depth][item.index]
    """description of class"""

