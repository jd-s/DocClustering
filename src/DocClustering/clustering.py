#!/usr/bin/env python3.6
import sys
import subprocess
import csv
import os
from optparse import OptionParser
import configparser
import logging


path = os.getcwd()


parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",default="", action="store", type="string",
                  help="The input file in JSON Format", metavar="filename")
parser.add_option("-d", "--directory", dest="directory",default="", action="store", type="string",
                  help="Use a different standard directory", metavar="directory")
parser.add_option("-a", "--algorithm", action="store", type="string",
                  dest="heuristic", default="SLF",
                  help="Define the heuristic to use\n SLF, GIS, CLIQUE, IP")
parser.add_option("-r", "--random", default=False,  help="Use a random instance", action="store_true", dest="random")
parser.add_option("-o", "--only_build", default=False,  help="Only build the graph and do not run graph partition", action="store_true", dest="onlybuild")
parser.add_option("-n", "--nodes", default=100,  help="Node count for random instances, default 100",
				  dest="nodes",  action="store", type="int")
parser.add_option("-e", "--edgesPercent", default=-1,  help="Percent value until documents are not similar 0<e<b<100",
				  dest="edgesPercent",  action="store", type="int")
parser.add_option("-b", "--blueEdgesPercent", default=-1,  help="Percent value until documents are blue  0<e<b<100",
				  dest="edgesBluePercent",  action="store", type="int")
(options, args) = parser.parse_args()

# Create random graph
number = 2					# Number of tests to run
nodes = options.nodes		# Nodes for instances, default 100

Config = configparser.ConfigParser()
Config.read("../etc/config.cfg")

logging.basicConfig(filename=Config.get("Debug", "Logfile"),level=logging.DEBUG, format='%(asctime)s %(message)s')

debug = Config.getboolean("Debug", "DebugInfo")
standardDirectory = options.directory
if options.directory == "":
	standardDirectory = Config.get("Path", "StandardDirectory")
maxEdgeValue = Config.getint("Graph", "maxEdgeValue");
# Values for Edge creation
createEdgePercent = Config.getint("Graph", "createEdgePercent") 			# Bis zu einem Wert von 30% NICHT ähnlich
createBlueEdgePercent = Config.getint("Graph", "createBlueEdgePercent") 	# Bis zu einem Wert von 50% ETWAS ähnlich


outputList = []
#for i in range(0,number):
head, tail = os.path.split(options.filename)

tmp = []
tmp.append (1)

if options.heuristic != "CLIQUE" and options.heuristic != "SLF" and options.heuristic != "GIS" and options.heuristic != "IP":
	print (" No valid heuristic given. Valid values are: CLIQUE, SLF, GIS ")
	exit(-1)

if options.filename != "" and options.random == False:
	params = [path + "/createGraph/makeGraph.py", "-f", str(options.filename), "-d", "-o", standardDirectory+str("graph_"+tail)]
	if options.edgesBluePercent >= 0:
		params.append ("-b")
		params.append (str(options.edgesBluePercent))
	if options.edgesPercent >= 0:
		params.append("-e")
		params.append(str(options.edgesPercent))
	output = subprocess.Popen(params,
							  stdout=subprocess.PIPE).communicate()[0]
	text = output.decode("utf-8")
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	print ("====================================")
	print (" Graph builded from ")
	print (" File: \t\t\t\t"+str(options.filename) )
	print (" Output: \t\t\t"+standardDirectory+str("graph_"+tail))
	print (" Runtime: \t\t\t"+ str(text[0])+ " seconds")
	print (" Nodes: \t\t\t"+str(text[1]))
	print (" Edges: \t\t\t" + str(text[2]))
	print (" Blued Edges: \t\t" + str(text[3]))
	print("====================================")
	for j in text:
		tmp.append(j.replace(".", ","))
