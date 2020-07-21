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
import logging
import random
import string
import base64
from xray_variables import *
import base64
import mimetypes 
import xray_variables
import time
import sys
import os.path
from os import path



logging.basicConfig(level=logging.INFO)

def addTestExecutionsToTestPlan(headers,execid, planid,alias,mutation):
    logging.debug("Adding Test Plan to Test")
    mutation = mutation  + " "+ alias + ": addTestExecutionsToTestPlan( " \
        "       issueId: \""+ planid  +"\", " \
        "       testExecIssueIds: [\"" + execid +"\"] " \
        "       ) { " \
        "       addedTestExecutions " \
        "       warning " \
        "   }"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +2
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addTestToPlan(headers,test, planID,alias,mutation):
    logging.debug("Adding Test Plan to Test")
    mutation = mutation  + " "+ alias + ": addTestPlansToTest( " \
        "       issueId: \""+ test  +"\", " \
        "       testPlanIssueIds: [\"" + planID +"\"] " \
        "       ) { " \
        "       addedTestPlans " \
        "       warning " \
        "   }"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +2
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addTestSetsToTest(headers,test, setID,alias, mutation):
    logging.debug("Adding Test Sets to Test")
    mutation= mutation  + " "+ alias + ": addTestSetsToTest( " \
        "       issueId: \""+ test  +"\", " \
        "       testSetIssueIds: [\"" + setID +"\"] " \
        "       ) { " \
        "       addedTestSets " \
        "       warning " \
        "   }"
    logging.debug("Mutation " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +2
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addPreconditionsToTest(headers,test, pre_cond,alias,mutation):
    logging.debug("Adding PreConditions to Test")
    mutation= mutation  + " "+ alias + ": addPreconditionsToTest( " \
        "       issueId: \""+ test +"\", " \
        "       preconditionIssueIds: [\"" + pre_cond +"\"] " \
        "       ) { " \
        "       addedPreconditions " \
        "       warning " \
        "   }"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter+2
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


## Mutations for Test definition update
def addToGenericTestUpdate(headers,id,type,definition,mutation,key):
    logging.info("Adding Generic Tests details to mutation")
    defencoded = definition.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')

    mutation = mutation + " "+ randomString(10) + ": updateTestType(" \
        "       issueId: \""+ id +"\", " \
        "       testType: {name:\"" + type +"\"} " \
        "       ) { " \
        "       issueId " \
        "       testType {" \
        "       name " \
        "       kind " \
        "   } " \
        "   }"
    mutation = mutation + " "+ randomString(10) + ": updateUnstructuredTestDefinition(" \
        "       issueId: \""+ id +"\", " \
        "       unstructured:  \"" + defencoded  + "\" " \
        "       ) { " \
        "       issueId " \
        "       unstructured " \
        "   }"
    logging.debug("Mutation " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +4
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


    ## Mutations for Test definition update
def packUpdateandSend(headers,url_xray,mutation):
    if mutation=="":
        logging.info("Nothing to send to server....skipping")
        return
    logging.info("======= Collecting INFO [STOP] =========")
    logging.info("======= Persisting information in Cloud [START] =========")
    start = time.time()
    logging.info("Pack mutation and push...")
    mutation= "mutation { " +  mutation  + "}"  
    #logging.info("mutation : " + mutation)
    r = None
    if GLOBAL_SIMULATE == False:
        while True:
            try:
                logging.info("Commiting...")    
                r = requests.post(url_xray, json={'query': mutation},headers=headers)
                #logging.info("Mutation being push: " + mutation)
                #logging.info(r.text)
                xray_exe = json.loads(r.text)
                if 'errors' in xray_exe:
                    if "No valid issues to add as defects" in r.text:
                        logging.error("Some issues were not added as they are not present in instance.")
                        logging.error(r.text)
                        logging.error("Mutation :" + mutation)
                    else:
                        logging.info("Ohh dear...")
                        logging.info(r.text)
                        sys.exit()
                if 'error' in xray_exe:
                    if "Too many requests in this time frame" in r.text:
                        logging.error("Too many requests...sleeping.")
                        time.sleep(5)
                        continue
            except:
                if not r:
                    logging.info("Retrying...")
                    logging.info(sys.exc_info())
                    continue
                if "502 Bad Gateway" in r.text  or "504 Gateway Time-out" in r.text:
                    logging.info(r.text)
                    logging.info("Retrying...")
                    continue
                else:
                    logging.info("Ohh dear...")
                    logging.info(r.text)
                    sys.exit()
            break
                
    logging.info('It took ' + str(time.time()-start) + 'seconds to commit.')
    logging.info("======= Persisting information in Cloud [END] =========")
    logging.info("======= Collecting INFO [START] =========")
    

def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



def addToCucumberTestUpdate(headers,ids,types,definition,mutation,key):
    logging.info("Adding Cucumber details to mutation")
    defencoded = definition.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')

    mutation = mutation + " "+ randomString(10) + ": updateTestType(" \
        "       issueId: \""+ ids +"\", " \
        "       testType: {name:\"" + types +"\"} " \
        "       ) { " \
        "       issueId " \
        "       testType {" \
        "       name " \
        "       kind " \
        "   } " \
        "   }"
    mutation = mutation + " "+ randomString(10) + ": updateGherkinTestDefinition(" \
        "       issueId: \""+ ids +"\", " \
        "       gherkin: \"" + defencoded  + " " +  "\" " \
        "       ) { " \
        "       issueId " \
        "       gherkin " \
        "   }"
        # extra space in definition is to handle terminations with 4" that would break the commit 
    #logging.info("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +4
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def updatePrecondition(headers,id,types,definition,mutation,key):
    logging.info("Adding Pre Condition details to mutation")
    defencoded = definition.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
    mutation = mutation + " "+ randomString(10) + ": updatePrecondition(" \
        "       issueId: \""+ id +"\", " \
        "       data: {preconditionType: {name:\"" + types +"\"}, definition:\"" + defencoded +  "\" }" \
        "       ) { " \
        "       issueId " \
        "       preconditionType  {" \
        "       name " \
        "       kind " \
        "   } " \
        "   definition " \
        "   }"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +3
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def addToManualTestTypeUpdate(headers,id,type,definition,mutation,key):
    # Needs to be reviwed after team fixes API
    logging.info("Adding Manual Tests details to mutation")
    mutation = mutation + " "+ randomString(10) + ": updateTestType(" \
        "       issueId: \""+ id +"\", " \
        "       testType: {name:\"" + type +"\"} " \
        "       ) { " \
        "       issueId " \
        "       testType {" \
        "       name " \
        "       kind " \
        "   } " \
        "   }"
    #logging.info(len(definition.steps))
    idStep=1
    stepMutationsCount=0
    for step in definition.steps:
        data=""
        steps=""
        result="" 
        ## handling exceptions...
        if (xray_variables.GLOBAL_XrayVersionIsObove4 == "Yes"):
            if hasattr(step.fields, 'Action'):
                steps = step.fields.Action
            if hasattr(step.fields, 'Data'):
                data = step.fields.Data
            if hasattr(step.fields, 'Expected Result'):
                result = getattr(step.fields, 'Expected Result')
        else:
            if hasattr(step, 'step'):
                steps = step.step
            if hasattr(step, 'data'):
                data = step.data
            if hasattr(step, 'result'):
                result = step.result
        

        if  len(data) > 8192:
            data = (data[:8190] + '..')
            logging.warning("Truncating data in step definition as its bigger than 8192 characters")
        if  len(steps) > 8192:
            steps = (steps[:8190] + '..')
            logging.warning("Truncating step in step definition as its bigger than 8192 characters")
        if  len(result) > 8192:
            result = (result[:8190] + '..')
            logging.warning("Truncating result in step definition as its bigger than 8192 characters")
        steps = steps.replace('"""', '""')
        data = data.replace('"""', '""')
        result = result.replace('"""', '""')

        #logging.info("Step : " + step.step) 
        #logging.info("Data : " + step.data) 
        #logging.info("Result :" + step.result) 
       # logging.debug("Attachment :" + str(len(step.attachments)))
        attachmentDetails=""
        if hasattr(step, 'attachments') and len(step.attachments)>0 :
            fileToBig = False
            for attachment in step.attachments:      
                #logging.info("" + onPremiseURL+"/plugins/servlet/raven/attachment/"+ str(attachment.id) +"/" + attachment.fileName +'')
                r = requests.get('' + GLOBAL_onPremiseURL+'/plugins/servlet/raven/attachment/'+ str(attachment.id) +'/' + attachment.fileName +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
                cleanBase64Image=str(get_as_base64(r.content))
                cleanBase64Image=cleanBase64Image[2:-1]
                #logging.info("size : " + str(size64(cleanBase64Image)))
                if size64(cleanBase64Image) > xray_variables.GLOBAL_MAX_ATTACH_SIZE:
                   logging.error("###### File is to big ...skipping")
                   fileToBig = True
                addMimeType()
                mime= mimetypes.guess_type(attachment.fileName, strict=True)[0]
                if mime is None:
                    logging.info("adding a default mime")
                    mime="application/octet-stream"
                attachmentDetails= attachmentDetails +  "{filename:\"" + attachment.fileName + "\" mimeType:\""+ mime +"\" data:\""+ cleanBase64Image +"\"},"
                #attachmentDetails= "[{filename:\"" + attachment.fileName + "\" mimeType:\""+ mime +"\" data:\""+ cleanBase64Image +"\"}]"

                #logging.info(mimetypes.guess_type(attachment.fileName, strict=True)[0])
                #logging.info(attachmentDetails)
                #attachmentDetails= "[{filename:oi,mimeType:sss, data:sss}]"

                #logging.info(attachmentDetails)
        if hasattr(step, 'attachments') and len(step.attachments)>0 and not fileToBig:
            attachmentDetails = attachmentDetails[:-1]
            attachmentDetails ="[" + attachmentDetails + "]"
            dataDec = data.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
            resultDec = result.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
            stepsDec = steps.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')

            mutation = mutation + " "+ randomString(10) + ": addTestStep(" \
            "       issueId: \""+ id +"\", " \
            "       step : {action:\"" + stepsDec + "\", "\
            "       data:\"" +  dataDec + "\", "\
            "       attachments:" + attachmentDetails  +", "\
            "       result:\"" +  resultDec +  "\"} "\
            "       ) { " \
            "       id " \
            "       action " \
            "       data " \
            "       result " \
            "   }"
            #stepMutationsCount = stepMutationsCount + 3
            # if adding a file psuh it at once..do not accumulate or we could go above the limit.
            packUpdateandSend(headers,GLOBAL_url_xray,mutation)
            mutation=""
            xray_variables.GLOBAL_mutation_counter = 0
        else :
            #logging.info("data :"  + data)
            #logging.info("resultDec :"  + result)
            #logging.info("stepsDec :"  + steps)
            dataDec = data.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
            resultDec = result.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
            stepsDec = steps.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
            mutation = mutation + " "+ randomString(10) + ": addTestStep(" \
            "       issueId: \""+ id +"\", " \
            "       step : {action:\"" +  stepsDec + "\", " \
            "       data:\"" +  dataDec +"\", " \
            "       result:\"" +  resultDec +"\"} " \
            "       ) { " \
            "       id " \
            "       action " \
            "       data " \
            "       result " \
            "   }"
            stepMutationsCount = stepMutationsCount + 2
        xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter + 2 + stepMutationsCount
        if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
            packUpdateandSend(headers,GLOBAL_url_xray,mutation)
            mutation=""
            xray_variables.GLOBAL_mutation_counter = 0
            stepMutationsCount = 0
        idStep=idStep+1
       # print("tests" + test)
   # r = requests.post(url_xray, json={'query': mutation},headers=headers)
    #logging.info("mutation " + mutation)
    #logging.info(r.text)
   
    return mutation

def get_as_base64(text):
    return base64.b64encode(text)



def addTestToTestExecution(headers,mutation,test, exec,alias):
    logging.debug("Adding Test to Test execution")
    mutation = mutation  + " "+ alias + ": addTestExecutionsToTest( " \
        "       issueId: \""+ test +"\", " \
        "       testExecIssueIds: [\"" + exec +"\"] " \
        "       ) { " \
        "       addedTestExecutions " \
        "       warning " \
        "   }"
    logging.debug("Mutation: " + mutation)
    #xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    #if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
    packUpdateandSend(headers,GLOBAL_url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def removeTestExecutionsFromTest(headers,mutation,test, exec,alias):
    logging.debug("Remove Test execution from Test")
    mutation = mutation  + " "+ alias + ": removeTestExecutionsFromTest( " \
        "       issueId: \""+ test +"\", " \
        "       testExecIssueIds: [\"" + exec +"\"] " \
        "       ) "

    #logging.info("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def removeTestEnvironmentsToTestExecution(headers,mutation,test, env,alias):
    env = env.replace(' ', '')
    if  len(env) > 22:
        tmp = env
        tmp = tmp.replace('"', '').replace('[', '').replace(']', '')
        tmpListOfEnv = tmp.split(',')
        newListOfEnv =[]
        for typee in tmpListOfEnv:
            if len(typee) > 18:
                newListOfEnv.append('"' + typee[:18] + '"')
            else:
                newListOfEnv.append('"' + typee + '"')
        env = ','.join(newListOfEnv)
        env =  '[' + env + ']'
    env = env.replace(' ', '')
            
    logging.debug("remove Test Environments To TestExecution")
    mutation = mutation  + " "+ alias + ": removeTestEnvironmentsFromTestExecution( " \
        "       issueId: \""+ test +"\", " \
        "       testEnvironments: " + env +" " \
        "       ) "
       # print("tests" + test)
    #logging.info("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def addTestEnvironmentsToTestExecution(headers,mutation,test, env):
    env = env.replace(' ', '')
    if  len(env) > 22:
        tmp = env
        tmp = tmp.replace('"', '').replace('[', '').replace(']', '')
        tmpListOfEnv = tmp.split(',')
        newListOfEnv =[]
        for typee in tmpListOfEnv:
            if len(typee) > 18:
                newListOfEnv.append('"' + typee[:18] + '"')
            else:
                newListOfEnv.append('"' + typee + '"')
        env = ','.join(newListOfEnv)
        env =  '[' + env + ']'
    env = env.replace(' ', '')
            
    logging.debug("add Test Environments To TestExecution")
    mutation = mutation  + " "+ randomString() + ": addTestEnvironmentsToTestExecution( " \
        "       issueId: \""+ test +"\", " \
        "       testEnvironments: " + env +" " \
        "       ) { " \
        "       associatedTestEnvironments " \
        "       createdTestEnvironments " \
        "       warning " \
        "   }"
       # print("tests" + test)
    #logging.info("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def GetTestRuns(headers,url_xray,listofTests,testExec):
    logging.debug("Get test runs")
    query_xray = "{" \
    " getTestRuns(testIssueIds: " + listofTests + ", testExecIssueIds: " + testExec + ", limit: 100) { " \
    "   total" \
    "   start" \
    "   limit" \
    "   results {" \
    "        id" \
    "        status {" \
    "           name" \
    "    }" \
    "        test {" \
    "           issueId" \
    "    }" \
    "        steps  {" \
    "           id" \
    "    }" \
    "        testExecution  {" \
    "           issueId" \
    "    }" \
    "    }" \
    "   }" \
    "}"
    logging.debug(query_xray)
    
    while True:
        try:
            logging.info("Retrieving data...")
            r = requests.post(url_xray, json={'query': query_xray},headers=headers)
            xray_exe = json.loads(r.text)
            if 'errors' in xray_exe:
                logging.info("Ohh dear...")
                logging.info(r.text)
                sys.exit()
        except:
            if "502 Bad Gateway" in r.text :
                    logging.info(r.text)
                    logging.info("Retrying...")
                    continue
            else:
                logging.info("Ohh dear...")
                logging.info(r.text)
                sys.exit()
        if 'data' not in xray_exe:
            if "Too many requests in this time frame" in r.text:
                logging.error("Too many requests...sleeping.")
                logging.error(r.text)
                time.sleep(5)
                continue
            else:
                logging.info("Ohh dear...")
                logging.info(xray_exe)
                sys.exit()
        break
    return xray_exe['data']['getTestRuns']['results']

def GetTestRun(headers,test,exec):
    start = time.time()
    logging.debug("Get test runs")
    query_xray = "{" \
    " getTestRun(testIssueId: \"" + test + "\", testExecIssueId: \"" + exec + "\") { " \
    "   id" \
    "   status {" \
    "        name" \
    "        color " \
    "        description" \
    "    }" \
    "   steps {" \
    "        id" \
    "    }" \
    "}" \
    "}"
    #logging.info(query_xray)
    logging.debug(query_xray)

  
    while True:
        try:
            logging.info("Retrieving data...")
            r = requests.post(GLOBAL_url_xray, json={'query': query_xray},headers=headers)
            xray_exe = json.loads(r.text)
            #logging.info(r.text)
        except:
            if "502 Bad Gateway" in r.text :
                    logging.info(r.text)
                    logging.info("Retrying...")
                    continue
            else:
                logging.info("Ohh dear...")
                logging.info(r.text)
                sys.exit()
        #logging.info(r.text)
        if 'data' not in xray_exe:
            if "Too many requests in this time frame" in r.text:
                logging.error("Too many requests...sleeping.")
                logging.error(r.text)
                time.sleep(5)
                continue
            else:
                logging.info("Ohh dear...")
                logging.info(xray_exe)
                sys.exit()
        break
    
    logging.info('It took ' + str(time.time()-start) + 'seconds to retrive information.')
    return xray_exe['data']['getTestRun']


def addTestRunStatus(headers,mutation,run, status):
    logging.debug("Updating test run status")
    mutation = mutation  + " "+  randomString() + ": updateTestRunStatus( " \
        "       id: \""+ run +"\", " \
        "       status: \"" + status +"\" " \
        "       ) "
       # print("tests" + test)
    #logging.info("Mutation " + mutation)
    #xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    #if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
    packUpdateandSend(headers,GLOBAL_url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addDefectsToTestRun(headers,mutation,run, defects):
    logging.debug("Adding defects to test run")
    logging.info("Defects : " + defects)
    mutation = mutation  + " "+ randomString() + ": addDefectsToTestRun( " \
        "       id: \""+ run +"\", " \
        "       issues: " + defects +" " \
        "       ) { " \
        "       addedDefects " \
        "       warnings " \
        "   }"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addEvidenceToTestRun(headers,mutation,run, fileName,fileURL):
    logging.debug("Adding Evidence To TestRun")

    if not fileURL or fileURL == "":
        logging.error("Missing file path...skipping")
        return mutation
    r = requests.get('' + fileURL +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
    cleanBase64Image=str(get_as_base64(r.content))
    cleanBase64Image=cleanBase64Image[2:-1]
    if size64(cleanBase64Image) > xray_variables.GLOBAL_MAX_ATTACH_SIZE:
            logging.error("###### File is to big ...skipping")
            return mutation

    addMimeType()
    mime= mimetypes.guess_type(fileName, strict=True)[0]
    if mime is None:
        logging.info("adding a default mime")
        mime="application/octet-stream"
    logging.error("minme" + mime)
    logging.error("fileName" + fileName)
    logging.error("run" + run)

    attachmentDetails= "[{filename:\"" + fileName+ "\" mimeType:\""+ mime +"\" data:\""+ cleanBase64Image +"\"}]"
    mutation = mutation  + " "+ randomString() + ": addEvidenceToTestRun( " \
        "       id: \""+ run +"\", " \
        "       evidence: " + attachmentDetails +" " \
        "       ) { " \
        "       addedEvidence " \
        "       warnings " \
        "   }"
    logging.debug("Mutation " + mutation)
    # Push always you have a file.
    packUpdateandSend(headers,GLOBAL_url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0


    return mutation

def addDefectsToTestRunStep(headers,mutation,run, defects,testRunId):
    logging.debug("Adding Defects To Test Run Step")
    mutation = mutation  + " "+ randomString() + ": addDefectsToTestRunStep( " \
        "       testRunId: \""+ testRunId +"\", " \
        "       stepId: \""+ run +"\", " \
        "       issues: " + defects +" " \
        "       ) { " \
        "       addedDefects " \
        "       warnings " \
        "   }"
    logging.debug("Mutation " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def updateTestRunStepComment(headers,mutation,run, comment,testRunId):
    logging.debug("update Test Run Step Comment")
    mutation = mutation  + " "+ randomString() + ": updateTestRunStepComment( " \
        "       testRunId: \""+ testRunId +"\", " \
        "       stepId: \""+ run +"\", " \
        "       comment: \"\"\"" + comment + " " + "\"\"\" )"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def updateTestRunStepStatus(headers,mutation,run, status,testRunId):
    logging.debug("update Test Run Step Comment")
    mutation = mutation  + " "+ randomString() + ": updateTestRunStepStatus( " \
        "       testRunId: \""+ testRunId +"\", " \
        "       stepId: \""+ run +"\", " \
        "       status: \"" + status + "\" ) { " \
        "       warnings " \
        "   }"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def updateTestRunComment(headers,mutation,run, status,alias):
    logging.debug("update Test Run Comment")
    mutation = mutation  + " "+ alias + ": updateTestRunComment( " \
        "       id: \""+ run +"\", " \
        "       comment: \"\"\"" + status + " " + "\"\"\" )"
    logging.debug("Mutation: " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def addEvidenceToTestRunStep(headers,mutation,run, fileName,fileURL ,alias,stepid):
    logging.debug("add Evidence To Test RunStep")

    logging.debug("File Name " + fileName)
    logging.debug("File URL " + fileURL)
    r = requests.get('' + fileURL +'', auth=HTTPBasicAuth(GLOBAL_basic_auth_user, GLOBAL_basic_auth_pass))
    cleanContent=str(get_as_base64(r.content))
    cleanContent=cleanContent[2:-1]
    if size64(cleanContent) > xray_variables.GLOBAL_MAX_ATTACH_SIZE:
            logging.error("###### File is to big ...skipping")
            return mutation
    mime= mimetypes.guess_type(fileName, strict=True)[0]
    if mime is None:
        logging.info("Adding a default mime")
        mime="application/octet-stream"
    #attachmentDetails= "[{filename:\"" + fileName+ "\" mimeType:\""+ mimetypes.guess_type(fileName, strict=True)[0] +"\" data:\""+ str(get_as_base64(r.content)) +"\"}]"
    attachmentDetails= "[{filename:\"" + fileName+ "\" mimeType:\""+ mime +"\" data:\""+ cleanContent +"\"}]"
    mutation = mutation  + " "+ alias + ": addEvidenceToTestRunStep( " \
        "       testRunId: \""+ run +"\", " \
        "       stepId: \""+ stepid +"\", " \
        "       evidence: " + attachmentDetails +" " \
        "       ) { " \
        "       addedEvidence " \
        "       warnings " \
        "   }"
    logging.debug("Mutation: " + mutation)
    # Push always you have a file.
    packUpdateandSend(headers,GLOBAL_url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def size64(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)

def addMimeType():
    mimetypes.add_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.xlsx')
    mimetypes.add_type('application/java-archive','.jar')

def createFolder(headers,url_xray,projectID, path,mutation):
    logging.debug("Adding folder to repository")
    mutation = mutation  + " "+ randomString() + ": createFolder( " \
        "       projectId: \""+ projectID  +"\", " \
        "       path: \"" + path +"\" " \
        "       ) { " \
        "       folder { " \
        "       name " \
        "       path " \
        "       testsCount " \
        "       }" \
        "       warnings " \
        "   }"
    #logging.info("Mutation: " + mutation)
   
    packUpdateandSend(headers,url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addTestsToFolder(headers,projectID, path,testIssueIds,mutation):
    logging.debug("Adding Test to Folder")
    mutation = mutation  + " "+ randomString() + ": addTestsToFolder( " \
        "       projectId: \""+ projectID  +"\", " \
        "       path: \"" + path +"\" " \
        "       testIssueIds: " + testIssueIds +" " \
        "       ) { " \
        "       folder { " \
        "       name " \
        "       path " \
        "       testsCount " \
        "       }" \
        "       warnings " \
        "   }"
    #logging.info("Mutation: " + mutation)
    packUpdateandSend(headers,GLOBAL_url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def createPlanFolder(headers,url_xray,plandID, path,mutation):
    logging.debug("Adding folder to repository")
    mutation = mutation  + " "+ randomString() + ": createFolder( " \
        "       testPlanId: \""+ plandID  +"\", " \
        "       path: \"" + path +"\" " \
        "       ) { " \
        "       folder { " \
        "       name " \
        "       path " \
        "       testsCount " \
        "       }" \
        "       warnings " \
        "   }"
    #logging.info("Mutation: " + mutation)
   
    packUpdateandSend(headers,url_xray,mutation)
    mutation=""
    xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def addTestsToPlanFolder(headers,plandID, path,testIssueIds,mutation):
    logging.debug("Adding Test to Folder")
    
    mutation = mutation  + " "+ randomString() + ": addTestsToFolder( " \
        "       testPlanId: \""+ plandID  +"\", " \
        "       path: \"" + path +"\" " \
        "       testIssueIds: " + testIssueIds +" " \
        "       ) { " \
        "       folder { " \
        "       name " \
        "       path " \
        "       testsCount " \
        "       }" \
        "       warnings " \
        "   }"
    #logging.info("Mutation: " + mutation)
    
    #packUpdateandSend(headers,url_xray,mutation)
    #mutation=""
    #xray_variables.GLOBAL_mutation_counter = 0
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter+1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation

def updateTestRun(headers,mutation,run, startedOn,finishedOn,assigneeId,executedById,comment):
    logging.debug("update Test Run")
    if startedOn == ""  and  finishedOn == "" and  assigneeId == ""  and comment == "" and executedById == "":
        logging.info("Nothing to update in test run details...")
        return mutation
    comment = comment.replace('\\','\\\\').replace('\n','\\n').replace('\r','').replace('"','\\"')
    mutation = mutation  + " "+  randomString() + ": updateTestRun(  id: \""+ run +"\", "
    if startedOn !="":
        mutation = mutation + " startedOn: \""+ startedOn +"\", "
    if finishedOn !="":
        mutation = mutation + " finishedOn: \""+ finishedOn +"\", "
    if assigneeId !="":
        mutation = mutation + " assigneeId: \""+ assigneeId +"\", "
    if comment !="":
        mutation = mutation + " comment: \""+ comment +"\", "
    if executedById !="":
        mutation = mutation + " executedById: \""+ executedById +"\", "

    mutation = mutation[:-2]
    mutation = mutation + ") { warnings }"

    #mutation = mutation  + " "+ alias + ": updateTestRun( " \
    #    "       id: \""+ run +"\", " \
    #    "       startedOn: \""+ startedOn +"\", " \
    #    "       finishedOn: \""+ finishedOn +"\", " \
    #    "       assigneeId: \""+ assigneeId +"\", " \
     #   "       comment: \""+ comment +"\", " \
     #   "       executedById: \"" + executedById + " " + "\" )"
    #logging.info("Mutation test run : " + mutation)
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation


def renewToken():
    response = requests.post('https://xray.cloud.xpand-it.com/api/v1/authenticate', data={"client_id": GLOBAL_client_id,"client_secret":GLOBAL_client_secret})
    token=response.text.replace("\"","")
    headers = {'Authorization':'Bearer %s' % token}
    logging.info("Token renewed.")
    return headers


def GetTest(headers,id):
    start = time.time()
    logging.debug("Get test runs")
    query_xray = "{" \
    " getTest(issueId: \"" + id + "\") { " \
    "   issueId" \
    "   steps {" \
    "        id" \
    "    }" \
    "}" \
    "}"
    logging.info(query_xray)
    logging.debug(query_xray)

  
    while True:
        try:
            logging.info("Retrieving data...")
            r = requests.post(GLOBAL_url_xray, json={'query': query_xray},headers=headers)
            xray_exe = json.loads(r.text)
            logging.info(r.text)
            if 'errors' in xray_exe:
                logging.info("Ohh dear...")
                logging.info(r.text)
                sys.exit()
        except:
            if "502 Bad Gateway" in r.text :
                    logging.info(r.text)
                    logging.info("Retrying...")
                    continue
            else:
                logging.info("Ohh dear...")
                logging.info(r.text)
                sys.exit()
        #logging.info(r.text)
        if 'data' not in xray_exe:
            if "Too many requests in this time frame" in r.text:
                logging.error("Too many requests...sleeping.")
                logging.error(r.text)
                time.sleep(5)
                continue
            else:
                logging.info("Ohh dear...")
                logging.info(xray_exe)
                sys.exit()
        break
    
    logging.info('It took ' + str(time.time()-start) + 'seconds to retrive information.')
    logging.info(xray_exe['data'])
    return xray_exe['data']['getTest']



def removeTestStepsFromTest(headers,mutation,testId):
    logging.debug("Remove Test steps from Test")
    mutation = mutation  + " "+ randomString(10) + ": removeAllTestSteps( " \
    "       issueId: \""+ testId +"\" " \
    "       ) "
    xray_variables.GLOBAL_mutation_counter  = xray_variables.GLOBAL_mutation_counter +1
    if xray_variables.GLOBAL_mutation_counter >= xray_variables.GLOBAL_maxMutationsForPack:
        packUpdateandSend(headers,GLOBAL_url_xray,mutation)
        mutation=""
        xray_variables.GLOBAL_mutation_counter = 0
    return mutation