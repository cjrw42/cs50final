#!/usr/bin/python3.7
"""
    call the script that runs the sensor read and stuffs
    values into the sqlite database
    
    normally this script is called every five mins from the
    crontab
"""
import functions

try:
    functions.dbInsertRow()
except Exception as e:
    print("dbInsert failed",e)