#!/usr/bin/env
import time
import sys

#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 
from configuration import parameters as P
from modelization.engine.Non_Stochastic_State_Map import State_Map
from modelization.engine.Distribution import *

from collections import deque
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
import mdptoolbox

from sklearn import linear_model


colors = "bgrcmykw"



#WARNING: L must be >= 2

MAX_PRICE = 1000
MIN_PRICE = 100
BACKORDER_FIXED_COST = 200
OBSERVATION_PRICE = 500
OBSERVED_DEMAND = 1
MARKET_SIZE_DEMAND_RATE = 2
N_PRICES = 80
N_PERIODS = 6
N_PARTS = 6
print((MAX_PRICE - MIN_PRICE)/N_PRICES)
PRICE_LIST = range(MIN_PRICE, MAX_PRICE, int((MAX_PRICE - MIN_PRICE)/N_PRICES))

print("Generation of the states...")
start = time.time()
G = State_Map(N_PERIODS, N_PARTS)
end = time.time()
print("Generation time: "+ str(end - start))

distribution = PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, N_PARTS)

print("Generation of the price -> probability map...")
start = time.time()
distribution.generateTransitionProbabilities(PRICE_LIST)
tms = distribution.generateTransitionMatrices(PRICE_LIST,G)
end = time.time()
#print(np.array_repr(tms[1,:,:]))

print("Computation time the price -> probability map: "+ str(end - start))

print("Generation of the price -> reward map...")
start = time.time()
rms = distribution.generateRewardMatrices(PRICE_LIST,G)
end = time.time()
#print(np.array_repr(rms[1,:,:]))

print("Computation time for the reward map: "+ str(end - start))

test = mdptoolbox.mdp.PolicyIteration(tms, rms, 0.995)
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
    
#G.calculateStationaryTransitionMap(distribution)
#G.calculateStationaryProbabilities()
#stationary_transition_map = G.stationary_transition_map
end = time.time()
print("Stationary Markov Chain: "+ str(end - start))


valueList = []
priceList = []

for i in range(0, N_PARTS +1):
    valueList.append([])
    priceList.append([])

for item in G.stateList:
    valueList[item.get_inventory()].append(item.value)
    priceList[item.get_inventory()].append(item.price)


clfPrice = linear_model.LinearRegression()
clfValue = linear_model.LinearRegression()
X = []
Y = []
Z = []
for item in G.stateList:
    X.append(list(item.tuple))
    Y.append(item.price)
    Z.append(item.value)

clfPrice.fit(X,Y)
clfValue.fit(X,Z)

#print(clf.coef_)

estPrice = clfPrice.predict(X)
estValue = clfValue.predict(X)

#print(Y)
#print(est)

#print(Y-est)
for i in range(0, N_PARTS):
    #plt.scatter(valueList[i], priceList[i], c=colors[i])
    plt.scatter(estValue, estPrice)
plt.show()


