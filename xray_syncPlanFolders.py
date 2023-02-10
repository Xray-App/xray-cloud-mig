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
import time
from os import path
import sys
import pandas as pd
import numpy as np
from datetime import datetime


# Command line arguments
parser = argparse.ArgumentParser(description='Plan folder definition Syncronizer')
parser.add_argument('-export',
    help='Export list of issues processed (default: information is logged but no file is created).'
)
commandExecutionExceptions = parser.parse_args()

start = time.time()
# Logging 
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



#logging.basicConfig(filename=os.path.basename(__file__ +".log"), filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info("------------------- ##### Starting ##### ------------------- ")
# Build ignore list if required

if commandExecutionExceptions.export != None: 
        fileExport = open(commandExecutionExceptions.export,"w") 

f = Figlet(font='slant')
print (f.renderText('Your Xray Generic Test definition synchronizer !'))

#Get auth token and build header for requests
response = requests.post('https://xray.cloud.getxray.app/api/v1/authenticate', data={"client_id": GLOBAL_client_id,"client_secret":GLOBAL_client_secret})
token=response.text.replace("\"","")
headers = {'Authorization':'Bearer %s' % token}
jira = JIRA(basic_auth=(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass),options={"server": GLOBAL_onPremiseURL})  # a username/password tuple

jiraCloud = JIRA(basic_auth=(GLOBAL_cloudUser, GLOBAL_apitoken),options={"server": GLOBAL_onCloudMig})  # a username/password tuple


# Get all Tests
logging.info("-------")
logging.info("======= Collecting INFO [START] =========")
logging.info("Processing Tests...")

mutation = ""
paths = []


def processFolders(repository, plan,mutation,headers):
   
    if "name" in repository and repository["name"] not in paths:
        logging.info("Name" + repository["name"])
        paths.append(repository["name"])
        path = repository["testRepositoryPath"] + "/" + repository["name"]
        createPlanFolder(headers,GLOBAL_url_xray,plan.id,path,mutation)
        page = 1
        while True:
            if "id" in repository and "totalTestCount" in repository:
                nTests = repository["totalTestCount"]
                if nTests > 0:
                    # Get all Tests linked to OnPremise test execution
                    r = requests.get('' + GLOBAL_onPremiseURL+'/rest/raven/1.0/api/testrepository/'+plan.key +'/folders/' + str(repository['id'])  +'/tests?limit=100&page=' + str(page) +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
                    if r.text == "" or r.text == None or r.text=="[]":
                        break
                    else :
                        try:
                            json_data = json.loads(r.text)
                        except:
                            logging.error(r.text)
                            break
                        listOfTests= []
                        if "tests" in json_data and str(json_data["tests"])!="[]":
                            for test in json_data["tests"]:
                                listOfTests.append(test['key'])
                                issue = jiraCloud.issue(test['key'])
                                strIssue = "[\"" + str(issue.id)+ "\"]"
                                mutation = addTestsToPlanFolder(headers,plan.id, path,strIssue,mutation)
                            packUpdateandSend(headers,GLOBAL_url_xray,mutation)
                            mutation = ""
                        else:
                            break
                    page = page +1
                else:
                    break
            else:
                break
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""

    if repository['folders'] == "[]":
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation = ""
        return
    else:
        for folder in repository['folders']:
            processFolders(folder,plan,mutation,headers)


block_size = 100
block_num = 0
mutation = ""
keyStats = []
timeStats = []
count = 0
while True:
    start_idx = block_num*block_size
    testplans = jira.search_issues(GLOBAL_jqlPlanFolder,start_idx,block_size)
    if len(testplans) == 0:
        # Retrieve issues until there are no more to come
        logging.info("No more Test plans.")
        break
    block_num += 1
    for plan in testplans:
        startExec = time.time()
        cloudPlan = jiraCloud.issue(plan.key)
        r = requests.get('' + GLOBAL_onPremiseURL+'/rest/raven/1.0/api/testrepository/'+ plan.key +'/folders', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
        if r.text == "" or r.text == None or r.text=="[]":
            break
        else :
            try:
                json_data = json.loads(r.text)
            except:
                logging.error("An error as occurred  - Skipping " + plan.key +" Test Plan")
                logging.error(r.text)
                break
            logging.info("Test Plan  " + plan.key)

            repository = json.loads(r.text)
            processFolders(repository,cloudPlan,mutation,headers)
            #for folder in folders:
        if commandExecutionExceptions.export != None:
            fileExport.write("%s\n" % plan.key)
            fileExport.flush()
        keyStats.append(plan.key)
        timeStats.append(time.time()-startExec)
        count = count +1
        logging.info('Done ' + str(count) + ' of ' + str(len(testplans)) )   

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