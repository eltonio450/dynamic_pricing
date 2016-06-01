#!/usr/bin/env
import time
import sys

#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 
from configuration import parameters as P
from modelization.engine.State_Map import State_Map
from modelization.engine.Distribution import *
from modelization.Simulation import Simulation
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
OBSERVED_DEMAND = 1
MARKET_SIZE_DEMAND_RATE = 2
N_PRICES = 200
N_PERIODS = 4
N_PARTS = 4
MAX_SALES = 10
print((MAX_PRICE - MIN_PRICE)/N_PRICES)
PRICE_LIST = range(MIN_PRICE, MAX_PRICE, int((MAX_PRICE - MIN_PRICE)/N_PRICES))


simu_test = Simulation()
simu_test.setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, N_PARTS, N_PERIODS+1, MAX_SALES)
simu_test.setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
simu_test.run(True)
G = simu_test.G

simu_test2 = Simulation()
simu_test2.setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, N_PARTS+3, N_PERIODS+1, MAX_SALES)
simu_test2.setDistribution(PoissonWithLinearLambda(MARKET_SIZE_DEMAND_RATE, OBSERVATION_PRICE, OBSERVED_DEMAND, BACKORDER_FIXED_COST, MAX_SALES))
simu_test2.run(True)
G2 = simu_test2.G

simu_test_bernoulli = Simulation()
simu_test_bernoulli.setParameters(MIN_PRICE, MAX_PRICE, N_PRICES, N_PARTS, N_PERIODS+1, 1)
simu_test_bernoulli.setDistribution(BernoulliWithLinearParameter(500, 0.1, 0.3))
#simu_test_bernoulli.run(True)
#G = simu_test_bernoulli.G

#print("Test Start:")
#test_domination = TestLemmaDomination(simu_test)
#test_domination.run()
#print("Test end")




valueList = []
priceList = []

valueList2 = []
priceList2 = []


#creation of the lists for the different inventory levels
for i in range(0, N_PARTS +1):
    valueList.append([])
    priceList.append([])

for i in range(0, N_PARTS +4):
    valueList2.append([])
    priceList2.append([])

#lists fill in
for item in G.stateList:
    valueList[item.get_inventory()].append(item.value)
    priceList[item.get_inventory()].append(item.price)

for item in G2.stateList:
    valueList2[item.get_inventory()].append(item.value)
    priceList2[item.get_inventory()].append(item.price)



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
    axes.set_ylim([100, 1000])
    plt.scatter(valueList[i], priceList[i], c=colors[i])
   


plt.figure(1)

plt.subplot(122)
axes = plt.gca()
for i in range(0, N_PARTS):
    axes.set_ylim([100, 1000])
    plt.scatter(valueList2[i], priceList2[i], c=colors[i])
plt.show()

