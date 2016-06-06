#!/usr/bin/env
import time
import sys

#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 
from modelization.engine.State_Map import State_Map
from modelization.engine.Distribution import *
from modelization.Simulation import Simulation
from modelization.Analytical_Calculation_All_States import *
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
N_PRICES = 100
N_PERIODS = 4
N_PARTS = 5
N_SIMUS = 3
MAX_SALES = 10
GAMMA = 0.95
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

approx_initiale_constante = {}
approx_initiale_exp = {}

plt.figure(1)
for i in range(0, N_SIMUS+1):
    print("Exact simulation " + str(i) + "...")
    simu.append(Simulation())
    simu[i].setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, i, N_PERIODS+1, MAX_SALES, GAMMA)
    simu[i].setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
    simu[i].run(False)
    res = simu[i].G

    valueLists.append([])
    priceLists.append([])
    for item in res.stateList:
        valueLists[i].append(item.value)
        priceLists[i].append(item.price)
    plt.subplot(4, N_SIMUS+1, i+1)
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



plt.figure(1)
for i in range(0, N_SIMUS+1):
    print("Exponential approximation " + str(i) + "...")
    simuB.append(Exponential_Approximation())
    simuB[i].setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, i, N_PERIODS+1, MAX_SALES, GAMMA)
    simuB[i].setCoefficients(C)
    simuB[i].setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
    simuB[i].generateStateMap()
    simuB[i].run(False)
    res = simuB[i].G

    approx_initiale_exp[i] = {}
    approx_initiale_constante[i] = {}

    valueListsB.append([])
    priceListsB.append([])
    for item in res.stateList:
        approx_initiale_exp[i][item.index] = item.value
        approx_initiale_constante[i][item.index] = 0
        valueListsB[i].append(item.value)
        priceListsB[i].append(item.price)
    plt.subplot(4, N_SIMUS+1, N_SIMUS + i+2)
    plt.ylim([MIN_PRICE, MAX_PRICE])
    plt.scatter(valueListsB[i], priceListsB[i], c=colors[i])
   
#Generation des approximations

print("Debut de la reapproximation...")
simuC = []
mapsC = []
valueListsC = []
priceListsC = []
for i in range(0, N_SIMUS+1):
    print("Reapproximation " + str(i) + "...")
    simuC.append(Continuous_Approximation())
    simuC[i].setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, i, N_PERIODS+1, MAX_SALES, GAMMA)
    simuC[i].setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
    simuC[i].generateStateMap()
    simuC[i].setDepth(3)
    simuC[i].setApproximateValues(approx_initiale_exp[i])
    simuC[i].run(True)

    res = simuC[i].G
    valueListsC.append([])
    priceListsC.append([])
    for item in res.stateList:
        valueListsC[i].append(item.value)
        priceListsC[i].append(item.price)
    plt.subplot(4, N_SIMUS+1, 2*N_SIMUS + 2 + i + 1)
    plt.ylim([MIN_PRICE, MAX_PRICE])
    plt.scatter(valueListsC[i], priceListsC[i], c=colors[i])
    

print("Debut de la reapproximation a partir de V=0...")
simuD = []
mapsD = []
valueListsD = []
priceListsD = []
for i in range(0, N_SIMUS+1):
    print("Reapproximation " + str(i) + "...")
    simuD.append(Continuous_Approximation())
    simuD[i].setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, i, N_PERIODS+1, MAX_SALES, GAMMA)
    simuD[i].setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
    simuD[i].generateStateMap()
    simuD[i].setDepth(3)
    simuD[i].setApproximateValues(approx_initiale_constante[i])
    simuD[i].run(True)

    res = simuD[i].G
    valueListsD.append([])
    priceListsD.append([])
    for item in res.stateList:
        valueListsD[i].append(item.value)
        priceListsD[i].append(item.price)
    plt.subplot(4, N_SIMUS+1, 3*N_SIMUS + 3 + i + 1)
    plt.ylim([MIN_PRICE, MAX_PRICE])
    plt.scatter(valueListsD[i], priceListsD[i], c=colors[i])
    

for a in simu[N_SIMUS].G.stateList:
    b = simuB[N_SIMUS].G.stateList[simuB[N_SIMUS].G.stateDict[a.tuple[1::]]]
    c = simuC[N_SIMUS].G.stateList[simuC[N_SIMUS].G.stateDict[a.tuple[1::]]]
    print("State: " + str(simu[N_SIMUS].G.stateList[simuB[N_SIMUS].G.stateDict[a.tuple[1::]]].tuple) + ", V1: "+ str(round(a.value,0)) + ", V2: " + str(round(b.value,0)) + ", V3: " + str(round(c.value,0)) + ", Diff1: "+ str(round(a.value - b.value,0))+ ", Diff2: "+ str(round(a.value - c.value,0)))



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
