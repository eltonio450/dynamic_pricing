import time
import mdptoolbox
from modelization.engine.State_Map import State_Map
import numpy as np

#this class allows to perform exacts simulations on a set of prices, N and L.
class Simulation(object):
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

        if(self.verbose):print("Generation of the price -> probability map...")
        start = time.time()
        PRICE_LIST = range(self.min_price, self.max_price, int((self.max_price - self.min_price)/self.n_prices))
        self.distribution.generateTransitionProbabilities(PRICE_LIST)
        tms = self.distribution.generateTransitionMatrices(PRICE_LIST, self.G)
        end = time.time()
        if(self.verbose):print("Computation time the price -> probability map: "+ str(end - start))

        if(self.verbose):print("Generation of the price -> reward map...")
        start = time.time()
        rms = self.distribution.generateRewardMatrices(PRICE_LIST,self.G)
        end = time.time()
        if(self.verbose):print("Computation time for the reward map: "+ str(end - start))

        optimalPolicy = mdptoolbox.mdp.PolicyIteration(tms, rms, self.gamma)
        start = time.time()
        optimalPolicy.run()
        end = time.time()
        if(self.verbose):print("Solver: "+ str(end - start))

        # Calculate the stationary transition map when the best policy is reached.

        self.stationary_transition_map = np.zeros((len(self.G.stateList),len(self.G.stateList)))

        start = time.time()
        if(self.verbose): print("Computing the stationary Markov Chain and properties...")
        for i in range(0, len(self.G.stateList)):
            self.G.stateList[i].value=optimalPolicy.V[i]
            self.G.stateList[i].price = optimalPolicy.policy[i]*(self.max_price-self.min_price)/self.n_prices + self.min_price
    
        #G.calculateStationaryTransitionMap(distribution)
        #G.calculateStationaryProbabilities()
        #stationary_transition_map = G.stationary_transition_map
        end = time.time()
        if(self.verbose):print("Stationary Markov Chain: "+ str(end - start))
        self.finished = True

    def setParameters(self, min_price, max_price, n_prices, n_parts, n_periods, max_sales = 0, gamma = 0.99, verbose = False):
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

    def setDistribution(self, distribution):
        self.distribution = distribution
        self.distributionReady = True
        self.ready = self.parametersReady


    def getStates():
        pass

    def getValues():
        pass

    def getPrices():
        pass

    def getStationaryProbabilities():
        pass

    def isFinished(self):
        return self.finished
