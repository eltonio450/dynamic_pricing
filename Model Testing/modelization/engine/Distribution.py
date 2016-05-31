import math
import numpy as np
from modelization.engine.State import *



class Distribution(object):
    """description of class"""

    """Generates the probability of transition, regarding the distribution.
    - normalTP(i, p) is the probability to sell i items when the price is p
    - backorderTP(i, p) is the probabilty of selling i items when the price is p and the inventory is i: it is the probability to have a demand between i and infitnity
    
    """

    def generateTransitionProbabilities(self, p_list):
        self.normalTP = {}
        self.backorderedTP = {}
        #i designates the number of items in our inventory
        for i in range(0, self.N_max+1):
            for p in p_list:          
                self.normalTP[i, p] = self.probability(i, p)
                if i == 0:
                    self.backorderedTP[i, p] = 1
                else:
                    #to avoind rounding issues
                    self.backorderedTP[i, p] = max(self.backorderedTP[i-1, p] - self.probability(i-1, p), 0)

    
                

    def generateTransitionMatrices(self, p_list, map):
        n_states = len(map.stateList)
        tmm = np.zeros((len(p_list), n_states, n_states))
        for i in range(0, len(p_list)):
            tmm[i,:,:] = self.generateTransitionMatrix(p_list[i], map)
        return tmm

    

    def generateTransitionMatrix(self, p: int, map):
        n_states = len(map.stateList)
        tm = np.zeros((n_states,n_states))
        for trans in map.transition_list:
                tm[trans[0],trans[1]] = self.getTransitionProbability(p, map.stateList[trans[0]], map.stateList[trans[1]], map)
        return tm
    
    """This function calculates the transition probibilty between two states s1 and s2, depending on the price, and for this specific distribution.
        Returns 0 if the transition is not possible
        Return the sum of all the cases with backorder if inventory = transition sales"""
    def getTransitionProbability(self, p: int, s1: State, s2: State, map):
        if map.is_authorized(s1, s2):
            if min(s1.get_inventory(), self.N_max) > s2.get_last_period_sales(): 
                return self.normalTP[s2.get_last_period_sales(), p]
            else:
                return self.backorderedTP[s2.get_last_period_sales(), p]
        else:
            return 0

    """Generates the reward matrices. rmm[i,j,k] corresponds to the reward, going from state j to state k, with price set up at i""" 
    def generateRewardMatrices(self, p_list, map):
        n_states = len(map.stateList)
        dict = self.generateRewardDict(self.get_backorder_cost(), p_list)
        rmm = np.zeros((len(p_list), n_states, n_states))
        for i in range(0, len(p_list)):
            for j in range(0, n_states):
                rmm[i,j,:] = np.ones(n_states)*dict[min(map.stateList[j].get_inventory(), self.N_max), p_list[i]]
        return rmm




    
    def get_backorder_cost(self):
        return self.bfc


"""parent class for the Poisson Distribution. Only the children take the price into account: the parent has a fixed lambda"""
class Poisson(Distribution):
    def __init__(self, lambda_distribution, backoder_fixed_cost, N_max):
        self.lambda_dist = lambda_distribution
        self.bfc = backoder_fixed_cost
        self.N_max = N_max
        
    """For a given p, this function return the lambda(p) corresponding to the corresponding Poisson distribution"""
    def lambda_distribution(self, p):
        return self.lambda_dist
    
    def probability(self, k, p):
        return math.pow(self.lambda_distribution(p),k) * math.exp(-self.lambda_distribution(p))/math.factorial(k)

    """in the case of a poisson distribution, the bo cost is lambda - sum of what we could have sold"""
    """The reward dictionnary corresponds to a dictionnary of the expected reward, regardless of the transition.
    --> dict[inventory, p] correspond to our expectated revenue if we have n parts in our inventory and we set up the price to p.
    All the parts that we sell above inventory (or n_max by the way) are considered as backordered."""
    def generateRewardDict(self, backorder_cost, price_list):
        res = {}
        for i in range (0, self.N_max+1):
            for p in price_list:
                possibly_sold = 0
                for j in range(0, i+1):
                    possibly_sold += j*self.normalTP[j, p]
                res[i,p] = p * possibly_sold - backorder_cost * (self.lambda_distribution(p) - possibly_sold)
        return res


class Bernoulli(Distribution):
    def __init__(self, parameter):
        self.parameter = parameter
        self.N_max = 1
        self.bfc = 100

    def parameter_distribution(self, price):
        return self.parameter
    
    def probability(self, k, price):
        if k == 0:
            return (1-self.parameter_distribution(price))
        else:
            return self.parameter_distribution(price)

    def generateRewardDict(self, backorder_cost, price_list):
        res = {}
        for p in price_list:            
            res[0,p] = - backorder_cost * (self.backorderedTP[0,p] - self.normalTP[0, p]) #forces p = p_max if inventory = 0
            res[1,p] = p*self.normalTP[1,p]
        return res

class BernoulliWithLinearParameter(Bernoulli):
    def __init__(self, past_price, past_sales, market_size):
        self.p_max = past_price/(1-(past_sales/market_size))
        self.N_max = 1
        self.bfc = 100
        self.market_size = market_size        

    def parameter_distribution(self, price):
        return max(min(self.market_size*(1 - float(price)/float(self.p_max)), 1), 0)

class PoissonWithLinearLambda(Poisson):
    def __init__(self, market_size_lambda, past_price, past_lambda, backoder_fixed_cost, N_max):
        self.market_size_lambda = market_size_lambda
        self.past_price = past_price
        self.past_lambda = past_lambda
        self.bfc = backoder_fixed_cost
        self.N_max = N_max

    def lambda_distribution(self, p):
        return max(self.market_size_lambda - p*(self.market_size_lambda - self.past_lambda)/self.past_price, 0)


"""We want that the lambda parameters decays with the price, under a parameter alpha"""
class PoissonWithExponentialLambda(Poisson):
    def __init__(self, market_size_lambda, past_price, past_lambda, backoder_fixed_cost, N_max):
        self.market_size_lambda = market_size_lambda
        self.past_price = past_price
        self.past_lambda = past_lambda
        self.alpha = -math.log(past_lambda/market_size_lambda)/past_price
        self.bfc = backoder_fixed_cost
        self.N_max = N_max

    def lambda_distribution(self, p):
        return self.market_size_lambda*math.exp(-self.alpha*p)