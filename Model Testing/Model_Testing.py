#!/usr/bin/env
import time
import sys

#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 
from configuration import parameters as P
from modelization.engine.State_Map import State_Map
from modelization.engine.Distribution import *
from modelization.Simulation import Simulation
from modelization.Analytical_Calculation import *
from modelization.visualization.Test import *
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

MAX_PRICE = 1100
MIN_PRICE = 300
BACKORDER_FIXED_COST = 10
OBSERVATION_PRICE = 500
OBSERVED_DEMAND = 0.5
MARKET_SIZE_DEMAND_RATE = 1
N_PRICES = 200
N_PERIODS = 4
N_PARTS = 5
N_SIMUS = 4
MAX_SALES = 10
GAMMA = 0.8
print((MAX_PRICE - MIN_PRICE)/N_PRICES)
PRICE_LIST = range(MIN_PRICE, MAX_PRICE, int((MAX_PRICE - MIN_PRICE)/N_PRICES))


#simu_test = Simulation()
#simu_test.setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, N_PARTS, N_PERIODS+1, MAX_SALES)
#simu_test.setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
#simu_test.run(True)
#G = simu_test.G
simu = []
maps = []
valueLists = []
priceLists = []


plt.figure(1)
for i in range(0, N_SIMUS+1):
    simu.append(Simulation())
    simu[i].setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, i, N_PERIODS+1, MAX_SALES, GAMMA)
    simu[i].setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
    simu[i].run(True)
    res = simu[i].G

    valueLists.append([])
    priceLists.append([])
    for item in res.stateList:
        valueLists[i].append(item.value)
        priceLists[i].append(item.price)
    plt.subplot(2, N_SIMUS+1, i+1)
    plt.ylim([MIN_PRICE, MAX_PRICE])
    plt.scatter(valueLists[i], priceLists[i], c=colors[i])
   



initial_states = []
H = []

for i in range(0, N_SIMUS+1):
    initial_states.append((i,))
    for k in range(0,N_PERIODS):
        initial_states[i] = initial_states[i] + (0,)
    H.append(simu[i].G.stateList[simu[i].G.stateDict[initial_states[i][1::]]].value)

for i in range(0, N_SIMUS+1):
    print("Initial State: "+ str(initial_states[i]))
    print("Value: "+ str(H[i]))

simuB = []
mapsB = []
valueListsB = []
priceListsB = []

C = []
C.append(H[0])
for i in range(1, N_SIMUS+1):
    C.append(H[i] - H[i-1])
print(C)


for i in range(0, N_SIMUS+1):
    simuB.append(Analytical_Calculation_With_Coefficients())
    simuB[i].setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, i, N_PERIODS+1, MAX_SALES, GAMMA)
    
    simuB[i].setCoefficients(C)

    simuB[i].setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
    simuB[i].run(True)
    res = simuB[i].G

    #for item in res.stateList:
        #print(item)
    valueListsB.append([])
    priceListsB.append([])
    for item in res.stateList:
        valueListsB[i].append(item.value)
        priceListsB[i].append(item.price)
    plt.subplot(2, N_SIMUS+1, N_SIMUS + i+2)
    plt.ylim([MIN_PRICE, MAX_PRICE])
    plt.scatter(valueListsB[i], priceListsB[i], c=colors[i])
   

   

    

for a in simu[N_SIMUS-1].G.stateList:
    b = simuB[N_SIMUS-1].G.stateList[simuB[N_SIMUS-1].G.stateDict[a.tuple[1::]]]
    print("State: " + str(simu[N_SIMUS-1].G.stateList[simuB[N_SIMUS-1].G.stateDict[a.tuple[1::]]].tuple) + ", V1: "+ str(round(a.value,0)) + ", V2: " + str(round(b.value,0)) + ", Diff: "+ str(round(a.value - b.value,0)))

for a in simu[N_SIMUS-1].G.stateList:
    print(a)

plt.show()










"""
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
"""
