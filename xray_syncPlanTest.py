# Copyright (c) 2020, Xblend Software, Lda
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#    This product includes software developed by the Xblend Software, Lda.
# 4. Neither the name of the Xblend Software, Lda nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import requests
import json
from collections import namedtuple
from collections import Counter
from jira import JIRA
from requests.auth import HTTPBasicAuth
from xray_helper import *
from pyfiglet import Figlet
import argparse
from xray_variables import *
import logging
import os.path
from os import path
import sys
from jira.exceptions import JIRAError
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Command line arguments
parser = argparse.ArgumentParser(description='Test Plan and Test Syncronizer')
parser.add_argument('-ignore',
    help='Pass as input a list of onpremise issues keys, to be ignored (default: will try to get test defined in the JQL query). The format should be TESTPLANKEY:TESTKEY'
)
parser.add_argument('-export',
    help='Export list of issues processed (default: information is logged though the log file but no file is created). Format can then be used as input of this script'
)
commandExecutionExceptions = parser.parse_args()
start = time.time()

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
rootLogger = logging.getLogger()
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler = logging.FileHandler(filename=os.path.basename(__file__ + str(datetime.now().strftime("%H_%M_%d_%m_%Y")) +".log"), mode='a')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

logging.info("------------------- ##### Starting ##### ------------------- ")
# Build ignore list if required
ignoreList=[]
if commandExecutionExceptions.ignore != None:
    logging.info("Colleting list of issues to ignore....")
    if not path.exists(commandExecutionExceptions.ignore ):
        logging.info("File '"  + commandExecutionExceptions.ignore + "' does not exists")
        sys.exit()
    else:    
        with open(commandExecutionExceptions.ignore, mode='r',newline='') as csv_file:
             for line in csv_file:
                logging.info(line.replace('\n', ' ').replace('\r', ''))
                ignoreList.append(line.replace('\n', '').replace('\r', ''))

if commandExecutionExceptions.export != None: 
        fileExport = open(commandExecutionExceptions.export,"w") 


f = Figlet(font='slant')
print (f.renderText('Your Test Plan Xray synchronizer!'))

#Get auth token and build header for requests
response = requests.post('https://xray.cloud.getxray.app/api/v1/authenticate', data={"client_id": GLOBAL_client_id,"client_secret":GLOBAL_client_secret})
token=response.text.replace("\"","")
headers = {'Authorization':'Bearer %s' % token}
jira = JIRA(basic_auth=(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass),options={"server": GLOBAL_onPremiseURL})  # a username/password tuple
jiraCloud = JIRA(basic_auth=(GLOBAL_cloudUser, GLOBAL_apitoken),options={"server": GLOBAL_onCloudMig})  # a username/password tuple

# Get all Test Plans
logging.info("-------")
logging.info("======= Collecting INFO [START] =========")
logging.info("Processing Test Plans...")
block_size = 100
block_num = 0
mutation = ""
issuesScanned = []
keyStats = []
timeStats = []
count = 0
while True:
    start_idx = block_num*block_size
    issues = jira.search_issues(GLOBAL_jqlPlan,start_idx,block_size)
    if len(issues) == 0:
        # Retrieve issues until there are no more to come
        logging.info("No more Test Plans.")
        break
    block_num += 1
    for issue in issues:
        startExec = time.time()
        logging.info("Processing Test Plan : " + issue.key)
        # Get Tests from Test Plan
        page = 1
        while True:
            r = requests.get('' + GLOBAL_onPremiseURL+'/rest/raven/1.0/api/testplan/'+issue.key +'/test?limit=200&page=' + str(page) +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
            if r.text == "" or r.text == None or r.text=="[]":
                break
            else :
                mutation ="" 
                json_data =""
                try:
                    json_data = json.loads(r.text)
                except:
                     logging.error("An error as occurred  - Skipping " + issue.key +" Test Plan")
                     logging.error(r.text)
                     break
                logging.debug(json.dumps(json_data, indent=4, sort_keys=True))
                for testfromPlan in json_data:
                    composeKey=issue.key + ":" + testfromPlan["key"]
                    if not ignoreList or (ignoreList and composeKey not in ignoreList):
                        cloudTest = ""
                        try:
                            cloudTest =  jiraCloud.issue(testfromPlan["key"])
                        except JIRAError as e:
                            logging.error("Failed to retrieve test " + testfromPlan["key"] + " for " + issue.key + " from Jira Cloud connected returned with status " + str(e.status_code)  + " and message " + e.text + " Skipping to next plan ")
                            continue
                        logging.info("Processing Test: " + testfromPlan["key"])
                        plan = jiraCloud.issue(issue.key)
                        if commandExecutionExceptions.export != None:
                            issuesScanned.append(composeKey)
                        mutation = addTestToPlan(headers,cloudTest.id,plan.id,randomString(),mutation)
                        if commandExecutionExceptions.export != None and mutation == "":
                            ## Limit of mutation items has been reach and was push when adding to mutation
                            for item in issuesScanned:
                                fileExport.write("%s\n" % item)
                            issuesScanned.clear()
                    else:
                        logging.info("Ignoring by user request : " + issue.key)
                packUpdateandSend(headers,GLOBAL_url_xray,mutation)
                if commandExecutionExceptions.export != None:
                    for item in issuesScanned:
                        fileExport.write("%s\n" % item)
                    issuesScanned.clear()
            page += 1
        keyStats.append(issue.key)
        timeStats.append(time.time()-startExec)
        count = count +1
        logging.info('Done ' + str(count) + ' of ' + str(issues.total) )  
        
logging.info("======= Collecting INFO [END] =========")
logging.info('It took ' + str(time.time()-start) + 'seconds.')
logging.info("------------------- #####    End   ##### ------------------- ")
if keyStats:
    keysSeries = pd.Series(keyStats)
    timeSeries = pd.Series(timeStats)
    d = {'Key':keysSeries,
    'Time':timeSeries
    }
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(d)
    logging.info("------------------- #####    STATISTICS  - Full list  ##### ------------------- ")
    print (df)
    logging.info("------------------- #####    STATISTICS  - Aggregated data  ##### ------------------- ")

    print (df.describe())
    
if commandExecutionExceptions.export != None:
    fileExport.close()

