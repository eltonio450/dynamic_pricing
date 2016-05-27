#!/usr/bin/env
import time
import sys

#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 
from configuration import parameters as P
from modelization.engine.State_Map import State_Map
from modelization.engine.Distribution import *
from modelization.Simulation import Simulation
from collections import deque
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
import mdptoolbox

from sklearn import linear_model
from sklearn.metrics import r2_score


colors = "bgrcmykw"



#WARNING: L must be >= 2

MAX_PRICE = 1000
MIN_PRICE = 100
BACKORDER_FIXED_COST = 10
OBSERVATION_PRICE = 500
OBSERVED_DEMAND = 1
MARKET_SIZE_DEMAND_RATE = 2
N_PRICES = 80
N_PERIODS = 5
N_PARTS = 8
print((MAX_PRICE - MIN_PRICE)/N_PRICES)
PRICE_LIST = range(MIN_PRICE, MAX_PRICE, int((MAX_PRICE - MIN_PRICE)/N_PRICES))


simu_test = Simulation()
simu_test.setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, N_PERIODS+1, N_PARTS)
simu_test.setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, N_PARTS))
simu_test.run()

G = simu_test.G
print("Coucou")

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

test = mdptoolbox.mdp.PolicyIteration(tms, rms, 0.99)
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


#creation of the lists for the different inventory levels
for i in range(0, N_PARTS +1):
    valueList.append([])
    priceList.append([])

#lists fill in
for item in G.stateList:
    valueList[item.get_inventory()].append(item.value)
    priceList[item.get_inventory()].append(item.price)


clfPrice = linear_model.LinearRegression()
clfValue = linear_model.LinearRegression()
X = []
Y = []
Z = []
for item in G.stateList:
    X.append(item.tuple)
    Y.append(item.price)
    Z.append(item.value)

clfPrice.fit(X,Y)
clfValue.fit(X,Z)

#print(clf.coef_)

estPrice = clfPrice.predict(X)
estValue = clfValue.predict(X)

print("Value:")
print("Coeffs: "+ str(clfValue.coef_ - min(clfValue.coef_)))
print("Intercept: "+ str(clfValue.intercept_))
print("R2: "+ str(r2_score(Z,estValue)))
print("Price:")
print("Coeffs: " + str(clfPrice.coef_ - min(clfPrice.coef_)))
print("R2: "+ str(r2_score(Y,estPrice)))
print("Intercept: "+ str(clfPrice.intercept_))


valueListEst = []
priceListEst = []

#creation of the lists for the different inventory levels for the simulation
for i in range(0, N_PARTS +1):
    valueListEst.append([])
    priceListEst.append([])

for item in X:
    valueListEst[item[0]].append(estValue[X.index(item)])
    priceListEst[item[0]].append(estPrice[X.index(item)])


#print(Y-est)
plt.figure(1)
plt.subplot(121)
axes = plt.gca()
for i in range(0, N_PARTS):
    axes.set_ylim([400, 1100])
    plt.scatter(valueList[i], priceList[i], c=colors[i])
   


plt.figure(1)

plt.subplot(122)
axes = plt.gca()
for i in range(0, N_PARTS):
    axes.set_ylim([400, 1100])
    plt.scatter(valueListEst[i], priceListEst[i], c=colors[i])
plt.show()

