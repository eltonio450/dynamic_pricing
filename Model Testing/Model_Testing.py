#!/usr/bin/env
import time
import sys
#sys.path.append('C:\Users\Sauvage_Antoine\Documents\Visual Studio 2015\Projects\Model Testing\Model Testing\') 

from bin.engine.Non_Stochastic_State_Map import Non_Stochastic_State_Map

from collections import deque
import networkx as nx
import matplotlib as plt

G = Non_Stochastic_State_Map(10,8)


#test2.print()
nx.draw(G.map)
plt.pyplot.show()






