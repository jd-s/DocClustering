#!/usr/bin/env python3.6
import sys
import random
import networkx as nx
import math
import decimal
from pulp import *
from operator import itemgetter
import os
import json
import networkx as nx
import math
from networkx.algorithms import approximation as approx
import time
from itertools import groupby as g
from operator import itemgetter
from graphFunctions import *
import scipy.interpolate as interp
import csv
import configparser
import logging
#from networkx.readwrite import d3_js
from networkx.readwrite import json_graph
from mpl_toolkits.mplot3d import Axes3D
import scipy
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from scipy.interpolate import griddata

#import mpld3
#mpld3.enable_notebook()
#from mpld3 import plugins
#import matplotlib.pyplot as plt


Config = configparser.ConfigParser()
Config.read("../etc/config.cfg")

logging.basicConfig(filename=Config.get("Debug", "Logfile"),level=logging.INFO, format='%(asctime)s %(message)s')

debug = Config.getboolean("Debug", "DebugInfo")
standardDirectory = Config.get("Path", "StandardDirectory")
filename = ""
lastcomm = ""
outputfile = ""
maxEdgeValue = Config.getint("Graph", "maxEdgeValue");
# Values for Edge creation
createEdgePercent = Config.getint("Graph", "createEdgePercent") 			# Bis zu einem Wert von 30% NICHT ähnlich
createBlueEdgePercent = Config.getint("Graph", "createBlueEdgePercent") 	# Bis zu einem Wert von 50% ETWAS ähnlich
createBluedEdges = True
doNormalization = True
for argument in sys.argv:
	if lastcomm.strip() == "-f":
		filename = argument.strip();
	if lastcomm.strip() == "-d":
		debug = True
	if lastcomm.strip() == "-m":
		maxEdgeValue = int(argument.strip());
	if lastcomm.strip() == "-o":
		outputfile = argument.strip();
	lastcomm = argument
if lastcomm.strip() == "-f":
	filename = argument.strip();
if lastcomm.strip() == "-d":
	debug = True
if lastcomm.strip() == "-m":
	maxEdgeValue = int(argument.strip());
if lastcomm.strip() == "-o":
	outputfile = argument.strip();

logging.debug (" ========")
logging.info ("  Starting PS-Clustering Algorithm with IP on "+filename)
logging.info (" ========")
start_time = time.time()

if filename == "":
	logging.error ("No file name given.")
	exit()

G=nx.Graph()
logging.info (" ... now reading graph at "+filename)
G = nx.read_gml(filename)

if len(G) == 0:
	logging.error (" ... Graph is empty! Exiting!")
	exit()
build_time = time.time() - start_time
logging.info (" => Build time: "+str(build_time))

start_time = time.time()


start_time = time.time()
# valueGraph und Farbenliste bauen




# Now building the IP

# New instance
lp_prob = pulp.LpProblem("DC", pulp.LpMinimize)
# Die Farben
y = pulp.LpVariable.dicts("y", range(0,G.number_of_nodes()+1), 0, 1, LpInteger)
# Die x_ij
x = []
x = [pulp.LpVariable.dicts("x" + str(y), range(0,G.number_of_nodes()+1), 0, 1, LpInteger) for y in range(0,G.number_of_nodes()+1)]
k = pulp.LpVariable("k",0,1000,LpInteger)

label = "Min_Funk"
do_min = None
for i in range(1, G.number_of_nodes()+1):
	do_min += y[i]
min_condition = do_min == k
lp_prob += min_condition, label
lp_prob += k, "Objective Function"
# Zeile 1
for i in range(1, G.number_of_nodes()):
	label = "Constraint1_for_" + str(i) + ","
	dot_x_ij = None
	for j in range(0, G.number_of_nodes()+1):
		# print ("Für Ziel "+str(i)+" gibt es "+str(S[i])+" Blockungen")
		dot_x_ij += x[i][j]
	condition = dot_x_ij == 1
	# print (str(condition))
	lp_prob += condition, label

# Zeile 2
for i in range(1, G.number_of_nodes()+1):
	for j in range(1, G.number_of_nodes()+1):
		label = "Constraint2_for_" + str(i) + ","+str(j)
		dot_x_ij = None
		# print ("Für Ziel "+str(i)+" gibt es "+str(S[i])+" Blockungen")
		dot_x_ij += x[i][j]
		dot_x_ij -= y[j]
		condition = dot_x_ij <= 0
		# print (str(condition))
		lp_prob += condition, label
# Zeile 3
for i in range(1, G.number_of_nodes()+1):
	for j in range(1, G.number_of_nodes()+1):
		if G.nodes()[i-1] in G.neighbors(G.nodes()[j-1]):
			if G[G.nodes()[i-1]][G.nodes()[j-1]]["color"] != "blue":
				for k in range(1, G.number_of_nodes()+1) :
					label = "Constraint_for_nodes_" + str(i) + ","+str(j)+",col"+str(k)
					dot_x_ij = None
					dot_x_ij += x[i][k]
					dot_x_ij += x[j][k]
					condition = dot_x_ij <= 1
					lp_prob += condition, label
#Zeile 4
# --> Ignorieren, da alle Knoten Blau

