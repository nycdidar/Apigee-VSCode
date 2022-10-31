
#!/usr/bin/python
#
'''
Apigee Automation

https://apidocs.apigee.com/docs/resource-files/1/overview
https://apidocs.apigee.com/apis
https://apidocs.apigee.com/docs/api-proxies/1/overview



Installation
Python Requirements: 3.18+
Install all the necessary missing modules if prompted
pip install MODULENAME

'''

import json
from operator import truediv
import requests
import os
import time
import random
import string
import sys
from zipfile import ZipFile
import shutil

from datetime import datetime
now = datetime.now() # current date and time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler



###--------- CONFIGS ----------------------------------
###----------------------------------------------------
# This is your Apigee user name and password in the basic auth format.
# This is equivalent of header -u USERNAME:PASSWORD, Use Postman to generate the code below
# In mac terminal. Type this command to generate the AuthCode
# echo -n "YOUR_APIGEE_USER_NAME:YOUR_APIGEE_PASSWORD" | base64
ApigeeBasicAuthCreds = "ABCDEdkeflalwielddkdkddd=="
path = 'logs'
allowedFiles = ["*.js"]
ignoreFiles = [".DS_Store"]
##----------------------------------------------------
##----------------------------------------------------

date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
#print("date and time:",date_time)
# Check whether the specified path exists or not
isExist = os.path.exists(path)
if not isExist:
  # Create a new directory because it does not exist 
  os.makedirs(path)
  print("The log directory is created!")

# Some OSX verion has prefix path
macPathPrefix = "/System/Volumes/Data"

orgName = "fancyOrg"
watchDirectory = ""
configFile = "data.json"
listOfAPIS = {}
allAPIs = []
apiBasePath = "https://api.enterprise.apigee.com/v1/o/" + orgName
apiType = "apis"
apiName = "Demo"
outputFolderName = ''
revNo = "1"
api_url = apiBasePath
headers = {"Authorization": "Basic " + ApigeeBasicAuthCreds}
formData = ""


def unzipFile(fileName, apiType):
  print("** Unzipping File ** ", fileName)
  with ZipFile(fileName + '.zip', 'r') as zipObj:
    # Extract all the contents of zip file in current directory
    zipObj.extractall()

    if (apiType == "apis"):
        bundleName = "apiproxy"
    else:
        bundleName = "sharedflowbundle"

    os.remove(fileName + '.zip')
    os.rename(bundleName, fileName)

    watchDirectory = fileName + os.sep
    print("** Watching directory for changes ** ", watchDirectory)

    watch = OnMyWatch()
    watch.watchDirectory = watchDirectory
    watch.run()
    

def downloadAPI(apiName, fileName, revision, apiType):
  try:
    shutil.rmtree(fileName)
  except:
    print('Error while deleting directory. So skipping..' + fileName)
  api_url = apiBasePath + "/" + apiType +  "/"  + apiName + "/revisions/" + str(revision) + "?format=bundle"
  print('Endpoint: ' + api_url)
  response = requests.get(api_url, headers = headers)

  os.mkdir(fileName)
  os.mkdir(fileName + os.sep + revision)

  if (apiType == "apis"):
    bundleName = "apiproxy"
  else:
    bundleName = "sharedflowbundle"

  open(fileName + os.sep + revision + os.sep + bundleName +".zip", "wb").write(response.content)
  unzipFile(fileName + os.sep + revision + os.sep + bundleName, apiType)

# Do not do anything if the PROD version is same as dev/test to avoid accidental PROD override
def deploymentStatus(apiType, apiName):
  api_url = apiBasePath + "/" + apiType + "/" + apiName + "/deployments"
  #print("List of APIs", api_url)
  response = requests.get(api_url, headers = headers)
  responseJSON = json.loads(response.content)
  prodVersion = 0
  devVersion = 0
  testVersion = 0
  for x in responseJSON['environment']:
    print("Deployments: " + x['name'], x['revision'][0]['name'])
    if (x['name'] == "prod"):
        prodVersion = x['revision'][0]['name']
    if (x['name'] == "dev"):
        devVersion = x['revision'][0]['name']
    if (x['name'] == "test"):
        testVersion = x['revision'][0]['name']

  if (int(prodVersion) > 0 and (prodVersion == devVersion or prodVersion == testVersion)):
    return True
  else:
    return False


def getAPIList(apiType):
  api_url = apiBasePath + "/" + apiType
  #print("List of APIs", api_url)
  response = requests.get(api_url, headers = headers)
  responseJSON = json.loads(response.content)
  return responseJSON


def apiDetails(apiName):
  api_url = apiBasePath + "/" + apiType +  "/"+  apiName
  #print("List of APIs", api_url)
  response = requests.get(api_url, headers = headers)
  responseJSON = json.loads(response.content)
  #print(responseJSON)
  return responseJSON

def listOfResourceFiles():
  api_url = apiBasePath + "/" + apiType +  "/"+  apiName + "/revisions/" +  revNo + "/resourcefiles"
  #print("List of APIs", api_url)
  response = requests.get(api_url, headers = headers)
  responseJSON = json.loads(response.content)
  return responseJSON  

