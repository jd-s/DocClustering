
class additionalList:

    def __init__(self, filename, caption):
        self.list = self.getPMIDList ( filename)
        self.caption = caption
        #print (self.list)

    def getPMIDList (self, filename):
        list = []
        with open(filename) as f:
            for i, line in enumerate(f):
                list.append (str(line).rstrip())
        return list

    def getListValue (self, node):
        nodelist =  node['ids'].split("|")
        count = 0
        for id in nodelist:
            if id in self.list:
                count += 1
        ret = {}
        ret[self.caption] = count
        return ret

    def getListValueProz (self, node):
        nodelist =  node['ids'].split("|")
        count = 0
        for id in nodelist:
            if id in self.list:
                count += 1
        ret = {}
        ret[self.caption+"percent"] = float(count)/float(node['value'])
        return ret
