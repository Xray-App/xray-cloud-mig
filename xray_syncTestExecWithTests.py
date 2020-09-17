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
import time
import argparse
import os.path
from os import path
import sys
import csv
import numpy as np
import math
import pandas as pd
from datetime import datetime



# pip install jira
# pip install jira


## Command setup and handling
parser = argparse.ArgumentParser(description='Test Execution Syncronizer')
parser.add_argument('-manualTestlist',
    help='Pass as input the list of test keys, for whom step information will be retrieved (default: will try to get steps for all tests).'
)
parser.add_argument('-export',
    help='Export list of Test Execs fully processed (Important: Only Test Exec that were fully importorted are loogged in this file.If  a Test Exec is not present in the file its as not been processed or is in unstable situation.'
)
parser.add_argument('-ignore',
    help='Pass as input a  list of onpremise keys, to be ignored (default: will try to get test defined in the JQL query).'
)
parser.add_argument('-c','--comments', action='store_const',help='Do not include Executions comments (default: will include comments).', const=1)
parser.add_argument('-d','--defects', action='store_const',help='Do not include Executions defects (default: will include defects).', const=1)
parser.add_argument('-e','--evidences', action='store_const',help='Do not include Executions evidences (default: will include evidences).', const=1)
parser.add_argument('-sc','--stepcomments', action='store_const',help='Do not include steps comments (default: will include comments).', const=1)
parser.add_argument('-sd','--stepdefects', action='store_const',help='Do not include steps defects (default: will include defects).', const=1)
parser.add_argument('-se','--stepevidences', action='store_const',help='Do not include steps evidences (default: will include evidences).', const=1)
parser.add_argument('-st','--stepstatus', action='store_const',help='Do not include steps status (default: will include status).', const=1)
parser.add_argument('-s','--steps', action='store_const',help='Do not include steps comments (default: will include comments).', const=1)
parser.add_argument('-rerun', action='store_const',help='Used when we want to update existing information.Existing test runs will be deleted as part of this.', const=1)
commandExecutionExceptions = parser.parse_args()


## handling Loggers file and console. File will be based in a timestamp as its better for troubleshooting.

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
rootLogger = logging.getLogger()
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler = logging.FileHandler(filename=os.path.basename(__file__ + str(datetime.now().strftime("%H_%M_%d_%m_%Y")) + ".log"), mode='a')
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

## Export list should be by run
if path.exists(commandExecutionExceptions.export):
    logging.info("File '"  + commandExecutionExceptions.export + "' exists, please remove it before it starts. Note : You can use it as ignore list if it contains issues that you already processed and don't wish to process again.")
    sys.exit()
if commandExecutionExceptions.export != None: 
        fileExport = open(commandExecutionExceptions.export,"w") 


## warning user....
logging.info("Synchronizing comments....") if not commandExecutionExceptions.comments else logging.info("Ignoring comments....")
logging.info("Synchronizing defects....") if not commandExecutionExceptions.defects else logging.info("Ignoring defects....")
logging.info("Synchronizing evidences....") if not commandExecutionExceptions.evidences else logging.info("Ignoring evidences....")
logging.info("Synchronizing step comments....") if not commandExecutionExceptions.stepcomments else logging.info("Ignoring step comments....")
logging.info("Synchronizing step defects....") if not commandExecutionExceptions.stepdefects else logging.info("Ignoring step defects....")
logging.info("Synchronizing step evidences....") if not commandExecutionExceptions.stepevidences else logging.info("Ignoring step evidences....")
logging.info("Synchronizing step status....") if not commandExecutionExceptions.stepstatus else logging.info("Ignoring step status....")
logging.info("Synchronizing step....") if not commandExecutionExceptions.steps else logging.info("Ignoring step....")
logging.info("Updating existing information....") if commandExecutionExceptions.rerun else logging.info("Running Fresh Sync... ")

    

start = time.time()

## Build ignore list if we don't want to run the steps syncronization for a list of issues.
listOfTestsTogetDetails=[]
if commandExecutionExceptions.manualTestlist != None:
    logging.info("Restricting fetching of step information to list of issues provided....")
    if not path.exists(commandExecutionExceptions.manualTestlist ):
        logging.info("File '"  + commandExecutionExceptions.manualTestlist + "' does not exists")
        sys.exit()
    else:    
        with open(commandExecutionExceptions.manualTestlist, mode='r',newline='') as csv_file:
             for line in csv_file:
                logging.info(line.replace('\n', ' ').replace('\r', ''))
                listOfTestsTogetDetails.append(line.replace('\n', '').replace('\r', ''))

