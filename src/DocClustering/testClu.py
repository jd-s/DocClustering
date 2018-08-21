


import random
def clustering(run):
    newcluster=[]
    for i in range(0,run):
        rand=random.randint(0, len(cluster.G.nodes()))
        if str(rand) in cluster.docList:
            if cluster.docList[str(rand)].externalid.rstrip() in list1.list:
                colorDoc = dict((key, value) for key, value in cluster.docList.items() if value.color == cluster.docList[str(rand)].color)
                for doc in colorDoc.values():
                    if not doc.externalid.rstrip() in newcluster:
                        newcluster.append (doc.externalid.rstrip())
            else:
                colorDoc = dict((key, value) for key, value in cluster.docList.items() if value.color == cluster.docList[str(rand)].color)
                for doc in colorDoc.values():
                    if doc.externalid.rstrip() in newcluster:
                        newcluster.remove (doc.externalid.rstrip())
        rand=random.randint(0, len(cluster2.G.nodes()))
        if str(rand) in cluster2.docList:
            if cluster2.docList[str(rand)].externalid.rstrip() in list1.list:
                colorDoc = dict((key, value) for key, value in cluster2.docList.items() if value.color == cluster2.docList[str(rand)].color)
                for doc in colorDoc.values():
                    if not doc.externalid.rstrip() in newcluster:
                        newcluster.append (doc.externalid.rstrip())
            else:
                colorDoc = dict((key, value) for key, value in cluster2.docList.items() if value.color == cluster2.docList[str(rand)].color)
                for doc in colorDoc.values():
                    if doc.externalid.rstrip() in newcluster:
                        newcluster.remove (doc.externalid.rstrip())
    return newcluster









# CALL

for i in range(1,60):
    count = 0
    newcluster = clustering(i)
    for doc in newcluster:
        if doc  in list1.list:
            count += 1
        #else:
            #print ("??")
    ratio = 0
    if len(newcluster)>0:
        ratio = count/len(newcluster)
    ratio2 = 0
    if count > 0:
        ratio2 = count/len(list1.list)
    print (str(i)+" & "+ str(len(newcluster))+ " & "+str(count) + " &" + str(ratio) + " & "+ str(len(list1.list)) +" & "+str(ratio2))