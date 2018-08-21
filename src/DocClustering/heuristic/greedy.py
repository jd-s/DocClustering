# Class Greedy
import logging
import sys
import time
import networkx as nx
from operator import itemgetter
import operator

class greedy:

    def __init__(self, G, strategy, docList):
        self.G = G
        self.strategy = strategy
        self.colorCount = 0
        self.color_time = 0
        self.mps_time = 0
        self.countNodesEliminated = 0
        self.mpsCount = 0
        self.docList = docList
        # Logging

    # Function to get nodes neighbors counted
    def getNeighbors(self,G):
        nh = {}
        for node in G.nodes():
            nh[node] = G.degree(node)  # len(G.neighbors(node)
        nh = {k: v for k, v in nh.items() if v != 0}
        nh = dict(sorted(nh.items(), key=operator.itemgetter(1)))
        return nh

    def getSmalestNeighbor(self,G, u1):
        nh = {}
        for node in G[u1]:
            nh[node] = G.degree(node)  # len(G.neighbors(node))
        nh = sorted(nh.items(), key=operator.itemgetter(1))
        # print (nh)
        # print (nh[0])
        if len(nh) > 0:
            return nh[0][0]
        else:
            return None

    def getMaxClique(self,G):
        cl = nx.get_node_attributes(G, 'clique')
        max = 0
        for key in cl:
            if cl[key] > max:
                max = cl[key]
        return max

    def nodes_connected(self,G, u, v):
        return u in G.neighbors(v)

    def returncolorCount (self):
        return self.colorCount
    # assuming that a Graph has attribute "color" it counts all occurrences
    def countColor(self, color):
        return len(list(n for n, d in self.G.nodes_iter(data=True) if d['color'] == color))

    # Function to remove all double items in a list
    def unique(self, seq):
        # order preserving
        noDupes = []
        [noDupes.append(i) for i in seq if not noDupes.count(i)]
        return noDupes

    def coloring(self):
        start_time = time.time()
        if self.strategy == "SLF":
            d = nx.coloring.greedy_color(self.G,
                                     strategy=nx.coloring.strategy_saturation_largest_first)
            nx.set_node_attributes(self.G, 'color', d)
        elif self.strategy == "GIS":
            d = nx.coloring.greedy_color(self.G,
                                     strategy=nx.coloring.strategy_independent_set)
            nx.set_node_attributes(self.G, 'color', d)
        elif self.strategy == "CLIQUE":
            G2 = self.G.copy()
            G2 = nx.complement(G2)
            nh = self.getNeighbors(G2)
            cliques = []
            for key, value in nh.items():
                u1 = key
                # print (u1)
                if u1 not in G2.nodes():
                    # print (" -> not in G2")
                    continue
                u2 = self.getSmalestNeighbor(G2, u1)
                if u2 == None:
                    # print (" -> None ")
                    continue
                G2.add_node(str(u1) + "|" + str(u2))
                for node in G2[u1]:
                    if self.nodes_connected(G2, u2, node):
                        G2.add_edge(str(u1) + "|" + str(u2), node)
                if 'clique' in G2.node[u2]:
                    G2.node[str(u1) + "|" + str(u2)]['clique'] = G2.node[u2]['clique']
                else:
                    G2.node[str(u1) + "|" + str(u2)]['clique'] = self.getMaxClique(G2) + 1
                G2.remove_node(u1)
                G2.remove_node(u2)
            for node in G2.nodes():
                if 'clique' not in G2.node[node]:
                    G2.node[node]['clique'] = self.getMaxClique(G2) + 1
            cl = nx.get_node_attributes(G2, 'clique')
            for key, value in cl.items():
                if "|" in str(key):
                    nodes = key.split("|")
                else:
                    nodes = [key]
                for node in nodes:
                    if node in self.G.nodes():
                        self.G.node[node]['color'] = value
                    elif int(node) in self.G.nodes():
                        self.G.node[int(node)]['color'] = value
                    else:
                        print(" Error, node does not exist! ")
            d = nx.get_node_attributes(self.G,'color')
        # Update docList
        for node in self.G.nodes():
            #print (self.docList)
            if node in self.docList:
                self.docList[node].setColor(self.G.node[node]["color"])
            else:
                print (str(node)+" not in list")

        self.colorCount = d[max(d, key=lambda key: d[key])]
        self.color_time = time.time() - start_time



    def run(self):
        self.coloring()
        start_time = time.time()
        colorList = []
        for i in range(0, self.colorCount+1):
            countC = self.countColor(i);
            colorList.append([i, countC])
        colorList = sorted(colorList, key=itemgetter(1))
        for colorSet in colorList:
            # Get a list of nodes with that color
            tmpNodeList = list(n for n, d in self.G.nodes_iter(data=True) if d['color'] == colorSet[0])
            # Now iterate over these nodes
            for i in range(0, len(tmpNodeList)):
                # catch that node
                node = tmpNodeList[i]
                # check if this node is not already an end-point!
                if "end" not in self.G.node[node]:
                    self.G.node[node]["end"] = 0
                if self.G.node[node]["end"] == 0:
                    colors = []
                    # for all neighbours
                    for nb in self.G.neighbors(node):
                        # is edge blue?
                        if "color" not in self.G[node][nb]:
                                self.G[node][nb]["color"] = False
                        if self.G[node][nb]["color"] == True:
                            # is node not yet excluded from stable sets?
                            if (self.G.node[nb]["color"] >= 0):
                                # Nodes are not in the same stable sets
                                if (self.G.node[nb]["color"] != self.G.node[node]["color"]):
                                    colors.append(self.G.node[nb]["color"])
                    # Now remove all double entries
                    uniqueList = self.unique(colors)
                    # check if "node" has at last two blue neighbours in different stable sets
                    if len(uniqueList) >= 2:
                        # Node is excluded from stable sets (color -1)
                        self.G.node[node]["color"] = -1
                        if node in self.docList:
                            self.docList[node].setColor(-1)
                        else:
                            print ("ERROR! NODE NOT IN LIST")
                        self.countNodesEliminated += 1
                        # now we see, that this node connects all stable sets connected with blue edges:
                        # mark all nodes as end-nodes
                        connectedSetsTmp = []
                        for nb in self.G.neighbors(node):
                            # is edge blue?
                            if self.G[node][nb]["color"] == True:
                                # is node not yet excluded from stable sets?
                                if (self.G.node[nb]["color"] >= 0):
                                    self.G.node[nb]["end"] = 1
                                    connectedSetsTmp.append(self.G.node[nb]["color"])
                        self.docList[node].extendNeighborCluster(connectedSetsTmp)
                        #self.G.node[node]["connected"] = connectedSetsTmp
        # print (str(valueGraph.number_of_nodes()))
        # logging.info (" (2) : \t\t "+str(valueGraph.number_of_nodes()-1))
        self.mps_time = time.time() - start_time
        colors = self.unique(list(nx.get_node_attributes(self.G, 'color').values()))
        self.mpsCount = len(colors)-1
        return [self.colorCount+1, self.mpsCount]