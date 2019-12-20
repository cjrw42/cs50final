#!/usr/bin/python3.7

import functions,time,os,sys
os.chdir(sys.path[0])  # important in cron driven scripts !!

# create an ampty list
data = []

# read a list back from the datbase of the most recent sensor data
rawData = functions.getLastRow()

# build a list of values to display
data.append("LastSensorRead "  + str(time.strftime('%H:%M:%S', time.localtime(rawData[1]))))
data.append("Light Level : " + str(rawData[2]))
data.append("Soil Moisture : " + str(rawData[4]))
data.append("Pressure : " + str(rawData[5]) + "mbar")
data.append("Humidity : " + str(rawData[6]) + "%")
data.append("Temperature : " + str(rawData[7]) + "'C")

# push those rows out to the OLED
functions.myOled(data)
