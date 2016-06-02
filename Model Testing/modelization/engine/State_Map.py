from collections import Set
from collections import deque
from modelization.engine.State import State
import networkx as nx
import numpy as np
import time
import copy
from discreteMarkovChain import markovChain


class State_Map(object):
    """description of class"""
    """
    Cette classe reflete la carte des etats. 
    
   
    """

    
    def __init__(self, max_sales, L=10, N=5):
        self.max_sales = max_sales
        self.n_states = 0
        self.stateList = []
        self.stateDict = {}
        
        dictTuples = {}


        self.generateTuples(L, N, dictTuples)
        
        for q in dictTuples[L, N]:
            self.stateList.append(State(q))

        print("All the states have been generated.")

        """WARNING: the dictionary only contains a reduced version of the tuple"""
        for i in range(0, len(self.stateList)):
            self.stateList[i].index = i
            self.stateDict[self.stateList[i].tuple[1::]] = i


        self.n_states = len(self.stateList)
        print("Generated states: "+ str(self.n_states))

        self.stationary_transition_map = None
        self.transition_list = []
        self.authorized_transitions_matrix = self.generateAuthorizedTransitionMatrix()


    """ Fonction auditee""" 
    def generateTuples(self, L, N, dict):
        if (L,N) not in dict.keys():
            if L == 1:
                dict[L,N] = [(N,)]
            else:
                dict[L,N] = []
                for i in range(0,min(N+1, self.max_sales+1)):
                    self.generateTuples(L-1, N-i, dict)
                    for tuple in dict[L-1, N-i]:
                        new_tuple = (tuple)+ (i,)
                        dict[L,N].append(new_tuple)  
        
    def generateAuthorizedTransitionMatrix(self):
        tm = np.zeros((self.n_states, self.n_states))
        for state in self.stateList:
            for j in range(0, min(state.get_inventory(), self.max_sales)+1):
                succ_index = self.stateDict[state.get_child_tuple(j)]
                tm[state.index, succ_index] = 1
                self.transition_list.append((state.index, succ_index))
        return tm

    def calculateStationaryTransitionMap(self, distribution):
        self.stationary_transition_map = np.zeros((self.n_states, self.n_states))
        for i in range(0, self.n_states):
            self.stateList[i].stationary_lambda = int(1000*distribution.lambda_distribution(self.stateList[i].price))/1000.
            self.stateList[i].stationary_backoorder_cost = distribution.calculateBackorderCost(distribution.backorder_cost(self.stateList[i].price), self.stateList[i].price, self.stateList[i].get_inventory())
            for j in range(0, self.n_states):
                self.stationary_transition_map[i][j] = distribution.getTransitionProbability(self.stateList[i].price, self.stateList[i], self.stateList[j], self)

    def calculateStationaryProbabilities(self):
        if self.stationary_transition_map is not None:
            mc = markovChain(self.stationary_transition_map)
            mc.computePi('linear')
            for i in range(0, self.n_states):
                self.stateList[i].stationary_probability = mc.pi[i]
        else:
            raise("The Stationary Transition Probability map has not been calculated")

    def stateList(self):
        return self.stateList

    def print(self):
        for item in self.stateList:
            item.print()
    
    def is_authorized(self, s1, s2):
        return (self.authorized_transitions_matrix[s1.index,s2.index] == 1)
