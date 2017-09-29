#!/usr/bin/env python3.6
import sys
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
logging.info ("  Starting PS-Clustering Algorithm with trategy_saturation_largest_first on "+filename)
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

d = nx.coloring.greedy_color(G, strategy=nx.coloring.strategy_saturation_largest_first)  #strategy_independent_set
#d = nx.get_node_attributes(G, 'color')
colorCount = d[max(d, key=lambda key: d[key])]

build_time = time.time() - start_time
logging.info (" => Coloring time: "+str(build_time))
start_time = time.time()


start_time = time.time()
# valueGraph und Farbenliste bauen
valueGraph = buildValueGraph (G, d , logging, normalize=doNormalization)
outputpathfilename = standardDirectory+outputfile
if os.path.isabs (outputfile):
	outputpathfilename = outputfile
outputpathfilename = outputpathfilename.split(".")[0]
logging.debug ("  ... saving weightes Value Graph at "+outputpathfilename+'coloredWithValue.gml')
nx.write_gml(valueGraph, outputpathfilename+'coloredWithValue.gml')
# Build a colorlist and sort min first
colorList = []
for i in range(0,colorCount):
		countC = countColor (G,i);
		colorList.append ( [i, countC] )
colorList = sorted(colorList,key=itemgetter(1))

build_time = time.time() - start_time
logging.info (" => Build weighted graph time: "+str(build_time))
start_time = time.time()

#G = addBlueEdges (G, createEdgePercent, createBlueEdgePercent, createBluedEdges, data)

# For all nodes
countNodesEliminated = 0;
listConnections = []

#colorCount = d[max(d, key=lambda key: d[key])]
minYear = 3000
maxYear = 0
for i in range(0,colorCount):#
	yearc = getClusterYearsList (G,i)
	for year in yearc:#
		if year[0]==0:
			continue
		if year[0]>maxYear:
			maxYear = year[0]
		if year[0]<minYear:
			minYear = year[0]

for node in G.nodes():
	G.node[node]['year']=int(G.node[node]['year'])

#logging.info (" (1) : \t\t "+str(valueGraph.number_of_nodes()-1))
for colorSet in colorList:
	# Get a list of nodes with that color
	tmpNodeList = list(n for n,d in G.nodes_iter(data=True) if d['color']==colorSet[0])	
	#print (" Color count before: "+str(countColor(G, colorSet[0])))
	# Now iterate over these nodes
	for i in range(0,len(tmpNodeList)):
		# catch that node
		node = tmpNodeList[i]
		# check if this node is not already an end-point!
		if G.node[node]["end"]==0:
			colors = []
			# for all neighbours
			for nb in G.neighbors(node):
				# is edge blue?
				if G[node][nb]["color"] == "blue":
					# is node not yet excluded from stable sets? 
					if (G.node[nb]["color"] >= 0):
						# Nodes are not in the same stable sets
						if (G.node[nb]["color"] != G.node[node]["color"]):
							colors.append (G.node[nb]["color"])
			# Now remove all double entries
			uniqueList = unique(colors)
			# check if "node" has at last two blue neighbours in different stable sets
			if len(uniqueList) >= 2:
				# Node is excluded from stable sets (color -1)
				G.node[node]["color"] = -1;
				countNodesEliminated += 1
				# now we see, that this node connects all stable sets connected with blue edges:
				for i in range(0,len(uniqueList)) :
					for j in range (i+1, len(uniqueList)):
						newYear = "y"+str(G.node[node]["year"])
						#print (" Year: "+newYear + " from "+ str(G.node[node]["year"]))
						if str(uniqueList[i]-1) in valueGraph.nodes() and str(str(uniqueList[j]-1)) in valueGraph.nodes():
							if valueGraph.has_edge(str(uniqueList[i]-1),str(uniqueList[j]-1)):
								valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]["value"]+=1
								if  "y"+str(G.node[node]["year"]) in valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]:
									# Jahr existiert
									valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]["y"+str(G.node[node]["year"])] += 1
								else:
									valueGraph.add_edge (str(uniqueList[i]-1) , str(uniqueList[j]-1), {newYear : 1})
							else:
								valueGraph.add_edge(str(uniqueList[i]-1),str(uniqueList[j]-1), value=1)
								valueGraph.add_edge (str(uniqueList[i]-1) , str(uniqueList[j]-1), {newYear : 1})
							for yearsum in range(minYear, G.node[node]["year"]-1):
								if  "s"+str(yearsum) not in valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]:
									newYear2 = "s"+str(yearsum)
									valueGraph.add_edge (str(uniqueList[i]-1) , str(uniqueList[j]-1), {newYear2 : 0})
							for yearsum in range(G.node[node]["year"], maxYear):
								if  "s"+str(yearsum) in valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]:
									valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]["s"+str(yearsum)] += 1
								else:
									newYear2 = "s"+str(yearsum)
									valueGraph.add_edge (str(uniqueList[i]-1) , str(uniqueList[j]-1), {newYear2 : 1})
						#else:
						#	logging.warn (" Error, nodes do not exist. ")
						#valueGraph[str(uniqueList[i]-1)][str(uniqueList[j]-1)]["y"+str(G.node[node]["year"])] += 1
				# mark all nodes as end-nodes
				for nb in G.neighbors(node):
					# is edge blue?
					if G[node][nb]["color"] == "blue":
						# is node not yet excluded from stable sets? 
						if (G.node[nb]["color"] >= 0):
							G.node[nb]["end"] = 1
	#print (" Color count after: "+str(countColor(G, colorSet[0])))
