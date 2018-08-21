"""
Created on 29 July 2012
@author: Lisa Simpson
DocClustering wrapper class
"""
import networkx as nx
import json
from bs4 import BeautifulSoup
import requests
# Document class
from DocClustering.data.document import *
# Heuristics
from DocClustering.heuristic.greedy import *
from collections import Counter
import operator
import csv
from DocClustering.similarity import *
from DocClustering.pubmed import *
import json

class reader:

    def write_SCAIView_from_PmidList(self, filename, outfile, sim=similarity.sim_given):
        """
       Function that only reads Pubmedlist
       :param filename:
       :param sim: Function for similarity measure
       :param fulltext: True, if the Fulltexts should be forced to Download from Pubmed
       :return:
       """
        self.G = nx.Graph()
        self.docList = {}
        # Calculate max value
        count = 0
        delcount = 0
        with open(filename) as f:
            for i, line in enumerate(f):
                print("Loading document " + str(i) + " PMID " + str(line), end="\r ", flush=True)
                if line.strip() != "":
                    doc = pubmed.getDocument(self, line)
                    meshterms = doc["terms"]
                    pyear = doc["year"]
                    label = line
                    # print (label)
                    title = doc["title"]
                    journal = doc["journal"]
                    uri = "https://www.ncbi.nlm.nih.gov/pubmed/?term=" + line
                    tmpDoc = document(label, label, title=title,
                                      author="",
                                      publishingYear=pyear, journal=journal, terms=meshterms, uri=uri)
                    tmpDoc.fulltext = doc["fulltext"]
                    self.G.add_node(label, color=-1, end=0)
                    self.docList[label] = tmpDoc
        nodeList = self.G.nodes()
        doclist = {}
        for i in range(0, len(nodeList)):
            doc = self.docList[nodeList[i]]
            docj = {}
            docj['Label'] = str(i)
            docj['abstract'] = doc.fulltext
            docj['ref'] = doc.journal
            docj['title']  = doc.title
            docj['MeSH'] = doc.terms
            docj['date'] = str(doc.publishingYear)
            docj['uri'] = "https://www.ncbi.nlm.nih.gov/pubmed/PMID:"+str(doc.externalid)
            doclist['node-'+str(i)]=docj
        run = 0
        for i in range(0, len(nodeList)):
            print("Calculating distance for node " + str(i) + " out of " + str(len(nodeList)))
            for j in range(i + 1, len(nodeList)):
                edge = {}
                edge["Label"] = 0.0
                edge["Source"] = nodeList[i]
                edge["Dest"] = nodeList[j]
                # for edge in data["edges"]:
                similarityV = sim(self, edge)  # ((int(edge["Label"])*100.0) / maxEdgeValue)
                node = {}
                node['Label'] = str(similarityV)
                node['Source'] = str(i)
                node['Dest'] = str(j)
                doclist['edges-' + str(run)] = [node]
                run += 1

        with open(outfile, 'w') as outfileh:
            json.dump(doclist, outfileh)
                # print ("-->")
        #        if (similarityV < self.createEdgePercent):
                    # print(" Sim: " + str(similarityV) + " edge: " + str(self.createEdgePercent))
        #            self.G.add_edge(edge["Source"], edge["Dest"])
        #            self.G[edge["Source"]][edge["Dest"]]["color"] = False
        #        elif ((similarityV >= self.createEdgePercent) and (similarityV <= self.createBlueEdgePercent)):
                    # print(" Sim: " + str(similarityV) + " edge: " + str(self.createBlueEdgePercent))
        #            self.G.add_edge(edge["Source"], edge["Dest"])
        #            self.G[edge["Source"]][edge["Dest"]]["color"] = True
        #            count += 1
        #for key in list(self.docList):
        #    value = self.docList[key]
            # print (value.terms)
        #    if value.terms == "null" or value.terms == "-" or len(value.terms) == 0:
        #        self.G.remove_node(key)
        #        del self.docList[key]
        #        delcount += 1
        # d = nx.coloring.greedy_color(self.G,
        #                             strategy=nx.coloring.strategy_saturation_largest_first)
        # self.colorCount = d[max(d, key=lambda key: d[key])]
        #return [len(self.docList), len(self.G.nodes()), self.G.number_of_edges(), count]

    def read_PmidList(self, filename, sim=similarity.sim_given, fulltext=False):
        """
        Function that only reads Pubmedlist
        :param filename:
        :param sim: Function for similarity measure
        :param fulltext: True, if the Fulltexts should be forced to Download from Pubmed
        :return:
        """
        self.G = nx.Graph()
        self.docList = {}
        # Calculate max value
        count = 0
        delcount = 0
        with open(filename) as f:
            for i, line in enumerate(f):
                print ("Loading document "+str(i)+" PMID "+str(line), end="\r ", flush=True)
                if line.strip() != "":
                    doc = pubmed.getDocument(self, line)
                    meshterms = doc["terms"]
                    pyear = doc["year"]
                    label = line
                    # print (label)
                    title = doc["title"]
                    journal = doc["journal"]
                    uri = "https://www.ncbi.nlm.nih.gov/pubmed/?term="+line
                    tmpDoc = document(label, label, title=title,
                                      author="",
                                      publishingYear=pyear, journal=journal, terms=meshterms, uri=uri)
                    tmpDoc.fulltext = doc["fulltext"]
                    self.G.add_node(label, color=-1, end=0)
                    self.docList[label] = tmpDoc
        nodeList = self.G.nodes()
        for i in range(0,len(nodeList)):
            print("Calculating distance for node " + str(i) + " out of " + str(len(nodeList)))
            for j in range (i+1,len(nodeList)):
                edge = {}
                edge["Label"] = 0.0
                edge["Source"] = nodeList[i]
                edge["Dest"] = nodeList[j]
                # for edge in data["edges"]:
                similarityV = sim(self, edge)  # ((int(edge["Label"])*100.0) / maxEdgeValue)
                # print ("-->")
                if (similarityV < self.createEdgePercent):
                    # print(" Sim: " + str(similarityV) + " edge: " + str(self.createEdgePercent))
                    self.G.add_edge(edge["Source"], edge["Dest"])
                    self.G[edge["Source"]][edge["Dest"]]["color"] = False
                elif ((similarityV >= self.createEdgePercent) and (similarityV <= self.createBlueEdgePercent)):
                    # print(" Sim: " + str(similarityV) + " edge: " + str(self.createBlueEdgePercent))
                    self.G.add_edge(edge["Source"], edge["Dest"])
                    self.G[edge["Source"]][edge["Dest"]]["color"] = True
                    count += 1
        for key in list(self.docList):
            value = self.docList[key]
            # print (value.terms)
            if value.terms == "null" or value.terms == "-" or len(value.terms) == 0:
                self.G.remove_node(key)
                del self.docList[key]
                delcount += 1
        # d = nx.coloring.greedy_color(self.G,
        #                             strategy=nx.coloring.strategy_saturation_largest_first)
        # self.colorCount = d[max(d, key=lambda key: d[key])]
        return [len(self.docList), len(self.G.nodes()), self.G.number_of_edges(), count]

    def read_SCAIview_Nodes(self, filename, sim=similarity.sim_given, fulltext=False):
        """
        Function that only reads nodes from SCAIview export
        :param filename:
        :param sim: Function for similarity measure
        :param fulltext: True, if the Fulltexts should be forced to Download from Pubmed
        :return:
        """
        self.G = nx.Graph()
        self.docList = {}
        with open(filename) as data_file:
            data = json.load(data_file)
        # Calculate max value
        count = 0
        delcount = 0
        for node in data:
            if str(node).startswith("node"):
                meshterms = (data[node]["MeSH"][1:-1].split(", "))
                if "date" not in data[node]:
                    pyear = self.get_year(data[node]["uri"].split(":", 1)[1].split(":", 1)[1])
                else:
                    pyear = int(data[node]["date"][0:4])
                # print (" Y: "+str(pyear))
                label = data[node]["Label"]
                # print (label)
                title = data[node]["title"]
                journal = data[node]["ref"]
                uri = data[node]["uri"]
                tmpDoc = document(label, data[node]["uri"].split(":", 1)[1].split(":", 1)[1], title=title,
                                  author="",
                                  publishingYear=pyear, journal=journal, terms=meshterms, uri=uri)
                if "abstract" in data[node]:
                    tmpDoc.fulltext = data[node]["abstract"]
                elif fulltext:
                    tmpDoc.fulltext = pubmed.get_abstract(self, tmpDoc.externalid)
                self.G.add_node(label, color=-1, end=0)
                self.docList[label] = tmpDoc
        nodeList = self.G.nodes()
        for i in range(0,len(nodeList)):
            #print("Calculating distance for node " + str(i) +" out of "+ str(len(nodeList)))
            for j in range (i+1,len(nodeList)):
                #print("Calculating distance between " + str(i) + " and " + str(j), end="\r ", flush=True)
                edge = {}
                edge["Label"] = 0.0
                edge["Source"] = nodeList[i]
                edge["Dest"] = nodeList[j]
                # for edge in data["edges"]:
                try:
                    similarityV = sim(self, edge)  # ((int(edge["Label"])*100.0) / maxEdgeValue)
                except:
                    print ("Exception processing texts "+str(i) + " and "+str(j))
                    similarityV = 0
                #print(" -> "+str(similarityV))
                # print ("-->")
                if (similarityV < self.createEdgePercent):
                    # print(" Sim: " + str(similarityV) + " edge: " + str(self.createEdgePercent))
                    self.G.add_edge(edge["Source"], edge["Dest"])
                    self.G[edge["Source"]][edge["Dest"]]["color"] = False
                elif ((similarityV >= self.createEdgePercent) and (similarityV <= self.createBlueEdgePercent)):
                    # print(" Sim: " + str(similarityV) + " edge: " + str(self.createBlueEdgePercent))
                    self.G.add_edge(edge["Source"], edge["Dest"])
                    self.G[edge["Source"]][edge["Dest"]]["color"] = True
                    count += 1
        #for key in list(self.docList):
        #    value = self.docList[key]
        #    # print (value.terms)
        #    if value.terms == "null" or value.terms == "-" or len(value.terms) == 0:
        #        self.G.remove_node(key)
        #        del self.docList[key]
        #        delcount += 1
        #print ("Nodecount: "+str(len(self.G.nodes())))
        # d = nx.coloring.greedy_color(self.G,
        #                             strategy=nx.coloring.strategy_saturation_largest_first)
        # self.colorCount = d[max(d, key=lambda key: d[key])]
        return [len(self.docList)+1, len(self.G.nodes())+1, self.G.number_of_edges(), count]


    def read_SCAIview(self, filename, sim=similarity.sim_given, fulltext=False):
        """
        Reads JSON from Scaiview Export
        :param filename:
        :param sim: Function for similarity measure
        :param fulltext: True, if the Fulltexts should be forced to Download from Pubmed
        :return:
        """
        self.G = nx.Graph()
        self.docList = {}
        with open(filename) as data_file:
            data = json.load(data_file)
        # Calculate max value
        count = 0
        delcount = 0
        for node in data:
            if str(node).startswith("node"):
                if isinstance(data[node]["MeSH"], (list, tuple)):
                    meshterms = data[node]["MeSH"]
                else:
                    meshterms = (data[node]["MeSH"][1:-1].split(", "))
                if "date" not in data[node]:
                    pyear = self.get_year(data[node]["uri"].split(":", 1)[1].split(":", 1)[1])
                else:
                    pyear = int(data[node]["date"][0:4])
                # print (" Y: "+str(pyear))
                label = data[node]["Label"]
                # print (label)
                title = data[node]["title"]
                journal = data[node]["ref"]
                uri = data[node]["uri"]
                tmpDoc = document(label, data[node]["uri"].split(":", 1)[1].split(":", 1)[1], title=title,
                                  author="",
                                  publishingYear=pyear, journal=journal, terms=meshterms, uri=uri)
                if "fulltext" in data[node]:
                    tmpDoc.fulltext = data[node]["fulltext"]
                elif fulltext:
                    tmpDoc.fulltext = similarity.get_abstract(self, tmpDoc.externalid)
                self.G.add_node(label, color=-1, end=0)
                self.docList[label] = tmpDoc
        for node in data:
            if str(node).startswith("edges"):
                for edge in data[node]:
                    # for edge in data["edges"]:
                    similarityV = sim(self, edge)  # ((int(edge["Label"])*100.0) / maxEdgeValue)
                    # print ("-->")
                    if (similarityV < self.createEdgePercent):
                        # print(" Sim: " + str(similarityV) + " edge: " + str(self.createEdgePercent))
                        self.G.add_edge(edge["Source"], edge["Dest"])
                        self.G[edge["Source"]][edge["Dest"]]["color"] = False
                    elif ((similarityV >= self.createEdgePercent) and (similarityV <= self.createBlueEdgePercent)):
                        # print(" Sim: " + str(similarityV) + " edge: " + str(self.createBlueEdgePercent))
                        self.G.add_edge(edge["Source"], edge["Dest"])
                        self.G[edge["Source"]][edge["Dest"]]["color"] = True
                        count += 1
        for key in list(self.docList):
            value = self.docList[key]
            # print (value.terms)
            if value.terms == "null" or value.terms == "-" or len(value.terms) == 0:
                self.G.remove_node(key)
                del self.docList[key]
                delcount += 1
        # d = nx.coloring.greedy_color(self.G,
        #                             strategy=nx.coloring.strategy_saturation_largest_first)
        # self.colorCount = d[max(d, key=lambda key: d[key])]
        return [len(self.docList), len(self.G.nodes()), self.G.number_of_edges(), count]