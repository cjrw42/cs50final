#!/usr/bin/python3.7
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import time
import os
import sys

os.chdir(sys.path[0]) # make sure we can find the json files when we call the script from cron

#============================================================================
photoDir="/home/pi/sensorProj/final/webApp/images/archive/"
#============================================================================
try:

    # this simple call to GoogleDrive() kicks off a whole bunch of background
    # auth stuff - see stps://pythonhosted.org/PyDrive/oauth.html# for more info
    drive = GoogleDrive()
    
    # empty list placeholder init
    remoteFiles=[]
    
    # iterate through all files in the root folder.  on the cloud account
    remoteList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for remoteFile in remoteList:
        # and build a simple list of  all the filenames
        remoteFiles.append(remoteFile['title'])    
    
    # now do something similar  for the local folder where the images are archived
    for root, dirs, localFiles in os.walk(photoDir):
        a = 1 # I dont know how to do the above without at least one indented line?
            
    
    print ("Differences List ::")        
    
    # ok, so now sort each of those lists uniquely  using set()  - Values should be 
    # unique any way -but it never hurts to be sure. Then subtract the remote list
    # from the local list and whatever is left are the files that need uploading
    diffsList = list(set(localFiles)-set(remoteFiles))
    for diff in diffsList:
        print(diff)
        filePath = photoDir + diff                  # build the read file path
        file1 = drive.CreateFile({'title' : diff})  # set the filename 
        file1.SetContentFile(filePath)              # read the file from the archive
        file1.Upload()                              # upload
        time.sleep(1)                               # snooze for a while
    
    # OK that was the end of a run 
    print("done")
    
    
except Exception as e:
    print ("Failed to upload photos to cloud based storage : ",e)


