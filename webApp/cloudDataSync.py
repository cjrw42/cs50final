#!/usr/bin/python3
"""
  Called as a systemd daemon process at boot and intantly restarted if app crashes
"""
import json
import sys
import time
import gspread
import sqlite3
from oauth2client.service_account import ServiceAccountCredentials
#============================================================================    
dbpath = '/home/pi/sensorProj/final/webApp/sensorlog.db'
#============================================================================    

GDOCS_OAUTH_JSON       = '/home/pi/sensorProj/final/webApp/creds.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'cs50rawSensorDataTest1'


def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)

def rowsToUpload():
    worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)
    all = worksheet.get_all_values()
    end_row = len(all)
    lastIdValue = worksheet.acell("A"+ str(end_row)).value
    with sqlite3.connect(dbpath) as con:   
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from sensorData where id > " + lastIdValue + " limit 95")  
        rows = cur.fetchall()  
        return rows

while True:
    # see whats in the database we have not uploaded yet
    rows = rowsToUpload()
    # Append the data in the spreadsheet
    try:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)
        for row in rows:
            worksheet.append_row((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
            
    except Exception as e:
        print('Append error - aborted write :: will restart',e)
        continue

    time.sleep(100)
    