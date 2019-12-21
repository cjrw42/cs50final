#!/usr/bin/python3.7

import time
import functions
import os,sys
os.chdir(sys.path[0]) 


try:
    path ="/home/pi/sensorProj/final/webApp/static/images/archive/" + time.strftime('%Y%m%d%H%M') +".jpg"
            
    hum,temp = functions.myHumiTemp()
    pressure,tempEnce = functions.myPressureTemp()
    commandLine = 'raspistill -n -w 1024 -h 768 -q 80 -ae 22 -a 8 -a "%Y-%m-%d %X Data::[L:' 
    commandLine += str(functions.myLight()) 
    commandLine += ' S:' 
    commandLine += str(functions.mySoil()) 
    commandLine += ' R:' 
    commandLine += str(functions.myRain())
    commandLine += ' H:' 
    commandLine += str(hum) + '%'
    commandLine += ' T:' 
    commandLine += str(temp) + 'C'
    commandLine += ' P:' 
    commandLine += str(pressure) + "mbar"
    commandLine += ']" -t 1 -o ' + path
    
    os.system(commandLine)

except Exception as e:
    print("image capture to archive failed : ",e)