# Zeile 5
for i in range(1, G.number_of_nodes()+1):
	for j in range(1, G.number_of_nodes()+1):
		label = "Constraint5_for_" + str(i) + ","+str(j)
		dot_x_ij = None
		# print ("Für Ziel "+str(i)+" gibt es "+str(S[i])+" Blockungen")
		dot_x_ij += x[i][j]
		condition = dot_x_ij >= 0
		# print (str(condition))
		lp_prob += condition, label

# Zeile 6
for i in range(1, G.number_of_nodes()+1):
	label = "Constraint6_for_y" + str(i) + ","
	dot_x_ij = None
	# print ("Für Ziel "+str(i)+" gibt es "+str(S[i])+" Blockungen")
	dot_x_ij += y[i]
	condition = dot_x_ij <= 1
	# print (str(condition))
	lp_prob += condition, label
bluenodelist = []
# zeile 7
# Find all triples of nodes...
for i in G.nodes():
	for v in G.nodes():
		for j in G.nodes():
			if i != v and v != j and i!=j:
				#print (str(i)+"-"+str(v)+"-"+str(j))
				if i in G.neighbors(v) and j in G.neighbors(v):
					if G[i][v]["color"] == "blue" and G[v][j]["color"] == "blue":
						# Tripel gefunden
						#x_{i,k}+x_{j,k}-2+x_{v,0}&\leq 0    (i,v,j)\in T, \forall k=1,...,n
						for k in range(1, G.number_of_nodes()):
							bluenodelist.append (v)
							label = "Constraint7_for_"+str(i)+","+str(v)+","+str(j)+","+str(k)
							dot_x_ij = None
							dot_x_ij += x[i][k]
							dot_x_ij += x[j][k]
							dot_x_ij -= 2
							dot_x_ij += x[v][0]
							condition = dot_x_ij <= 0
							lp_prob += condition, label
							label = "Constraint8_for_" + str(i) + "," + str(v) + "," + str(j) + "," + str(k)
							dot_x_ij = None
							dot_x_ij += x[i][0]
							dot_x_ij += x[j][0]
							dot_x_ij += x[v][0]
							condition = dot_x_ij <= 1
							lp_prob += condition, label
for i in G.nodes():
	if i in bluenodelist:
		# darf in 0
		label = "Constraint10COL_for_" + str(i)
		dot_x_ij = None
		dot_x_ij += x[i][0]
		condition = dot_x_ij >= 0
		lp_prob += condition, label
	else:
		#darf nicht in 0
		label = "Constraint10COL_for_" + str(i)
		dot_x_ij = None
		dot_x_ij += x[i][0]
		condition = dot_x_ij <= 0
		lp_prob += condition, label
#lp_prob += min_condition, "Objective Function"

lp_prob.writeLP("MinmaxProblem.lp")  # optional
lp_prob.solve()

varsdict = {}
for v in lp_prob.variables():
	varsdict[v.name] = v.varValue
	#print (v.name + ":"+str(v.varValue))

#print (varsdict)
minResult = pulp.value(varsdict["k"])

build_time = time.time() - start_time
logging.info (" => PS time: "+str(build_time))
start_time = time.time()

ps_time = build_time

#csvwriter.writerows (sorted(oldList.items(), key=operator.itemgetter(1), reverse=True)) 




#print ( sorted(numbers.items(), key=operator.itemgetter(1)))


#plotx,ploty, = np.meshgrid(np.linspace(np.min(X),np.max(X),10),\
#                           np.linspace(np.min(Y),np.max(Y),10))
#plotz = interp.griddata((X,Y),Z,(plotx,ploty),method='cubic')

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.plot_surface(plotx,ploty,plotz,cstride=1,rstride=1,cmap='viridis')
#fig.savefig("test.png")



#fig, axs = plt.subplots(1, 1, figsize=(10, 10))
#ax = axs
#pos = None
#mpld3.plugins.connect(fig,  NetworkXD3ForceLayout(valueGraph,
#                                                  pos,
#                                                  ax,
#                                                  gravity=.5,
#                                                  link_distance=20,
#                                                  charge=-600,
#                                                  friction=1
#                                                 )
#                     )


if debug:
	#logging.debug ("Graph created. Number of nodes: " + str(G.number_of_nodes())+ ", number edges: "+ str(G.number_of_edges()))
	#logging.debug (" Blue edges: "+str(bluedEdges))
	#print (" Black edges: "+ str(countBlack) + ", Blued edges: "+ str(countBlue) +", lost edged: "+str(countLost))
	#logging.debug (" Build time: \t " + str((build_time)))
	#logging.debug (" Color time: \t " + str((color_time )))
	logging.info (" PS time:  \t " + str((ps_time )))
	
	
	logging.info (" ========")
	logging.info (" Farben: \t\t 0")
	logging.info (" minMPS: \t\t "+str(minResult))
	#lower = colorCount - math.floor (bluedEdges / 2)
	#if lower < 2:
	#	lower = 2
	#logging.debug (" l_b: \t \t\t "+str(lower))
	#print (" Cliquenzahl:  "+ str(clique) )
	#logging.info (" Eliminated nodes: \t "+str(countNodesEliminated))
	#print (" Clique time: " + str((clique_time - color_time)))
	#print (G.edges())
#nx.set_node_attributes(G, 'label', {0: "0", 1: "1"})

output = []
output.append (ps_time)
output.append (0)
output.append (minResult)
output.append (0)

print (output)


