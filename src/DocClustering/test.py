#!/usr/bin/env python3.6
import sys
import subprocess
import csv
import os

# Create random graph
path = os.getcwd()
number = 2		# Number of tests to run
nodes = 100		# Nodes for instances
outputList = []
for i in range(0,number):
	
	tmp = []
	tmp.append (i)
	output = subprocess.Popen( [path+"/createGraph/makeGraphRand.py","-n",str(nodes),"-d", "-o","random_graph"], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8") 
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	for j in text:
		tmp.append (j.replace(".",","))

	# Sa
	output = subprocess.Popen( [path+"/heuristics/colorGraph.py","-f","/home/jens/IOgraph/random_graph.gml","-d","-o","random_graph_s"], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8") 
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	for j in text:
		tmp.append (j.replace(".",","))


	# strategy_independent_set
	output = subprocess.Popen( [path+"/heuristics/colorGraphIn.py","-f","/home/jens/IOgraph/random_graph.gml","-d","-o","random_graph_i"], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8") 
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	for j in text:
		tmp.append (j.replace(".",","))


	# Complement
	output = subprocess.Popen( [path+"/heuristics/colorGraphComplement.py","-f","/home/jens/IOgraph/random_graph.gml","-d","-o","random_graph_c"], stdout=subprocess.PIPE ).communicate()[0]
	text = output.decode("utf-8") 
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	for j in text:
		tmp.append (j.replace(".",","))

	# IP
	output = subprocess.Popen(
		[path + "/heuristics/colorGraphIP.py", "-f", "/home/jens/IOgraph/random_graph.gml", "-d", "-o",
		 "random_graph_c"], stdout=subprocess.PIPE).communicate()[0]
	text = output.decode("utf-8")
	text = text.split('[')[1]
	text = text.split(']')[0]
	text = text.split(', ')
	
	for j in text:
		tmp.append (j.replace(".",","))
	outputList.append (tmp)

with open("output_"+str(number)+"_"+str(nodes)+".csv", "w", newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(outputList)
