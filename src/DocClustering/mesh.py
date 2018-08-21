"""
Created on 29 July 2012
@author: Lisa Simpson
DocClustering wrapper class
"""
from bs4 import BeautifulSoup
import requests
import json


class mesh:

    def __init__(self, filename="/home/smadan/mesh.json", synonyms=False):
        self.meshterm = {}
        self.termmesh = {}
        with open(filename) as data_file:
            data = json.load(data_file)
        for term in data:
            #print (term)
            if "id" in term:
                if synonyms:
                    for SynName in term['synonyms']:
                        for tree in term['treeNumbers']:
                            # print (term['name'] + " -- "+ tree)
                            if SynName in self.meshterm:
                                if not tree in  self.meshterm[SynName]:
                                    self.meshterm[SynName].append(tree)
                            else:
                                self.meshterm[SynName] = [tree]
                            if not tree in self.termmesh:
                                self.termmesh[tree] = []
                            if not SynName in self.termmesh[tree]:
                                self.termmesh[tree].append(SynName)
                for tree in term['treeNumbers']:
                    #print (term['name'] + " -- "+ tree)
                    if term['name'] in self.meshterm:
                        if not tree in self.meshterm[term['name']]:
                            self.meshterm[term['name']].append (tree)
                    else:
                        self.meshterm[term['name']] = [tree]
                    if not tree in self.termmesh:
                        self.termmesh[tree] = []
                    if not term['name'] in self.termmesh[tree]:
                        self.termmesh[tree].append(term['name'])
                    #if term['name'] in self.termmesh[tree]:
                    #    self.termmesh[tree].append (term['name'])
                    #else:
                    #    self.termmesh[tree] = [term['name']]

    def getTrees (self, meshterm):
        return self.meshterm [meshterm]

    def getName(self, treeNumber):
        return self.termmesh [treeNumber]

