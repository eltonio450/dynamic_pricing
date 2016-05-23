from collections import Set
from collections import deque
from modelization.engine.State import State
import networkx as nx
import numpy as np
import time
import copy
from discreteMarkovChain import markovChain


class Non_Stochastic_State_Map(object):
    """description of class"""
    """
    Cette classe reflete la carte des etats. 
    
   
    """

    
    def __init__(self, L=10, N=5):
        self.n_states = 0
        self.stateList = []

        dictQueues = {}
        self.generateQueues(L, N, dictQueues)
        
        for q in dictQueues[L, N]:
            self.stateList.append(State(q.popleft(), q))

        self.n_states = len(self.stateList)
        print("Generated states: "+ str(self.n_states))
        
        #optimisation
        for item in self.stateList:
            item.index = self.stateList.index(item)

        
        
        self.stationary_transition_map = None
        self.transition_list = []
        self.authorized_transitions_matrix = self.generateAuthorizedTransitionMatrix()


    """ We generate all the possible states in a set, with p=0, in order to avoid doubles. Outdated"""
    def generateStatesOldVersion(self, L, N):
        
        successors_to_be_processed = []   
        initial_queue = deque()

        """Generation of a (0,0,0,0,0) state"""
        for i in range(0,L):
            initial_queue.append(0)
        initial_state = State(N, initial_queue)

        self.stateList.append(initial_state)

        """Generation of the first successors"""
        successors_to_be_processed.extend(initial_state.guess_successors())
           

        while successors_to_be_processed:
            succ = successors_to_be_processed.pop()
            
            if not succ in self.stateList:  
                successors_to_be_processed.extend(succ.guess_successors())
                self.stateList.append(succ)
        self.n_states = len(self.stateList)
        print("Generated states: "+ str(self.n_states))
        
        #optimisation
        for item in self.stateList:
            item.index = self.stateList.index(item)

    def generateQueues(self, L, N, dict):
        if (L,N) not in dict.keys():
            if L == 1:
                dict[L,N] = [deque([N])]
            else:
                dict[L,N] = []
                for i in range(0,N+1):
                    self.generateQueues(L-1, N-i, dict)
                    for rq in dict[L-1, N-i]:
                        nrq = copy.deepcopy(rq)
                        nrq.append(i)
                        dict[L,N].append(nrq)  

                  
                



        



    def generateAuthorizedTransitionMatrix(self):
        tm = np.zeros((self.n_states, self.n_states))
        for i in range(0, self.n_states):
            for succ in self.stateList[i].guess_successors():
                i_succ = self.stateList.index(succ)
                tm[i,i_succ] = 1
                self.transition_list.append((i,i_succ))
        return tm

    def calculateStationaryTransitionMap(self, distribution):
        self.stationary_transition_map = np.zeros((self.n_states, self.n_states))
        for i in range(0, self.n_states):
            self.stateList[i].stationary_lambda = int(1000*distribution.lambda_distribution(self.stateList[i].price))/1000.
            self.stateList[i].stationary_bo_cost = distribution.calculateBackorderCost(distribution.backorder_cost(self.stateList[i].price), self.stateList[i].price, self.stateList[i].get_inventory())
            for j in range(0, self.n_states):
                self.stationary_transition_map[i][j] = distribution.calculateTransitionProbability(self.stateList[i].price, self.stateList[i], self.stateList[j], self)

    def calculateStationaryProbabilities(self):
        if self.stationary_transition_map is not None:
            mc = markovChain(self.stationary_transition_map)
            mc.computePi('linear')
            for i in range(0, self.n_states):
                self.stateList[i].stationary_probability = mc.pi[i]
        else:
            raise("The Stationary Transition Probability map has not neen calculate")

    """Functions related to nx.graph"""
    def generateGraph(self, L, N):
        successors_to_be_processed = []   
        initial_queue = deque()

        """Generation of a (0,0,0,0,0) state"""
        for i in range(0,L):
            initial_queue.append(0)
        initial_state = State(N, initial_queue)


        self.map.add_node(initial_state, label=str(initial_state))
        i = 1

        """Generation of the first successors"""
        successors_to_be_processed.extend(initial_state.guess_successors())
           
        
        while successors_to_be_processed:
            succ = successors_to_be_processed.pop()
            if not self.map.has_node(succ):  
                successors_to_be_processed.extend(succ.guess_successors())
                self.map.add_node(succ, label=str(succ))

    """this function links all the state between them, successors and predecessors"""
    def link_nodes(self):
        for node in self.map.nodes():
            for succ in node.guess_successors():
                self.map.add_edge(node,succ, sales=(node.stock - succ.stock), label=str(node.stock - succ.stock))


    
    



    def stateList(self):
        return self.stateList

    def print(self):
        for item in self.stateList:
            item.print()
    
    def is_authorized(self, s1, s2):
        return (self.authorized_transitions_matrix[s1.index,s2.index] == 1)