# Variables


f = Figlet(font='slant')
print (f.renderText('Your Xray Test Execution synchronizer!'))

#Get auth token and build header for requests
response = requests.post('https://xray.cloud.xpand-it.com/api/v1/authenticate', data={"client_id": GLOBAL_client_id,"client_secret":GLOBAL_client_secret})
token=response.text.replace("\"","")
#print(response.text)
headers = {'Authorization':'Bearer %s' % token}
jira = JIRA(basic_auth=(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass),options={"server": GLOBAL_onPremiseURL})  # a username/password tuple
jiraCloud = JIRA(basic_auth=(GLOBAL_cloudUser, GLOBAL_apitoken),options={"server": GLOBAL_onCloudMig})  # a username/password tuple

# check before running test that have steps ...so we only do calls for steps for those.
# Get all Test Executions OnPremise
logging.info("-------")
logging.info("======= Collecting INFO [START] =========")
logging.info("Processing Test Executions...")
block_size = 100
block_num = 0
keyStats,timeStats,typeStats = [],[],[]
mutation=""
tokenTimer = start
count = 0
while True:
    start_idx = block_num*block_size
    # get test executions OnPremise
    issues = jira.search_issues(GLOBAL_jqlExec,start_idx,block_size)
    if len(issues) == 0:
        # Retrieve issues until there are no more to come
        logging.info("No more Test Executions.")
        break
    block_num += 1
    for issue in issues:
        startExec = time.time()
        if ignoreList and (issue.key in ignoreList):
            logging.info("Ignoring by user request : " + issue.key)
            continue
        
        # For each Test Execution we have OnPremise
        logging.info("Processing OnPremise Test Execution : " + issue.key)
        page = 1
        # Get details from Test Exec into Cloud
        cloudExec = jiraCloud.issue(issue.key)
        onPremiseEnvType = getattr(issue.fields,"customfield_" + GLOBAL_testEnvironmentsId)
        onPremiseEnvType = str(onPremiseEnvType).replace('\'','\"')
        logging.info(onPremiseEnvType)
        if onPremiseEnvType !="[]":
            mutation = addTestEnvironmentsToTestExecution(headers,mutation,cloudExec.id, onPremiseEnvType)
        while True:
            timeToRenew= time.time()-tokenTimer
            if timeToRenew > 43200: #  12 hours
                headers = renewToken()
                tokenTimer = time.time()
            # Get all Tests linked to OnPremise test execution
            r = requests.get('' + GLOBAL_onPremiseURL+'/rest/raven/1.0/api/testexec/'+issue.key +'/test?limit=100&detailed=true&page=' + str(page) +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
            if r.text == "" or r.text == None or r.text=="[]":
                break
            else :
                listofkeysInCloud,listoftests,listofExe,listOfStatus,listOfTimeFinished,listOfTimeStarted,listOfExecuter,listOfAssignee,listOfDefect,listOfEvidences,listOfCommentsForTest = [],[],[],[],[],[],[],[],[],[],[]
                listOfDefectSteps,listOfCommentsSteps,listOfEvidencesStep,listOfStatusSteps = {},{},{},{}
                json_data = ""
                try:
                    json_data = json.loads(r.text)
                except:
                     logging.error("An error as occurred  - Skipping " + issue.key +" Test Execution")
                     logging.error(r.text)
                     break
                logging.info("Test Exec details from OnPremise: ")

                ## Clean up before adding
                if commandExecutionExceptions.rerun:
                    logging.info("Cleaning " + cloudExec.key)
                    listoftestsTOClean = []
                    for testfromtestExec in json_data:
                        cloudTest = jiraCloud.issue(testfromtestExec["key"])
                        mutation = removeTestExecutionsFromTest(headers,mutation,cloudTest.id, cloudExec.id,randomString())
                
                # make sure all were removed all test associations before we start adding
                packUpdateandSend(headers,GLOBAL_url_xray,mutation)
                mutation =""

                for testfromtestExec in json_data:
                    cloudTest = jiraCloud.issue(testfromtestExec["key"])
                    logging.info("Adding " + testfromtestExec["key"] + " to test execution on Cloud")
                    mutation = addTestToTestExecution(headers,mutation,cloudTest.id, cloudExec.id,randomString())
                    logging.info("[Getting detail for sync] - Status....")
                    listoftests.append(cloudTest.id)
                    listofkeysInCloud.append(cloudTest.key)
                    listOfStatus.append(testfromtestExec["status"])
                    ##
                    if 'finishedOn' in testfromtestExec:
                        listOfTimeFinished.append(testfromtestExec["finishedOn"])
                    else:
                        listOfTimeFinished.append("NOTFINISHED")
                    if 'startedOn' in testfromtestExec:
                        listOfTimeStarted.append(testfromtestExec["startedOn"])
                    else:
                        listOfTimeStarted.append("NOTSTARTED")
                    if 'executedBy' in testfromtestExec:
                        executerOnPremisseUsername = testfromtestExec['executedBy']
                        try:
                            executerOnPremisseUser= jira.user(executerOnPremisseUsername)
                        except:
                            logging.info("Couldn't retrieve user :" + executerOnPremisseUsername  + " using default user : " + GLOBAL_defaultUser)
                            executerOnPremisseUser= jira.user(GLOBAL_defaultUser)

                        responseForUser = requests.get('' + GLOBAL_onCloudMig+'rest/api/3/user/search?query=' + str(executerOnPremisseUser.emailAddress) +'', auth=HTTPBasicAuth(GLOBAL_cloudUser, GLOBAL_apitoken) )
                        json_data_user = json.loads(responseForUser.text)
                        if len(json_data_user) == 1:
                            # found one user
                            listOfExecuter.append( json_data_user[0]['accountId'])
                        else:
                            listOfExecuter.append("NOTEXECUTER")
                        
                    else:
                        listOfExecuter.append("NOTEXECUTER")
                    if 'assignee' in testfromtestExec:
                        assigneeOnPremisseUsername = testfromtestExec['assignee']
                        try:
                            assigneeOnPremisseUser= jira.user(assigneeOnPremisseUsername)
                        except:
                            logging.info("Couldn't retrieve user :" + assigneeOnPremisseUsername  + " using default user : " + GLOBAL_defaultUser)
                            assigneeOnPremisseUser= jira.user(GLOBAL_defaultUser)

                        responseForAssignee = requests.get('' + GLOBAL_onCloudMig+'/rest/api/3/user/search?query=' + str(assigneeOnPremisseUser.emailAddress) +'',  auth=HTTPBasicAuth(GLOBAL_cloudUser, GLOBAL_apitoken))
                        json_data_user = json.loads(responseForAssignee.text)
                        if len(json_data_user) == 1:
                            # found one user
                            listOfAssignee.append(json_data_user[0]['accountId'])   
                        else:
                            listOfAssignee.append("NOTASSIGNEE")                    
                    else:
                        listOfAssignee.append("NOTASSIGNEE")
                      
                    ##
                    if cloudExec.id not in listofExe :
                        listofExe.append(cloudExec.id)
                    ## Processs Defects
                    if not commandExecutionExceptions.defects:
                        logging.info("[Getting detail for sync] - Defects associated with run....")
                        logging.debug(testfromtestExec["defects"])
                        if len(testfromtestExec["defects"]) > 0:
                            listOfDefectsForTest = []
                            for defect in testfromtestExec["defects"]:
                                listOfDefectsForTest.append(defect['key'])
                            listOfDefect.append(listOfDefectsForTest)
                        else:
                            listOfDefect.append("NODEFECT") 
                    else:
                        listOfDefect.append("NODEFECT")
                    #Defects
                    ## evidences
                    
                    # Check if its to process evidences
                    if not commandExecutionExceptions.evidences:
                        logging.info("[Getting detail for sync] - Evidences associated with run....")
                        logging.debug(testfromtestExec["evidences"])
                        if len(testfromtestExec["evidences"]) > 0:
                            listOfEvidencesForTest = []
                            for evidence in testfromtestExec["evidences"]:
                                listOfEvidencesForTest.append(evidence['fileURL']  + "##NAME##" + evidence['fileName'])
                            listOfEvidences.append(listOfEvidencesForTest)
                        else:
                            listOfEvidences.append("NODEVIDENC")
                    else:
                        listOfEvidences.append("NODEVIDENC")

                    #evidences
                    ## comments
                    # Check if its to process comments
                    if not commandExecutionExceptions.comments:
                        logging.info("[Getting detail for sync] - comements associated with run....")
                        y = requests.get('' + GLOBAL_onPremiseURL+'/rest/raven/1.0/api/testrun/'+str(testfromtestExec["id"]) +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
                        runDetail = json.loads(y.text)
                        if runDetail.get("comment")  is not None:
                            listOfCommentsForTest.append(runDetail['comment'])
                        else:
                            listOfCommentsForTest.append("NOCOMMENT")
                    else:
                        listOfCommentsForTest.append("NOCOMMENT")                      
                    ## comments  

                    #step
                    listOfDefectSteps[cloudTest.id]="NODEFECTSTEP"
                    listOfCommentsSteps[cloudTest.id]="NOCOMMENTSTEP"
                    listOfEvidencesStep[cloudTest.id]="NOEVIDENCESTEP"
                    listOfStatusSteps[cloudTest.id]="NOSTATUSTSTEP"
                    if not commandExecutionExceptions.steps and not listOfTestsTogetDetails or (listOfTestsTogetDetails and testfromtestExec["key"] in listOfTestsTogetDetails):
                        logging.info("Validating if it has steps associated with test...")
                        z = requests.get('' + GLOBAL_onPremiseURL+'/rest/raven/1.0/api/testrun/'+str(testfromtestExec["id"]) +'/step', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
                        if z.text == "" or z.text == None or z.text=="[]":
                            logging.info("[Getting detail for sync] - No steps associated")
                        else :
                            logging.info("[Getting detail for sync] - Steps details...")
                            json_steps = json.loads(z.text)
                            commentWithSteps = 0
                            statusStep = 0
                            defectStep = 0
                            evidenceStep = 0
                            dicOfStepsComments={}
                            dicOfStepsStatus={}
                            dicOfStepDefects={}
                            dicOfStepEvidences={}
                            for step in json_steps:                              
                                logging.info("[Getting detail for sync] - Defect Steps details...")
                                if not commandExecutionExceptions.stepdefects:                                   
                                    if len(step['defects']) > 0 :
                                        defectStep = 1
                                        listOfDefectsForTeststep= []
                                        for defect in step["defects"]:
                                            listOfDefectsForTeststep.append(defect['key'])
                                        #dicOfSteps = {}
                                        dicOfStepDefects[step['index']] = str(listOfDefectsForTeststep).replace('\'','\"')
                                        #listOfDefectSteps[cloudTest.id] = dicOfSteps
                                    else:
                                        listOfDefectSteps[cloudTest.id]="NODEFECTSTEP"
                                else:
                                    listOfDefectSteps[cloudTest.id]="NODEFECTSTEP"                                 
                                #step comments
                                logging.info("[Getting detail for sync] - Comments Steps details...")                              
                                if not commandExecutionExceptions.stepcomments:
                                    if len(step['comment']) > 0 :
                                        commentWithSteps = 1
                                        if hasattr(step['comment'], 'raw'):
                                            dicOfStepsComments[step['index']] = step['comment']['raw']
                                        else:
                                            dicOfStepsComments[step['index']]=""
                                    else:
                                        listOfCommentsSteps[cloudTest.id]="NOCOMMENTSTEP"
                                else:
                                    listOfCommentsSteps[cloudTest.id]="NOCOMMENTSTEP"
                                # evidences
                                logging.info("[Getting detail for sync] - Evidences Steps details...")
                                if not commandExecutionExceptions.stepevidences:
                                    if len(step['evidences']) > 0 :
                                        evidenceStep = 1
                                        listOfEvidencesForTeststep= []
                                        for evidenceStep in step["evidences"]:
                                            listOfEvidencesForTeststep.append(evidenceStep['fileURL'] + "##NAME##" + evidenceStep['fileName'])
                                        #dicOfSteps = {}
                                        dicOfStepEvidences[step['index']] = listOfEvidencesForTeststep
                                        #listOfEvidencesStep[cloudTest.id] = dicOfSteps
                                    else:
                                        listOfEvidencesStep[cloudTest.id]="NOEVIDENCESTEP"
                                else:
                                    listOfEvidencesStep[cloudTest.id]="NOEVIDENCESTEP"     
                                ## Status
                                logging.info("[Getting detail for sync] - Status Steps details...")                              
                                if not commandExecutionExceptions.stepstatus:
                                    if len(step['status']) > 0 :
                                        statusStep = 1
                                        dicOfStepsStatus[step['index']] = step['status']
                                    else:
                                        listOfStatusSteps[cloudTest.id]="NOSTATUSTSTEP"
                                else:
                                    listOfStatusSteps[cloudTest.id]="NOSTATUSTSTEP"                               
                            if commentWithSteps == 1:
                                listOfCommentsSteps[cloudTest.id] = dicOfStepsComments
                            if statusStep == 1:
                                listOfStatusSteps[cloudTest.id] = dicOfStepsStatus
                            if defectStep == 1:
                                listOfDefectSteps[cloudTest.id] = dicOfStepDefects
                            if evidenceStep == 1:
                                listOfEvidencesStep[cloudTest.id] = dicOfStepEvidences
                        #step 
                    
                   
            page += 1
            # Pack and send to server association bettweeen test executions and all tests found OnPremise
            logging.info("Execution Sync of Test execution details and test association on Cloud...")
            packUpdateandSend(headers,GLOBAL_url_xray,mutation)
            mutation =""
            logging.info("Starting to pack test run details...")
            ts = str(listoftests).replace('\'','\"')
            ex = str(listofExe).replace('\'','\"')
            logging.info("Get test runs for tests inside the Test execution")
            # need to do a 100 + 100
            fullList = listoftests
            numberOfIterations=len(fullList)/100
            numberOfIterationsRounded = math.ceil(numberOfIterations)
            arrayOfArraysofIds = np.array_split(listoftests, numberOfIterationsRounded)
            for arrayOfIds in arrayOfArraysofIds:
                ids='["' + '","'.join(arrayOfIds) + '"]'
                ts = ids.replace('\'','\"')
                testRuns = GetTestRuns(headers,GLOBAL_url_xray,ts,ex)
                for testrun in testRuns:
                    logging.info("Lopping for each test run...")
                    # Get Index of test associated with current test run
                    index = listoftests.index(testrun['test']['issueId'])
                    logging.info("Processing Test run of : "  + listofkeysInCloud[index])

                   
                    #defects
                    logging.info("[Sync Test Run] - Defects....")
                    defects = listOfDefect[index]
                    formatedListOfDefects = str(defects).replace('\'','\"')
                    logging.debug("List of defects :" + formatedListOfDefects)
                    if formatedListOfDefects != "NODEFECT":
                        mutation = addDefectsToTestRun(headers,mutation,testrun['id'], formatedListOfDefects)
                    
                    #evidences
                    logging.info("[Sync Test Run] - Evidences....")
                    evidences = listOfEvidences[index]
                    logging.debug("List of Evidences " + str(evidences))
                    if len(evidences) > 0 and str(evidences)!="NODEVIDENC":
                        iter = 1
                        for evidence in evidences:
                            evidenceURL =  evidence.split("##NAME##")[0]
                            evidenceName =  evidence.split("##NAME##")[1]
                            mutation = addEvidenceToTestRun(headers,mutation,testrun['id'], evidenceName, evidenceURL)
                            iter=iter+1
                    
                    
                    #steps defects
                    defectStepsDic = []
                    defectStepsDic = listOfDefectSteps[testrun['test']['issueId']]
                    logging.info("[Sync Test Run Steps] - ....")
                    logging.info("[Sync Test Run Steps] - Defects...")
                    if len(defectStepsDic) > 0 and str(defectStepsDic)!="NODEFECTSTEP":
                        iter = 1
                        for step in testrun['steps']:
                            if defectStepsDic.get(iter) is not None:
                                mutation= addDefectsToTestRunStep(headers,mutation,step['id'], defectStepsDic.get(iter),testrun['id'])
                            iter=iter+1
                    #steps comments
                    logging.info("[Sync Test Run Steps] - Comments...")
                    commentsStepsDic = []
                    commentsStepsDic = listOfCommentsSteps[testrun['test']['issueId']]
                    if len(commentsStepsDic) > 0 and str(commentsStepsDic)!="NOCOMMENTSTEP":
                        iter = 1
                        for step in testrun['steps']:
                            if commentsStepsDic.get(iter) is not None:
                                if commentsStepsDic.get(iter) != "":
                                    mutation= updateTestRunStepComment(headers,mutation,step['id'], commentsStepsDic.get(iter),testrun['id'])
                            iter=iter+1
                    #steps evidences
                    logging.info("[Sync Test Run Steps] - Evidences...")
                    eviStepsDic = []
                    eviStepsDic = listOfEvidencesStep[testrun['test']['issueId']]
                    if len(eviStepsDic) > 0 and str(eviStepsDic)!="NOEVIDENCESTEP":
                        iter = 1
                        for step in testrun['steps']:
                            iter=iter+1
                            if eviStepsDic.get(iter) is not None:                            
                                evidencesList = eviStepsDic.get(iter)
                                for evidence in evidencesList:
                                    evidenceURL =  evidence.split("##NAME##")[0]
                                    evidenceName =  evidence.split("##NAME##")[1]
                                    mutation = addEvidenceToTestRunStep(headers,mutation,testrun['id'], evidenceName, evidenceURL,randomString(),step['id'])
                    # status
                    statusStepsDic = []
                    statusStepsDic = listOfStatusSteps[testrun['test']['issueId']]
                    
                    logging.info("[Sync Test Run Steps] - Status...")
                    if len(statusStepsDic) > 0 and str(statusStepsDic)!="NOSTATUSTSTEP":
                        iter = 1
                        for step in testrun['steps']:
                            if statusStepsDic.get(iter) is not None:
                                stepStatus = statusStepsDic.get(iter).strip()
                                if  statusStepsDic.get(iter).strip() in GLOBAL_statusStepXray:
                                    stepStatus = GLOBAL_statusStepXray[statusStepsDic.get(iter).strip()]
                                if stepStatus != GLOBAL_StepInitialStatus:
                                    mutation= updateTestRunStepStatus(headers,mutation,step['id'], stepStatus,testrun['id'])
                                else:
                                    logging.info("Not updating status...its in initial step.")
                            iter=iter+1

                     # Get status of test run based in index.
                    status = listOfStatus[index] 
                    finishedOn = listOfTimeFinished[index] 
                    startedOn = listOfTimeStarted[index]
                    executer = listOfExecuter[index] 
                    assignee = listOfAssignee[index] 
                    comment = listOfCommentsForTest[index]  
                    logging.info("[Sync Test Run] - Status....")
                    ### WriteToFile
                    if str(startedOn)!="NOTSTARTED":
                        if  status in GLOBAL_statusXray:
                            mutation = addTestRunStatus(headers,mutation,testrun['id'], GLOBAL_statusXray[status])
                        else:
                            mutation = addTestRunStatus(headers,mutation,testrun['id'], status)

                    #comments
                    logging.info("[Sync Test Run] - Comments....")
                    finishedOn = "" if finishedOn == "NOTFINISHED" else finishedOn
                    startedOn = "" if startedOn == "NOTSTARTED" else finishedOn
                    assignee = "" if assignee == "NOTASSIGNEE" else assignee
                    executer = "" if executer == "NOTEXECUTER" else executer
                    comment = "" if comment == "NOCOMMENT" else comment
                    mutation = updateTestRun(headers,mutation,testrun['id'], startedOn, finishedOn, assignee, executer, comment)


            packUpdateandSend(headers,GLOBAL_url_xray,mutation)
            mutation=""
        logging.info("Completed Processing OnPremise Test Execution : " + issue.key)
        if commandExecutionExceptions.export != None:
                fileExport.write("%s\n" % issue.key)
                fileExport.flush()
        logging.info('It took ' + str(time.time()-startExec) + 'seconds for processing :' + issue.key)
        count = count +1
        logging.info('Done ' + str(count) + ' of ' + str(issues.total) ) 
        keyStats.append(issue.key)
        timeStats.append(time.time()-startExec)
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
    print("------------------- #####    STATISTICS  - Full list  ##### ------------------- ")
    print (df)
    print("------------------- #####    STATISTICS  - Global statistics  ##### ------------------- ")

    print (df.describe())
    
if commandExecutionExceptions.export != None:
    fileExport.close()
print('It took ', time.time()-start, 'seconds.')

            