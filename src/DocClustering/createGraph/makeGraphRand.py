#!/usr/bin/env python3
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
import csv
import configparser
import logging
import random


Config = configparser.ConfigParser()
Config.read("../etc/config.cfg")

logging.basicConfig(filename=Config.get("Debug", "Logfile"),level=logging.INFO, format='%(asctime)s %(message)s')

nodes=100
p=0.75
b=0.2

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

for argument in sys.argv:
	if lastcomm.strip() == "-f":
		filename = argument.strip()
	if lastcomm.strip() == "-d":
		debug = True
	if lastcomm.strip() == "-m":
		maxEdgeValue = int(argument.strip())
	if lastcomm.strip() == "-o":
		outputfile = argument.strip()
	if lastcomm.strip() == "-n":
		nodes = int(argument.strip())
	lastcomm = argument
if lastcomm.strip() == "-f":
	filename = argument.strip()
if lastcomm.strip() == "-d":
	debug = True
if lastcomm.strip() == "-m":
	maxEdgeValue = int(argument.strip())
if lastcomm.strip() == "-o":
	outputfile = argument.strip()
if lastcomm.strip() == "-n":
	nodes = int(argument.strip())

start_time = time.time()


logging.debug (" ========")
logging.info ("  Starting Building Graph on "+filename)
logging.info (" ========")

#csvfile = open(standardDirectory+'export.csv', 'w')
#csvwriter = csv.writer(csvfile)
logging.info (" Creating a new random graph ...")
G=nx.fast_gnp_random_graph(nodes,p)
valueGraph=nx.Graph()

nx.set_node_attributes(G, 'color', -1)
nx.set_node_attributes(G, 'mesh',  ['',''])
nx.set_node_attributes(G, 'title', 'random')
nx.set_node_attributes(G, 'ref', 'random')
nx.set_node_attributes(G, 'uri', 'random')
nx.set_node_attributes(G, 'year', 1990)
nx.set_node_attributes(G, 'journal', 'random')
nx.set_node_attributes(G, 'end', 0)

nx.set_edge_attributes(G, 'color', 'black')
bluedEdges= 0
for u,v,a in G.edges(data=True):
	rand = random.random()
	if rand < b:
		G[u][v]["color"]="blue"
		bluedEdges += 1

# Der Graph
#G = res[0]
# Die blauen Kanten
#bluedEdges = res[1]
# gelöschte Knoten
delEdges = 0

build_time = time.time() - start_time
logging.info (" Build time was "+str(build_time)+" seconds")

start_time = time.time()

logging.info (" Now coloring graph ...")
d = nx.coloring.greedy_color(G, strategy=nx.coloring.strategy_largest_first)
if len(G) > 0:
	colorCount = d[max(d, key=lambda key: d[key])]
	nx.set_node_attributes(G, 'color', d)

color_time = time.time() - start_time
#clique = len(approx.max_clique(G))
clique = 0
clique_time = time.time()

outputpathfilename = standardDirectory+outputfile
if os.path.isabs (outputfile):
	outputpathfilename = outputfile

logging.debug (" Now writing file to ... "+outputpathfilename+".gml")
# Output vor färben
nx.write_gml(G, outputpathfilename+".gml")
#logging.debug (" Now writing file to ... "+standardDirectory+outputfile+".yaml")
#nx.write_yaml(G, standardDirectory+outputfile+".yaml")


if debug:
	logging.info ("Graph created. Number of nodes: " + str(G.number_of_nodes())+ ", number edges: "+ str(G.number_of_edges()))
	logging.debug (" Deleted nodes: "+str(delEdges))
	logging.info (" Blue edges: "+str(bluedEdges))
	logging.info (" Build time: \t " + str((build_time)))	

output = []
output.append (build_time)
output.append (G.number_of_nodes())
output.append (G.number_of_edges())
output.append (bluedEdges)

print (output)





