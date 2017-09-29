import sys
import json
import networkx as nx
import math
from networkx.algorithms import approximation as approx
import time
from itertools import groupby as g
from operator import itemgetter
from collections import Counter
import operator
import csv
from pubmed import *
from operator import itemgetter

def getMaxClique(G):
	cl = nx.get_node_attributes(G,'clique')
	max = 0
	for key in cl:
		if cl[key]>max:
			max = cl[key]
	return max

def nodes_connected(G, u, v):
	return u in G.neighbors(v)

# Function to get nodes neighbors counted
def getNeighbors(G):
	nh = {}
	for node in G.nodes():
		nh[node] = G.degree(node) # len(G.neighbors(node)
	nh = {k: v for k, v in nh.items() if v != 0}
	nh = dict(sorted(nh.items(), key=operator.itemgetter(1)))
	return nh

def getSmalestNeighbor(G,u1):
	nh = {}
	for node in G[u1]:
		nh[node] = G.degree(node) # len(G.neighbors(node))
	nh = sorted(nh.items(), key=operator.itemgetter(1))
	#print (nh)
	#print (nh[0])
	if len(nh)>0:
		return nh[0][0] 
	else:
		return None

# Function to remove all double items in a list
def unique(seq): 
   # order preserving
   noDupes = []
   [noDupes.append(i) for i in seq if not noDupes.count(i)]
   return noDupes

# Function that returns the most common item in a list
def most_common(L):
  return max(L, key=L.count)

# Function that removes all instances of an item from alist
def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

# assuming that a Graph has attribute "color" it counts all occurrences 
def countColor (G, color):
	return len(list(n for n,d in G.nodes_iter(data=True) if d['color']==color))	

def getMeshTermNumber (G):
	meshTags = []
	for node in G.nodes():	
		meshTags.extend (G.node[node]['mesh'])
	#print (Counter(meshTags))
	return Counter(meshTags)

def getClusterJournals (G, color, maxCount=3, separator=""):
	journals = []
	colorList=nx.get_node_attributes(G,'color')
	journalList=nx.get_node_attributes(G,'journal')
	for node in G.nodes():
		if str(colorList.get(node)) == str(color):
			journals.append (journalList.get(node))
	countTerms = Counter(journals)
	oldList = countTerms
	returnString = ""
	i = 1;
	for key, value in sorted(countTerms.items(), key=operator.itemgetter(1), reverse=True):
		returnString += key + " ("+str(int(oldList[key]))+") "+separator
		i += 1
		if (i > maxCount) and (maxCount != -1):
			break; 
	return (returnString)


def getClusterYears (G, color, maxCount=3, separator=""):
	years = []
	colorList=nx.get_node_attributes(G,'color')
	yearList=nx.get_node_attributes(G,'year')
	for node in G.nodes():
		if str(colorList.get(node)) == str(color):
			years.append (yearList.get(node))
	countTerms = Counter(years)
	oldList = countTerms
	returnString = ""
	i = 1;
	for key, value in sorted(countTerms.items(), key=operator.itemgetter(1), reverse=True):
		returnString += str(key) + " ("+str(int(oldList[key]))+") "+separator
		i += 1
		if (i > maxCount) and (maxCount != -1):
			break; 
	return (returnString)

def getClusterYearsList (G, color, maxCount=3, separator=""):
	years = []
	colorList=nx.get_node_attributes(G,'color')
	yearList=nx.get_node_attributes(G,'year')
	for node in G.nodes():
		if str(colorList.get(node)) == str(color):
			years.append (yearList.get(node))
	countTerms = Counter(years)
	oldList = countTerms
	returnString = ""
	i = 1;
	retList = []
	for key, value in sorted(countTerms.items(), key=operator.itemgetter(1), reverse=True):
		returnString += str(key) + " ("+str(int(oldList[key]))+") "+separator
		retList.append ([key, int(oldList[key] )])
		i += 1
	return (retList)


def getClusterName (G, color, maxCount=3, separator=""):
	meshTags = []
	#print (meshList)
	colorList=nx.get_node_attributes(G,'color')
	#print ("col:"+str(colorList))
	meshList=nx.get_node_attributes(G,'mesh')
	#print (meshList)
	for node in G.nodes():
		#print (str(i))
		#print ("col:"+str(color.get(str(i))))
		#print (str(colorList.get(node)) +" vs "+ str(color))
		if str(colorList.get(node)) == str(color):
			#print ("adding: "+meshList.get(str(i)))
			if isinstance(meshList.get(node), str):
				meshTags.append (meshList.get(node))
			else:
				meshTags.extend (meshList.get(node))
	#print (meshTags) 
	meshTermNumber = getMeshTermNumber (G)
	maxValue =  max(meshTermNumber.values())
	average = float( max(meshTermNumber.values())) / len(meshTermNumber)
	sumValues = sum(meshTermNumber.values())
	countTerms = Counter(meshTags)
	oldList = countTerms
	#print (str(oldList))
	#print ( sorted(countTerms.items(), key=operator.itemgetter(1), reverse=True) )
	for key, value in countTerms.items():
		# do something with value
		countTerms[key] = float(value) / sumValues
	#print ( sorted(countTerms.items(), key=operator.itemgetter(1), reverse=True) )
	
	#firstTag = most_common(meshTermNumber)
	#secondTag = ""
	#thirdTag = ""
	#meshTags = remove_values_from_list(meshTags, firstTag)
	#if (len(meshTags) > 0):
	#	secondTag = most_common(meshTags)
	#	meshTags = remove_values_from_list(meshTags, secondTag)
	#	secondTag = ", "+secondTag
	#if (len(meshTags) > 0):
	#	thirdTag = most_common(meshTags)
	#	meshTags = remove_values_from_list(meshTags, thirdTag)
	#	thirdTag = ", "+thirdTag
	returnString = ""
	i = 1;
	for key, value in sorted(countTerms.items(), key=operator.itemgetter(1), reverse=True):
		#print (key)
		returnString += key + " ("+str(int(oldList[key]*sumValues))+") "+separator
		i += 1
		if (i > maxCount) and (maxCount != -1):
			break; 
	#print (returnString)	
	return (returnString)

