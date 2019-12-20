#!/usr/bin/python3.7

"""
test
"""
import functions

print(functions.epochToTime(1576270203))

now = functions.myTimeStamp()
aDayAgo = now - 84000
query = "select timestamp,light from sensordata where timestamp > " + str(aDayAgo) 
rows = functions.dbGetRows(query)
data = functions.lOfTuplesToLoL(rows)

print (data)
# now convert the epocj time to something more readable
for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])
        print (data[i][0])