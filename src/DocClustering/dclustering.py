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
from DocClustering.reader import *
from DocClustering.mesh import *
import pickle

class dclustering:
    """dclustering is the wrapper class for DocClustering"""


    __all__ = [
        'runSLF',
        'runGIS',
        'runClique',
        'getDocumentList',
        'saveInstanceGraph',
        'readFromFile',
        'getCluster',
        'getClusters',
        'read_SCAIview',
        'addValueToValueGraph'
    ]

    def get_year(id):
        """
        Helper functions
         :return: Year from pubmed
        """
        r = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=' + str(id))
        html = r.text
        # Setup the BeautifulSoup Parser
        soup = BeautifulSoup(html, 'html.parser')
        year = soup.findAll(attrs={"name": "PubDate"})
        value = "0000"
        for val in year:
            value = val.text
        return int(value[0:4])

    def __init__(self, createEdgePercent=3, createBlueEdgePercent=4):
        self.docList = {}
        self.G =nx.Graph()
        self.createEdgePercent = createEdgePercent
        self.createBlueEdgePercent = createBlueEdgePercent
        self.colorCount = 0
        self.mpsCount = 0
        self.hasRun = False
        self.hasRunValueGraph = False
        self.m = mesh("/home/jens/ownCloud-SCAI/mesh.json")

    def runSLF(self):
        """
        Runs the Algorithm with SLF-Strategy
         :return: Coloring and minMPS'a
        """
        instance = greedy(self.G, "SLF", self.docList)
        ret = instance.run()
        self.colorCount = ret[0]
        self.mpsCount = ret[1]
        self.hasRun = True
        return ret

    def runGIS(self):
        """
        Runs the Algorithm with GIS-Strategy
         :return: Coloring and minMPS'a
        """
        instance = greedy(self.G, "GIS", self.docList)
        ret = instance.run()
        self.colorCount = ret[0]
        self.mpsCount = ret[1]
        self.hasRun = True
        return ret

    def runClique(self):
        """
        Runs the Algorithm with Clique
         :return: Coloring and minMPS'a
        """
        instance = greedy(self.G, "CLIQUE", self.docList)
        ret = instance.run()
        self.colorCount = ret[0]
        self.mpsCount = ret[1]
        self.hasRun = True
        return ret

    def names_Full(self, docs):
        terms = []
        for key, doc in docs.items():
            terms.extend (doc.terms)
        counter = Counter (terms)
        counted = sorted(counter.items(), key=operator.itemgetter(1), reverse=True)
        ret = ""
        for key in counted:
            ret += str(key[0])+" ("+str(key[1])+") "
        return ret

    def names_List(self, docs):
        terms = []
        for key, doc in docs.items():
            terms.extend (doc.terms)
        ret = list(set(terms))
        return ret

    def names_List_Abs(self, docs):
        terms = []
        for key, doc in docs.items():
            terms.extend (doc.terms)
        ret = terms
        return ret

    def getCluster(self, id, nameStrategy=names_Full):
        """
        Returns a simple ClusterList
        runs runSLF if not yet done
         :return: [Nodelist,EdgeList]
        """
        if not self.hasRun:
            self.runSLF()
        # Nodes
        ClusterList = {}
        colorDoc = dict((key, value) for key, value in self.docList.items() if value.color == id)
        if len(colorDoc) > 0:
            idlist = []
            yearList = {}
            for doc in colorDoc.values():
                idlist.append(doc.externalid)
                if "y" + str(doc.publishingYear) in yearList:
                    yearList["y" + str(doc.publishingYear)] += 1
                else:
                    yearList["y" + str(doc.publishingYear)] = 1
            ClusterList['topics'] = nameStrategy( colorDoc)
            ClusterList['ids'] = '|'.join(idlist)
            ClusterList['value'] = len(colorDoc)
            ClusterList.update (yearList)
        return ClusterList




    def getClusters(self):
        """
        Returns a simple ClusterList
        runs runSLF if not yet done
         :return: [Nodelist,EdgeList]
        """
        if not self.hasRun:
            self.runSLF()
        # Nodes
        ClusterList = {}
        for i in range(0, self.colorCount+1):
            colorDoc = dict((key, value) for key, value in self.docList.items() if value.color == i)
            if len(colorDoc) > 0:
                yearList = {}
                yearList['value'] = len(colorDoc)
                ClusterList[i] = yearList
        return ClusterList

    def getDocumentList(self):
        """
        Returns a NodeList and EdgeList according to the Clusters found
        runs runSLF if not yet done
         :return: [Nodelist,EdgeList]
        """
        if not self.hasRun:
            self.runSLF()
        # Nodes
        Nodelist = {}
        for i in range(0, self.colorCount+1):
            colorDoc = dict((key,value) for key, value in self.docList.items() if value.color == i)
            if len(colorDoc)>0:
                idlist = []
                idlistint = []
                yearList = {}
                for doc in colorDoc.values():
                    idlist.append(doc.externalid.rstrip())
                    idlistint.append(doc.id)
                    if "y"+str(doc.publishingYear) in yearList:
                        yearList["y"+str(doc.publishingYear)] += 1
                    else:
                        yearList["y"+str(doc.publishingYear)] = 1
                yearList['ids'] = '|'.join(idlist)
                yearList['idsinternal'] = '|'.join(idlistint)
                yearList['value'] = len(colorDoc)
                Nodelist[i] = yearList
        # Edges
        EdgeList = {}
        colorDoc = dict((key, value) for key, value in self.docList.items() if value.color == -1)
        for doc in colorDoc.values():
            for i in doc.nbClusters:
                for j in doc.nbClusters:
                    if i != j:
                        # Erhöhen
                        if str(i)+"|"+str(j) in EdgeList:
                            EdgeList[str(i)+"|"+str(j)].append (doc.externalid)
                        else:
                            EdgeList[str(i)+"|"+str(j)] = [ doc.externalid ]
        return [Nodelist,EdgeList]

    def getIntersection(self, cluster1, cluster2):
        """
        Gets all intersection between both clusters
        :param cluster1:
        :param cluster2:
        :return:
        """
        if not self.hasRunValueGraph:
            self.buildValueGraph
        tmpre = self.getDocumentList()
        EdgeList = tmpre[1]
        tmp = {}
        tmp['docids'] = []
        if str(cluster1) + "|" + str(cluster2) in EdgeList:
            tmp['docids'].extend(EdgeList[str(cluster1) + "|" + str(cluster2)])
        if str(cluster2) + "|" + str(cluster1) in EdgeList:
            tmp['docids'].extend(EdgeList[str(cluster2) + "|" + str(cluster1)])
        tmp['docids'] = list(set(tmp['docids']))
        neighbors = self.valueGraph.neighbors(cluster1)
        if cluster2 in neighbors:
            tmp['value'] = self.valueGraph[cluster1][cluster2]["value"]
        else:
            tmp['value'] = 0
        return tmp



    def __hirarchirecursive(self, node, parent, assigned):
        #print (" Looking at node "+str(node))
        for nb in self.valueGraph.neighbors(node):
            if nb in parent:
                if parent[nb] != None:
                    if parent[node] != nb:
                        val1 = self.getIntersection(nb, node)['value']
                        val2 = self.getIntersection(nb, parent[nb])['value']
                        if val1 >  val2:
                            parent[nb] = node
                            if nb not in assigned:
                                assigned.append (nb)
                                ret = self.__hirarchirecursive(nb, parent, assigned)
                                parent = ret[0]
                                assigned = ret[1]
            else:
                parent[nb] = node
        return [parent, assigned]

    def __get_degree(self,iterable):
        return iterable[1]["degree"]


    def getHirarchie(self):
        if not self.hasRunValueGraph:
            self.buildValueGraph()
        degrees = self.getClusterDegreesSimple()
        # degreesd = sorted(degrees.items(), key=self.__get_degree)
        degreesd = sorted(degrees.items(), key=operator.itemgetter(1), reverse=True)
        assigned = []
        parent = {}
        for key in degreesd:
            if key[0] not in parent:
                # The first key[0] with the most intersection
                assigned.append (key[0])
                parent[key[0]] = None
            ret = self.__hirarchirecursive(key[0], parent, assigned)
            parent = ret[0]
            assigned = ret[1]
        return parent

    def getClusterDegreesSimple(self):
        if not self.hasRunValueGraph:
            self.buildValueGraph()
        clusters = {}
        for node in self.valueGraph:
            neighbors = self.valueGraph.neighbors(node)
            count = 0
            for nb in neighbors:
                count += self.valueGraph[node][nb]["value"]
            clusters[node] = count
        return clusters


    def getClusterDegrees(self):
        if not self.hasRunValueGraph:
            self.buildValueGraph()
        clusters = {}
        for node in self.valueGraph:
            neighbors = self.valueGraph.neighbors(node)
            forcluster = {}
            forcluster['degree'] = len(neighbors)
            forcluster['docs'] = 0
            forcluster['docids'] = []
            for nb in neighbors:
                forcluster['docs'] += self.valueGraph[node][nb]["value"]
                tmp = self.getDocumentList()
                EdgeList = tmp[1]
                if str(node)+"|"+str(nb) in EdgeList:
                    forcluster['docids'].extend (EdgeList[str(node)+"|"+str(nb)])
                if str(nb)+"|"+str(node) in EdgeList:
                    forcluster['docids'].extend (EdgeList[str(nb)+"|"+str(node)])
            forcluster['docids']=list(set(forcluster['docids']))
            clusters[node] = forcluster
        return clusters

    def getLandscape(self):
        """
        Claculates a Landscape with spring_layout and height=value of clusters
        :return:
        """
        if not self.hasRunValueGraph:
            self.buildValueGraph()
        pos = nx.spring_layout(self.valueGraph, weight='value')
        Z = []
        A = []
        for k in pos:
            A.append(k)
            Z.append(int(self.valueGraph.node[k]['value']))
        X = []
        Y = []
        for item in list(pos.values()):
            X.append(item[0] * 10)
            Y.append(item[1] * 10)
        List = []
        List.append(A)
        List.append(X)
        List.append(Y)
        List.append(Z)
        return List
        #with open(outputpathfilename + 'grid.csv', 'w') as myfile:
        #    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        #    wr.writerows(List)

    def save(self, filename):
        with open(filename, 'wb') as output:
            data = [self.docList, self.G]
            pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

    def open(self, filename):
        with open(filename, 'rb') as input:
            data = pickle.load(input)
            self.docList = data[0]
            self.G = data[1]

    def append(self, filename, sim=similarity.sim_given):
        with open(filename, 'rb') as input:
            data = pickle.load(input)
            NewDocList = data[0]
            NewG = data[1]
        oldG = self.G
        # Join both graphs
        U = nx.Graph()
        U.add_edges_from(self.G.edges() + NewG.edges())
        U.add_nodes_from(self.G.nodes() + NewG.nodes())
        self.G = U
        z = self.docList.copy()
        z.update(NewDocList)
        self.docList = z
        # Calculate max value
        count = 0
        # Now add all missing edges
        nodeList = NewG.nodes()
        nodeListOld = oldG.nodes()
        print (" Joining two Graphs with (a) "+str(len(nodeList)) +" nodes and (b) "+str(len(nodeListOld)) + "nodes")
        for i in range(0, len(nodeList)):
            #print("Calculating distance for node " + str(i) + " out of " + str(len(nodeList)))
            for j in range(0, len(nodeListOld)):
                edge = {}
                edge["Label"] = 0.0
                edge["Source"] = nodeList[i]
                edge["Dest"] = nodeListOld[j]
                # for edge in data["edges"]:
                try:
                    similarityV = sim(self, edge)  # ((int(edge["Label"])*100.0) / maxEdgeValue)
                except:
                    print("Exception processing texts " + str(i) + " and " + str(j))
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


    def saveToCsv(self, filename, func=getClusterDegrees):
        """
        Saves a Dict to a csv file
        :param filename: the filename
        :return:
        """
        tmp = func(self)
        with open(filename, 'w') as f:
            writer = csv.writer(filename)
            if isinstance(tmp, dict):
                for key, value in tmp.items():
                    writer.writerow([key, value])
            else:
                writer.writerows(tmp)

    def value_edges(self, liste, a, b):
        proz = 0
        for node in liste:
            # node is externalid
            docs = dict((key, value) for key, value in self.docList.items() if value.externalid == node)
            for key, value in docs.items():
                node2 = value.id
            #print (" NEw node "+str(node2))
            # Calculate edges to cluster a
            if node2 in self.G.nodes():
                nb = self.G.neighbors(node2)
            elif  int(node2) in self.G.nodes():
                nb = self.G.neighbors(int(node2))
            else:
                #print ("ERROR")
                continue
            colorDoc = dict((key, value) for key, value in self.docList.items() if value.color == int(a))
            #print ("Color a "+str(len(colorDoc)))
            counta = 0
            if len(colorDoc) > 0:
                for doc in colorDoc.values():
                    if self.G.node[doc.id] in  nb or doc.id in nb:
                        counta = counta + 1
            # Calculate edges to cluster b
            colorDoc2 = dict((key, value) for key, value in self.docList.items() if value.color == int(b))
            #print("Color b " + str(len(colorDoc2)))
            countb = 0
            if len(colorDoc2) > 0:
                for doc in colorDoc2.values():
                    if self.G.node[doc.id] in nb or doc.id in nb:
                        countb += 1
            # (counta + countb)/(|a|+|b|)
            proz += float(counta+countb)/float(len(colorDoc)+len(colorDoc2))
        ret = float(proz)/float(len(liste))
        #print (str(ret))
        return ret

    def value_sum(self, liste, a, b):
        return len(liste)

    def addValueToValueGraph (self, fun, valuefun=value_sum):
        if not self.hasRunValueGraph:
            self.buildValueGraph(valuefun)
        for node in self.valueGraph.nodes():
            self.valueGraph.node[node].update( fun( self.valueGraph.node[node]) )


    def buildValueGraph(self, valuefun=value_sum):
        """
        This function builds the Value Graph. Usually this function is called by others.
        :param valuefun:
        :return:
        """
        if not self.hasRun:
            self.runSLF()
        # Do the saving
        tmp = self.getDocumentList()
        Nodelist = tmp[0]
        EdgeList = tmp[1]
        self.valueGraph = nx.Graph()
        minYear = 3000
        maxYear = 0
        for  key, value in Nodelist.items() :
             terms = "" #getClusterName(G, i, count);
             journals = "" # getClusterJournals(G, i, count)
             yearc = 0 #getClusterYearsList(G, i, count)
             # print (yearc)
             self.valueGraph.add_node(str(key), value)
        for key, value in EdgeList.items() :
            #print (str(key)+" -> "+ str(value))

            a = key.split("|")[0]
            b = key.split("|")[1]
            value = valuefun(self, value, a, b)
            if a in self.valueGraph.nodes() and b in self.valueGraph.nodes():
                self.valueGraph.add_edge(a,b, value=value, ids=str(value))
            elif int(a) in self.valueGraph.nodes() and int(b) in self.valueGraph.nodes():
                self.valueGraph.add_edge(int(a), int(b), value=value, ids=str(value))
            #else:
            #    print ("ERROR, edges not in Graph!")
        self.hasRunValueGraph = True

    def saveInstanceGraph(self, filename, valuefun=value_sum):
        """
        This function saves the value Graph of the Clustering as a gml file, for example
        for Cytoscape import.
        :param filename:  Path and filename to save the graph.
        :param valuefun: The function that calculates the edges weight.
        :return:
        """
        if not self.hasRunValueGraph:
            self.buildValueGraph(valuefun)
        nx.write_gml(self.valueGraph, filename)

    def getNodeDistance(self, node1, node2, sim=similarity.sim_given, fulltext=False):
        edge = {}
        edge["Label"] = 0.0
        edge["Source"] = node1
        edge["Dest"] =  node2
        # for edge in data["edges"]:
        return sim(self, edge)


    def readFromFile(self, filename, method=reader.read_SCAIview, sim=similarity.sim_given, fulltext=False):
        self.G = nx.Graph()
        self.docList = {}
        return method(self,filename, sim, fulltext)