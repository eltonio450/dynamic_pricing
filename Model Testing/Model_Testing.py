#!/usr/bin/env
import time
import sys

#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 
from configuration import parameters as P
from bin.engine.Non_Stochastic_State_Map import Non_Stochastic_State_Map
from bin.engine.Distribution import *

from collections import deque
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
import mdptoolbox



colors = "bgrcmykw"




if False:
    MAX_PRICE = 1100
    MIN_PRICE = 0
    BACKORDER_FIXED_COST = 200
    OBSERVATION_PRICE = 500
    OBSERVED_DEMAND = 1
    MARKET_SIZE_DEMAND_RATE = 2
    N_PRICES = 11
    N_PERIODS = 3
    N_PARTS = 3

elif False:
    MAX_PRICE = 1040
    MIN_PRICE = 0
    BACKORDER_FIXED_COST = 200
    OBSERVATION_PRICE = 500
    OBSERVED_DEMAND = 1
    MARKET_SIZE_DEMAND_RATE = 2
    N_PRICES = 26
    N_PERIODS = 4
    N_PARTS = 8

else:
    MAX_PRICE = 1030
    MIN_PRICE = 300
    BACKORDER_FIXED_COST = 200
    OBSERVATION_PRICE = 500
    OBSERVED_DEMAND = 1
    MARKET_SIZE_DEMAND_RATE = 2
    N_PRICES = 50
    N_PERIODS = 8
    N_PARTS = 6

print("Generation of the states...")
start = time.time()
G = Non_Stochastic_State_Map(N_PERIODS, N_PARTS)
end = time.time()
print("Generation time: "+ str(end - start))


#print(np.array_repr(G.authorized_transitions_matrix))


#if P.DEBUG == "SmallMatrix": 
 #   for item in (G.stateList):
  #      print(item)
    #print(np.array_repr(G.authorized_transitions_matrix))


distribution = PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST)

print("Generation of the price -> probability map...")
start = time.time()
tms = distribution.generateTransitionMatrices(MIN_PRICE,MAX_PRICE,N_PRICES,G)
end = time.time()
#print(np.array_repr(tms[1,:,:]))

print("Computation time the price -> probability map: "+ str(end - start))

print("Generation of the price -> reward map...")
start = time.time()
rms = distribution.generateRewardMatrices(MIN_PRICE,MAX_PRICE,N_PRICES,G)
end = time.time()
#print(np.array_repr(rms[1,:,:]))

print("Computation time for the reward map: "+ str(end - start))

test = mdptoolbox.mdp.PolicyIteration(tms, rms, 0.95)
start = time.time()
test.run()
end = time.time()
print("Solver: "+ str(end - start))
#print(test.V)
#print(test.policy)

# Calculate the stationary transition map when the best policy is reached.

stationary_transition_map = np.zeros((len(G.stateList),len(G.stateList)))

start = time.time()
print("Computing the stationary Markov Chain and properties...")
for i in range(0, len(G.stateList)):
    G.stateList[i].value=test.V[i]
    G.stateList[i].price = test.policy[i]*(MAX_PRICE-MIN_PRICE)/N_PRICES + MIN_PRICE
    
G.calculateStationaryTransitionMap(distribution)
G.calculateStationaryProbabilities()
stationary_transition_map = G.stationary_transition_map
end = time.time()
print("Stationary Markov Chain: "+ str(end - start))

#print(np.array_repr(stationary_transition_map))
valueList = []
priceList = []

for i in range(0, N_PARTS +1):
    valueList.append([])
    priceList.append([])

for item in G.stateList:
    valueList[item.get_inventory()].append(item.value)
    priceList[item.get_inventory()].append(item.price)
    print(item)

for i in range(0, N_PARTS +1):
    plt.scatter(valueList[i], priceList[i], c=colors[i])
plt.show()