def saveToFile(data, fileName):
    #data = {"favApis": ["Demo"]}
    with open(fileName, 'w') as f:
        json.dump(data, f)


def readFile(fileName):
    # Opening JSON file
    f = open(fileName)
    
    # returns JSON object as 
    # a dictionary
    return json.load(f)



def updateFileToApigee(updateFileName, src_path, revisionNo, apiName):
    now = datetime.now() # current date and time
    f = open(src_path, "r")
    fileData = f.read()
    f.close()
    fileTimeStamp = now.strftime("%m%d%Y%H%M%S")
    f = open("logs" + os.sep + apiType + "-"+ apiName + "-" + str(revisionNo) + "-"+ fileTimeStamp + "-"+ updateFileName, "w")
    f.write(fileData)
    f.close()

    for x in ignoreFiles:
        if (x == updateFileName):
            return False
    fileType = "jsc"
    api_url = apiBasePath + "/" + apiType + "/"  + apiName + "/revisions/" + str(revisionNo) + "/resourcefiles/" + fileType + "/" + updateFileName
    files = {'upload_file': open( src_path,'rb')}
    values = {}
    response = requests.put(api_url, headers = headers, files=files, data=values)
    responseJSON = json.loads(response.content)
    
    if (response.status_code == 200):
        print("Update successful . [" + str(response.status_code) +  "] - Uploading file: " , responseJSON['name'])
    else:
        print("** ERROR ** Could not update file ", updateFileName)
        print("** ERROR DETAILS **  ", responseJSON)
        print("** ERROR DETAILS **  ", src_path)
        print("** ERROR DETAILS **  ", api_url)


class OnMyWatch:
    # Set the directory on watch
    #watchDirectory = "Demo" + os.sep
    watchDirectory = ""
    def __init__(self):  
        self.observer = Observer()
        
    def run(self):
        #event_handler = Handler()
        event_handler = specificFilesHandler(self.watchDirectory)
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")
  
        self.observer.join()
  

# class that takes care of everything
class specificFilesHandler(PatternMatchingEventHandler):
    def __init__(self, source_path):
        # setting parameters for 'PatternMatchingEventHandler'
        # Only watch for JS files
        super(specificFilesHandler, self).__init__(patterns=allowedFiles,
                                     # ignore_patterns=["*~"],
                                     ignore_directories=True, 
                                     case_sensitive=False)
        self.source_path = source_path
        self.print_info = None
    def on_modified(self, event):
        x = event.src_path.split(os.sep)
        updateFileName = x[len(x) - 1]
        revisionNo = x[len(x) - 5]
        apiName = x[len(x) - 6]
        print("Watchdog FileName:", updateFileName)
        #print("Watchdog Revision No:", revisionNo)
        print("Watchdog API Name:", apiName)
        updateFileToApigee(updateFileName, macPathPrefix + event.src_path, revisionNo, apiName)


def apiWithRevision(apiType):
    allAPIs = getAPIList(apiType)
    print('********* ' + apiType + ' **************')
    i = 0
    for x in allAPIs:
        i = i + 1
        print("[" + str(i) + "] -> ", x)
    print('\r\n********* Select an option (number next API) **************')
    userInput = input()
    userSelected = allAPIs[int(userInput) - 1 ]
    proxyDetails = apiDetails(userSelected)
    revNo = proxyDetails['revision'][len(proxyDetails['revision']) - 1]
    deploymentDetails = deploymentStatus(apiType, userSelected)

    # Do not continue if PROD version is same as dev or test
    if (deploymentDetails == True):
        print("\r\n\r\n****** WARNING!!! ******** WARNING!!! ******** WARNING!!! **************")
        print("************** YOUR PROD VERSION IS SAME AS DEV/TEST *******************") 
        print("**** CREATE A NEW DEV REVISION TO ENSURE PROD IS NOT BEING IMPACTED ****") 
        print("************************************************************************")   
        return False


    print("-----", deploymentDetails)
    print("\r\n***************************************************")
    print("*** You selected *** [ ",  userSelected + " ]. " + " Last Revision " + revNo)
    print("****************************************************")   

    print('\r\n ********* Do you want to work with the ' + apiType + ' [' + userSelected + '] [Revision  '  + revNo +  '] ? [y/n] **************')
    continueWorking = input()
    if (continueWorking == "y" or continueWorking == "Y"):
        #userData = {"favApis": ["Demo", "OIDC_Core", "Saml2"]}
        #saveToFile(userData, configFile)
        downloadAPI(userSelected, userSelected , revNo, apiType)
    else:
        print('********* ok no problem !!! **************')



# Display User Prompt
def displayPromp():
    print('\r\n\r\n\r\n********* APIGEE TOOL *******************')
    print('********* Select an option **************\r\n')
    print('[1] - API Proxy')
    print('[2] - Shared Flow\r\n')
    proxyOrSharedFlow = input()
    if (proxyOrSharedFlow == "1"):
        #configData = readFile(configFile)
        #print('********* configData **************', configData['favApis'])
        print('********* API List **************')
        apiType = "apis"
        apiWithRevision(apiType)
    elif (proxyOrSharedFlow == "2"):
        apiType = "sharedflows"
        apiWithRevision(apiType)
    else:
        print('Invalid Option')
displayPromp()

