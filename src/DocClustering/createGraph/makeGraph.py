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


Config = configparser.ConfigParser()
Config.read("../etc/config.cfg")

logging.basicConfig(filename=Config.get("Debug", "Logfile"),level=logging.DEBUG, format='%(asctime)s %(message)s')

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
		filename = argument.strip();
	if lastcomm.strip() == "-d":
		debug = True
	if lastcomm.strip() == "-m":
		maxEdgeValue = int(argument.strip());
	if lastcomm.strip() == "-o":
		outputfile = argument.strip();
	if lastcomm.strip() == "-e":
		createEdgePercent = int(argument.strip())
	if lastcomm.strip() == "-b":
		createBlueEdgePercent = int(argument.strip())
	lastcomm = argument
if lastcomm.strip() == "-f":
	filename = argument.strip();
if lastcomm.strip() == "-d":
	debug = True
if lastcomm.strip() == "-m":
	maxEdgeValue = int(argument.strip());
if lastcomm.strip() == "-o":
	outputfile = argument.strip();
if lastcomm.strip() == "-e":
	createEdgePercent = int(argument.strip())
if lastcomm.strip() == "-b":
	createBlueEdgePercent = int(argument.strip())

start_time = time.time()

if filename == "":
	logging.error ("No file name given.")
	exit()

logging.debug (" ========")
logging.debug ("  Starting Building Graph on "+filename)
logging.debug (" ========")

#csvfile = open(standardDirectory+'export.csv', 'w')
#csvwriter = csv.writer(csvfile)
logging.info (" Creating a new graph ...")
G=nx.Graph()
valueGraph=nx.Graph()

logging.info (" Loading json file ...")
with open(filename) as data_file:    
	data = json.load(data_file)

logging.info (" Now building the graph ...")
res = buildGraph (createEdgePercent, createBlueEdgePercent, createBluedEdges, data);

# Der Graph
G = res[0]
# Die blauen Kanten
bluedEdges = res[1]
# gelöschte Knoten
delEdges = res[2]

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

logging.debug (" Now writing file to ... "+outputpathfilename.split(".")[0]+".gml")
# Output vor färben
nx.write_gml(G, outputpathfilename.split(".")[0]+".gml")
#logging.debug (" Now writing file to ... "+standardDirectory+outputfile+".yaml")
#nx.write_yaml(G, standardDirectory+outputfile+".yaml")


if debug:
	logging.debug ("Graph created. Number of nodes: " + str(G.number_of_nodes())+ ", number edges: "+ str(G.number_of_edges()))
	logging.debug (" Deleted nodes: "+str(delEdges))
	logging.debug (" Blue edges: "+str(bluedEdges))
	logging.debug (" Build time: \t " + str((build_time)))	

output = []
output.append (build_time)
output.append (G.number_of_nodes())
output.append (G.number_of_edges())
output.append (bluedEdges)

print (output)