else:
	output = subprocess.Popen( [path+"/createGraph/makeGraphRand.py","-n",str(nodes),"-d", "-o",standardDirectory+"graph_random"], stdout=subprocess.PIPE ).communicate()[0]
	tail = "random"
	text = output.decode("utf-8")
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	print("====================================")
	print(" Random Graph builded with ")
	print(" Output: \t\t\t" + standardDirectory + str("graph_" + tail))
	print(" Runtime: \t\t\t" + str(text[0]) + " seconds")
	print(" Nodes: \t\t\t" + str(text[1]))
	print(" Edges: \t\t\t" + str(text[2]))
	print(" Blued Edges: \t\t" + str(text[3]))
	print("====================================")
	for j in text:
		tmp.append (j.replace(".",","))
if options.onlybuild == True:
	exit(0)

if options.heuristic == "SLF":
	# Sa
	output = subprocess.Popen( [path+"/heuristics/colorGraph.py","-f",standardDirectory+str("graph_"+tail.split(".")[0])+".gml","-d","-o",standardDirectory+str("graph_gis_"+tail)], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8")
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	print("====================================")
	print(" Graph Partition builded with SLF-Stategy  ")
	print(" Runtime:\t\t\t" + str(text[0]) + " seconds")
	print(" Coloring: \t\t\t" + str(text[1]))
	print(" minMPS'-a: \t\t" + str(text[2]))
	print(" Removed Nodes: \t" + str(text[3]))
	print(" Output files: \t\t"+standardDirectory+str("graph_gis_"+tail)+"*")
	print("====================================")
	for j in text:
		tmp.append (j.replace(".",","))
if options.heuristic == "IP":
	# Sa
	output = subprocess.Popen( [path+"/heuristics/colorGraphIP.py","-f",standardDirectory+str("graph_"+tail.split(".")[0])+".gml","-d","-o",standardDirectory+str("graph_gis_"+tail)], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8")
	print (text)
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	print("====================================")
	print(" Graph Partition builded with SLF-Stategy  ")
	print(" Runtime:\t\t\t" + str(text[0]) + " seconds")
	print(" Coloring: \t\t\t" + str(text[1]))
	print(" minMPS'-a: \t\t" + str(text[2]))
	print(" Removed Nodes: \t" + str(text[3]))
	print(" Output files: \t\t"+standardDirectory+str("graph_gis_"+tail)+"*")
	print("====================================")
	for j in text:
		tmp.append (j.replace(".",","))
elif options.heuristic == "GIS":
	# strategy_independent_set
	output = subprocess.Popen( [path+"/heuristics/colorGraphIn.py","-f",standardDirectory+str("graph_"+tail.split(".")[0])+".gml","-d","-o",standardDirectory+str("graph_gis_"+tail)], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8") 
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	print("====================================")
	print(" Graph Partition builded with GIS-Stategy  ")
	print(" Runtime:\t\t\t" + str(text[0]) + " seconds")
	print(" Coloring: \t\t\t" + str(text[1]))
	print(" minMPS'-a: \t\t" + str(text[2]))
	print(" Removed Nodes: \t" + str(text[3]))
	print(" Output files: \t\t"+standardDirectory+str("graph_gis_"+tail)+"*")
	print("====================================")
	for j in text:
		tmp.append (j.replace(".",","))
elif options.heuristic == "CLIQUE":
	# Complement
	output = subprocess.Popen(
		[path + "/heuristics/colorGraphComplement.py", "-f", standardDirectory + str("graph_" + tail.split(".")[0]) + ".gml",
		 "-d", "-o", standardDirectory + str("graph_gis_" + tail)], stdout=subprocess.PIPE).communicate()[0]
	text = output.decode("utf-8")
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	print("====================================")
	print(" Graph Partition builded with CLIQUE-Stategy  ")
	print(" Runtime:\t\t\t" + str(text[0]) + " seconds")
	print(" Coloring: \t\t\t" + str(text[1]))
	print(" minMPS'-a: \t\t" + str(text[2]))
	print(" Removed Nodes: \t" + str(text[3]))
	print(" Output files: \t\t" + standardDirectory + str("graph_gis_" + tail) + "*")
	print("====================================")
	for j in text:
		tmp.append (j.replace(".",","))
	outputList.append (tmp)

#print (outputList)
#with open("output_.csv", "w", newline='') as f:
#    writer = csv.writer(f, delimiter=';')
#    writer.writerows(outputList)