#print (str(valueGraph.number_of_nodes()))
#logging.info (" (2) : \t\t "+str(valueGraph.number_of_nodes()-1))
if "-1" in valueGraph.nodes():
	valueGraph.remove_node("-1")
if -1 in valueGraph.nodes():
	valueGraph.remove_node(-1)
#logging.info (" (3) : \t\t "+str(valueGraph.number_of_nodes()-1))
count = 15

for node in valueGraph.nodes():	
	newValue = countColor (G, int(node))
	if newValue == 0:
		#print ("Removing node "+str(node)+" with "+str(valueGraph.node[node]["text"]))
		valueGraph.remove_node(node)
	else:
		valueGraph.node[node]["value"]=newValue
		terms = getClusterName(G,node,count);
		journals = getClusterJournals (G,node,count)
		yearc = getClusterYearsList (G,node,count)
		valueGraph.node[node]["text"]=terms
		valueGraph.node[node]["journal"]=journals
		yearc.sort(key=lambda tup: tup[0]) 
		#print (str(yearc))
		summe = 0
		#print ("New Sum")
		#print (str(minYear) +" -- "+str(maxYear))
		#print (yearc)
		for year in range(minYear, maxYear):
			addValue = 0
			#print ("Looking for year "+str(year))
			for years in yearc:
				if years[0]==0:
					continue
				if years[0] == year:
					#print (str(years[0]) +" == "+str(year))
					addValue = years[1]
			#print (" "+str(year))
			valueGraph.node[node]["y"+str(year)] = addValue
			valueGraph.node[node]["s"+str(year)] = addValue + summe
			summe += addValue	
		#csvwriter.writerow ([''])
		#csvwriter.writerow (["Node", int(node), "Nodes:", newValue])
		#csvwriter.writerow (getClusterName (G, int(node), maxCount=-1, separator=";").split(";")) 
		#csvwriter.writerow ([''])
		#nodeList = (n for n in G if G.node[n]['color']==int(node))
		#for nodeG in nodeList:
		#	csvwriter.writerow ([ G.node[nodeG]['title'], G.node[nodeG]['ref'], G.node[nodeG]['uri']])
if os.path.isabs (outputfile):
	outputpathfilename = outputfile
outputpathfilename = outputpathfilename.split(".")[0]
logging.debug ("  ... saving PS Value Graph at "+outputpathfilename+'coloredWithValuePS.gml')
nx.write_gml(valueGraph, outputpathfilename+'coloredWithValuePS.gml')
#logging.info (" (4) : \t\t "+str(valueGraph.number_of_nodes()-1))
build_time = time.time() - start_time
logging.info (" => PS time: "+str(build_time))
start_time = time.time()

ps_time = build_time

#csvwriter.writerows (sorted(oldList.items(), key=operator.itemgetter(1), reverse=True)) 

logging.debug ("  ... saving Network RB at  "+outputpathfilename+'network_rb.gml')
# Output nach neu färben
nx.write_gml(G, outputpathfilename+'network_rb.gml')

numbers = getMeshTermNumber (G);
#print ( sorted(numbers.items(), key=operator.itemgetter(1)))

# Positions
pos=nx.spring_layout(valueGraph,weight='value')

logging.warn (pos)

xi = np.linspace(0,10)
yi = np.linspace(0,10)
Z = []
A = []
for k in pos:
	A.append (k)
	Z.append (int(valueGraph.node[k]['value']))
X = []
Y = []
for item in list(pos.values()):
	X.append(item[0]*10)
	Y.append(item[1]*10)
List = []
List.append (A)
List.append (X)
List.append (Y)
List.append (Z)
with open(outputpathfilename+'grid.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerows(List)

#plotx,ploty, = np.meshgrid(np.linspace(np.min(X),np.max(X),10),\
#                           np.linspace(np.min(Y),np.max(Y),10))
#plotz = interp.griddata((X,Y),Z,(plotx,ploty),method='cubic')

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.plot_surface(plotx,ploty,plotz,cstride=1,rstride=1,cmap='viridis')
#fig.savefig("test.png")

# Export 
data = json_graph.node_link_data(valueGraph)
with open(outputpathfilename+'coloredWithValuePS.json', 'w') as outfile:
    json.dump(data, outfile)

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
	logging.info (" Farben: \t\t "+str(colorCount))
	logging.info (" minMPS: \t\t "+str(valueGraph.number_of_nodes()-1))
	#lower = colorCount - math.floor (bluedEdges / 2)
	#if lower < 2:
	#	lower = 2
	#logging.debug (" l_b: \t \t\t "+str(lower))
	#print (" Cliquenzahl:  "+ str(clique) )
	logging.info (" Eliminated nodes: \t "+str(countNodesEliminated))
	#print (" Clique time: " + str((clique_time - color_time)))
	#print (G.edges())
#nx.set_node_attributes(G, 'label', {0: "0", 1: "1"})

output = []
output.append (ps_time)
output.append (colorCount)
output.append (valueGraph.number_of_nodes())
output.append (countNodesEliminated)

print (output)


