import math
import numpy as np
from bin.engine.State import *



class Distribution(object):
    """description of class"""

    def __init__(self, backoder_fixed_cost):
        self.bfc = backoder_fixed_cost
        self.transition_probability_matrix = None
        self.transition_reward_matrix = None

    def generateTransitionMatrices(self, p_min, p_max, n_intervalles, map):
        states_list = map.stateList
        n_states = len(states_list)
        tmm = np.zeros((n_intervalles, n_states, n_states))
        
        step = float(p_max-p_min)/n_intervalles

        p = p_min
        for i in range(0, n_intervalles):
            tmm[i,:,:] = self.generateTransitionMatrix(p, map)
            p += step

        return tmm


    def generateTransitionMatrix(self, p: int, map):
        n_states = len(map.stateList)

        tm = np.zeros((n_states,n_states))

        for trans in map.transition_list:
                tm[trans[0],trans[1]] = self.calculateTransitionProbability(p, map.stateList[trans[0]], map.stateList[trans[1]], map)
        return tm
    
    """This function calculates the transition probibilty between two states s1 and s2, depending on the price, and for this specific distribution.
        Returns 0 if the transition is not possible
        Return the sum of all the cases with backorder if inventory = transition sales"""
    def calculateTransitionProbability(self, p: float, s1: State, s2: State, map):
        if map.is_authorized(s1, s2):
            if s1.get_inventory() > s2.get_last_period_sales(): 
                return self.probability(s2.get_last_period_sales(), p)
            else:
                sum_others = 0
                for i in range(0, s1.get_inventory()):
                    sum_others += self.probability(i, p)
                return (1 - sum_others)
        else:
            return 0

    def generateRewardMatrices(self, p_min, p_max, n_intervalles, map):
        states_list = map.stateList
        n_states = len(states_list)
        tmm = np.zeros((n_intervalles, n_states, n_states))
        
        step = float(p_max-p_min)/n_intervalles

        p = p_min
        for i in range(0, n_intervalles):
            tmm[i,:,:] = self.generateRewardMatrix(p, map)
            p+= step

        return tmm


    def generateRewardMatrix(self, p: int, map):
        n_states = len(map.stateList)

        tm = np.zeros((n_states,n_states))
        for trans in map.transition_list:
            tm[trans[0],trans[1]] = map.stateList[trans[1]].get_last_period_sales()*p - self.calculateBackorderCost(self.backorder_cost(p), p, map.stateList[trans[0]].get_inventory())
        return tm




    
    def backorder_cost(self, p):
        return max(p, self.bfc)


"""parent class for the Poisson Distribution. Only the children take the price into account: the parent has a fixed lambda"""
class Poisson(Distribution):
    def __init__(self, lambda_distribution, backoder_fixed_cost):
        self.lambda_dist = lambda_distribution
        self.bfc = backoder_fixed_cost
        
    """For a given p, this function return the lambda(p) corresponding to the corresponding Poisson distribution"""
    def lambda_distribution(self, p):
        return self.lambda_dist
    
    def probability(self, k, p):
        return math.pow(self.lambda_distribution(p),k) * math.exp(-self.lambda_distribution(p))/math.factorial(k)

    """Estimates de backorder cost, with 1% maximum error. Must be checked"""
    def calculateBackorderCost(self, cost_per_item, p, N):
        k = N+1
        res = 0
        t = cost_per_item*(k-N)*self.probability(k, p)
        res += t
        while 100*t > res:
            k += 1
            t = cost_per_item*(k-N)*self.probability(k, p) 
            res += t
        return res
    


class PoissonWithLinearLambda(Poisson):
    def __init__(self, market_size_lambda, past_price, past_lambda, backoder_fixed_cost):
        self.market_size_lambda = market_size_lambda
        self.past_price = past_price
        self.past_lambda = past_lambda
        self.bfc = backoder_fixed_cost
    
    def lambda_distribution(self, p):
        return max(self.market_size_lambda - p*(self.market_size_lambda - self.past_lambda)/self.past_price, 0)


"""We want that the lambda parameters decays with the price, under a parameter alpha"""
class PoissonWithExponentialLambda(Poisson):
    def __init__(self, market_size_lambda, past_price, past_lambda, backoder_fixed_cost):
        self.market_size_lambda = market_size_lambda
        self.past_price = past_price
        self.past_lambda = past_lambda
        self.alpha = -math.log(past_lambda/market_size_lambda)/past_price
        self.bfc = backoder_fixed_cost

    def lambda_distribution(self, p):
        return self.market_size_lambda*math.exp(-self.alpha*p)