def buildGraph (createEdgePercent, createBlueEdgePercent, createBluedEdges, data):
	G=nx.Graph()
	# Calculate max value
	#maxEdgeValue = max([int(x['Label']) for x in data['edges']])
	maxEdgeValue = 100
	count = 0
	delcount = 0
	#for node in data:
	#	if str(node).startswith("edges"):
	#		#print (str(data[node]))
	#		for edge in data[node]:
	#			#print (str(edge))
	#			if int(edge['Label']) > maxEdgeValue:
	#				maxEdgeValue = int(edge['Label'])
	#if maxEdgeValue == 0:
	#	maxEdgeValue = 0.1	
	#print (str(maxEdgeValue))
	for node in data:
		if str(node).startswith("node"):
			#print (">>"+str(data[node]))
			meshterms =  (data[node]["MeSH"][1:-1].split(", "))
			#print (data[node]["uri"])
			#print (data[node]["uri"].split(":",1)[1].split(":",1)[1] )
			pyear = 0
			if "date" not in data[node]:
				# No Date field given
				pyear = get_year(data[node]["uri"].split(":",1)[1].split(":",1)[1]) 
			else:
				pyear = int(data[node]["date"][0:4])
			#print (" Y: "+str(pyear))
			G.add_node(data[node]["Label"], color=-1, mesh=meshterms, title=data[node]["title"], ref=data[node]["ref"], uri=data[node]["uri"], year=pyear, journal=data[node]["ref"], end=0)
		if str(node).startswith("edges"):
			for edge in data[node]:
				#for edge in data["edges"]:
				similarity = int(edge["Label"]) #((int(edge["Label"])*100.0) / maxEdgeValue)
				#print (" Sim: "+str(similarity)+" edge: "+str(createEdgePercent))
				if (similarity <= createEdgePercent):
					G.add_edge(edge["Source"],edge["Dest"])
					G[edge["Source"]][edge["Dest"]]["color"]="black"
				elif (( similarity > createEdgePercent) and (similarity <= createBlueEdgePercent) ):
					if createBluedEdges:
						G.add_edge(edge["Source"],edge["Dest"])
						G[edge["Source"]][edge["Dest"]]["color"]="blue"
						count += 1
	for node in data:
		if str(node).startswith("node"):
			if data[node]["MeSH"]=="null" or data[node]["MeSH"]=="-":
				G.remove_node(data[node]["Label"])
				delcount += 1
	return [G, count, delcount]

def addBlueEdges (G, createEdgePercent, createBlueEdgePercent, createBluedEdges, data):
	# Calculate max value
	maxEdgeValue = 0
	for node in data:
		if str(node).startswith("edges"):
			#print (str(data[node]))
			for edge in data[node]:
				#print (str(edge))
				if int(edge['Label']) > maxEdgeValue:
					maxEdgeValue = int(edge['Label'])
	# Rebuild blue edges
	count = 0
	for node in data:
		if str(node).startswith("edges"):
			for edge in data[node]:
				similarity = ((int(edge["Label"])*100) / maxEdgeValue)
				if (( similarity > createEdgePercent) and (similarity <= createBlueEdgePercent) ):
					G.add_edge(edge["Source"],edge["Dest"], graphics={
						'width': 2.0, 'fill': '"#0000FF"'})
					G[edge["Source"]][edge["Dest"]]["color"]="blue"
					count += 1
	print (str(count)+" blue edges")
	return G

def buildValueGraph (G, d, count=15):
	valueGraph=nx.Graph()
	colorCount = d[max(d, key=lambda key: d[key])]
	minYear = 3000
	maxYear = 0
	for i in range(0,colorCount):
		terms = getClusterName(G,i,count);
		journals = getClusterJournals (G,i,count)
		yearc = getClusterYearsList (G,i,count)
		#print (yearc)
		countC = countColor (G,i);
		valueGraph.add_node(str(i), text=terms, journal=journals, value=countC) 
		for year in yearc:
			if year[0]==0:
				continue
			if year[0]>maxYear:
				maxYear = year[0]
			if year[0]<minYear:
				minYear = year[0]
	yearc.sort(key=itemgetter(0))
	#print (str(minYear)+" -- "+str(maxYear))
	for y in range(minYear, maxYear):
		nx.set_node_attributes(valueGraph, "y"+str(y), 0)
		nx.set_node_attributes(valueGraph, "s"+str(y), 0)
		nx.set_edge_attributes(valueGraph, "y"+str(y), 0)
		nx.set_edge_attributes(valueGraph, "s"+str(y), 0)
	for i in range(0,colorCount):
		yearc = getClusterYearsList (G,i,count)
		yearc.sort(key=lambda tup: tup[0]) 
		#print (str(yearc))
		summe = 0
		#print ("New Sum")
		for year in yearc:
			if year[0]==0:
				continue
			#print (" "+str(year))
			valueGraph.node[str(i)]["y"+str(year[0])] = year[1]
			valueGraph.node[str(i)]["s"+str(year[0])] = year[1] + summe
			summe += year[1]	
		#print (str(valueGraph.node[str(i)]))
	return valueGraph;


