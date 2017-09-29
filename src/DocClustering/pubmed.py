"""
Created on 29 July 2012
@author: Lisa Simpson
DocClustering wrapper class
"""
from bs4 import BeautifulSoup
import requests


class pubmed:

    def get_abstract(self, id):
        r = requests.get('https://www.ncbi.nlm.nih.gov/pubmed/?term=' + str(id))
        html = r.text
        # Setup the BeautifulSoup Parser
        soup = BeautifulSoup(html, 'html.parser')
        year = soup.findAll("abstracttext")
        value = ""
        for val in year:
            value = val.text
        return value

    def getDocument(line, id):
        r = requests.get('https://www.ncbi.nlm.nih.gov/pubmed/?term=' + str(id))
        html = r.text
        doc = {}
        # Setup the BeautifulSoup Parser
        soup = BeautifulSoup(html, 'html.parser')
        doc["fulltext"] = ""
        year = soup.findAll("abstracttext")
        for val in year:
            doc["fulltext"] = val.text
        # Heading
        heading = soup.find("div", {"class": "rprt abstract"})
        divs = heading.findAll("h1")
        for val in divs:
            doc["title"] = val.text
        # Authors
        divs = heading.findAll("div", {"class": "auths"})
        for val in divs:
                doc["author"] = val.text
        # Mesh
        divs = heading.find("div", {"class": "morecit"})
        MeshList = []
        found = False
        if divs != None:
            for val in divs.findChildren():
                if found == True:
                    if val.name == "ul":
                        for term in val.findChildren():
                            MeshList.append(term.text.replace("*", ""))
                    found = False
                if val.name == "h4" and val.text.strip() == "MeSH terms":
                    found = True
        doc["terms"] = list(set(MeshList))
        # Year
        divs = heading.find("div", {"class": "cit"}).findAll(text=True, recursive=False)
        for val in divs:
            doc["year"] = (val[:5])
        # Journal
        divs = heading.find("div", {"class": "cit"})
        for val in divs.findChildren():
            doc["journal"] = (val.text.strip()[:-1])
        return doc