#import ujson as json
#import pandas as pd
import os
import fileinput
import csv
import bisect
import sys


nameIdLookup = []
userIdList = []
idsToInclude = []
lookupId = 1493923903
edgeOut = csv.writer(open('edge_list.csv','w'))

#load screenname / id cross reference
for line in fileinput.FileInput("/Users/ericbudd/PycharmProjects/twitter-data-viz/twitter_name_id_table.txt"):
    nameIdLookup.append(tuple(line.strip().split(",")))

# create list of ids to use for filtering
for each in nameIdLookup:
    userIdList.append(int(each[1]))

userIdList.sort()
# print (userIdList)

print("I sorted the list")

#sys.exit()

def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return x
    else:
        return None


def indexName(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    else:
        return None




# find if id is in my import list
def checkForIdMatch(id, account):
    found = index(userIdList, int(id))
    return tuple((account[0],found))


    # for term in userIdList:
    #     if int(term) == int(id):
    #         return tuple((account[0],int(id)))
    #


#for followers_file in os.listdir("/Users/ericbudd/PycharmProjects/twitter-data-viz/custom-who-to-follow/followers"):
    #print(followers_file)


# nameIdLookup = []
# nameIdLookup.append(tuple(line.strip().split(",")))
# nameIdLookup.append(tuple('_alanbsmith,977286368'.split(",")))
# nameIdLookup.append(tuple('00Piep,33955042'.split(",")))

def parseSingleFollowerFile(nameAndId):
    print(nameAndId)
    idsFromSingleFile = []
    basepath = "/Users/ericbudd/PycharmProjects/twitter-data-viz/custom-who-to-follow/followers/"
    print(basepath + nameAndId[0])
    fileName = basepath + nameAndId[0] + ".txt"
    file = fileinput.FileInput(fileName)

    fileSize = os.stat(fileName).st_size
    print("File length = " + str(fileSize))


    if fileSize > 0000:
        for line in file:
            if line.strip().isdigit():
                # print("yay")
                edge = checkForIdMatch(line, nameAndId)
                if edge[1] != None:
                    #print(edge)
                    idsFromSingleFile.append(edge)

        # filter output by excluding nodes with less than a certain number of edges
        #print(len(idsFromSingleFile))
        if len(idsFromSingleFile) > 0:
            for edges in idsFromSingleFile:
                idsToInclude.append(edges)

    print("idsFromSingleFile=", len(idsFromSingleFile))
    print("idsToInclude length=",len(idsToInclude))

#parseSingleFollowerFile("00Piep.txt")

#print(idsToInclude)

i = 0

for line in nameIdLookup:
    # if i > 1:
    #     break
    parseSingleFollowerFile(line)
    i = i + 1
    #print(line)


#print(idsToInclude)

edgeNamesOut = []


sortedNameIdLookup = sorted(nameIdLookup, key=lambda s : int(s[1]))
#print(sortedNameIdLookup)


for id in idsToInclude:
    #print(id)
    index = indexName(userIdList, int(id[1]))
    edgeNamesOut.append(tuple((id[0], sortedNameIdLookup[index][0])))


    # for term in nameIdLookup:
    #     if int(term[1]) == int(id[1]):
    #         edgeNamesOut.append(tuple((id[0],term[0])))
    #         break

#print(edgeNamesOut)

for line in edgeNamesOut:
    dataOut = line[0],line[1]
    edgeOut.writerow(dataOut)
