# Helper class that stores all relevant information of a document
class document:

    def __init__(self, id, externalid=0, title="", author="", publishingYear=0, journal="", terms=[], uri="" ):
        self.id = id
        self.externalid = externalid
        self.title = title
        self.author = author
        self.publishingYear = str(publishingYear).strip()
        self.journal = journal
        self.terms = terms
        self.terms = list(filter(None, self.terms))
        self.uri = uri.rstrip()
        self.color = -2
        self.ende = False
        self.nbClusters = []
        self.fulltext = ""


    def getTerms(self):
        return self.terms

    def appendNeighborCluster(self, color):
        if color not in self.nbClusters:
            self.nbClusters.append (color)

    def extendNeighborCluster(self, colorList):
        for i in colorList:
            self.appendNeighborCluster(i)

    def returnNeighborCluster(self):
        return self.nbClusters

    def setColor (self, color):
        self.color = color

    def getColor (self):
        return self.color

    def setEnde (self, end):
        self.ende = end

    def getEnde (self):
         return self.ende
