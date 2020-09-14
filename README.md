## Description


## Prepare your environment for running the scripts

Install [Python 3.x](https://www.python.org/)

Note : You will need to install some extra modules as such you may want to create a python virtual environment for doing that I suggest reading of [Real python viertual environments](https://realpython.com/python-virtual-environments-a-primer/)  and [Python venv](https://docs.python.org/3/library/venv.html) 

## Required modules

- requests (pip install requests)
- jira (pip install jira)
- pyfiglet (pip install pyfiglet)
- pandas (pip install pandas)

## Assumptions/Requirements
[Get the entity properties from Xray Cloud issue types]( https://developer.atlassian.com/cloud/jira/platform/rest/v3/?utm_source=%2Fcloud%2Fjira%2Fplatform%2Frest&utm_medium=302#api-rest-api-3-issuetype-issueTypeId-properties-propertyKey-get)
- Assuming that migration to a cloud environment as been done using standard "export" and "import" of the XML instance or using [Cloud migration assistant](https://marketplace.atlassian.com/apps/1222010/jira-cloud-migration-assistant?hosting=server&tab=overview)
  There is one important item that you need to validate, **you need to make sure that your Issue types are been recognized by Xray**. 
  If you find in your instance reference to "Xray Test" Issue Type and other devivatives from it along side with the ones that you imported from server and if you don't see any functionalities of Xray in issues that you imported then **your imported issues are not recognized as Xray issues**.


  To fix this you will need to :


     - move (using standard move Jira functionality) all migrated issues linked to Xray OnPremise Issue types to the Xray Cloud issues Types , or 


     - or "transform" migrated Xray issue types into Xray Cloud issue types

      
          1) [Get the entity properties from Xray Cloud issue types]( https://developer.atlassian.com/cloud/jira/platform/rest/v3/?utm_source=%2Fcloud%2Fjira%2Fplatform%2Frest&utm_medium=302#api-rest-api-3-issuetype-issueTypeId-properties-propertyKey-get) and [set](https://developer.atlassian.com/cloud/jira/platform/rest/v3/?utm_source=%2Fcloud%2Fjira%2Fplatform%2Frest&utm_medium=302#api-rest-api-3-issuetype-issueTypeId-properties-propertyKey-put) them into migrated issue types
          
          2)Delete cloud Xray Issue Types  (all the ones that start with "Xray ..") 
          
          3)Reinstall Xray

          4)Perform a [Re-index](https://confluence.xpand-it.com/display/XRAYCLOUD/Project+Settings%3A+Re-Indexing). 
   

 - If you have migrated data to a cloud environment as been done using standard "export" and "import" of the XML instance or using [Cloud migration assistant](https://marketplace.atlassian.com/apps/1222010/jira-cloud-migration-assistant?hosting=server&tab=overview) 
 and you have not installed Xray then you will need to perform the below actions so that your imported issues are recognized as Xray Issue Types:
        
   1)Install Xray
       
   2)[Get the entity properties from Xray Cloud issue types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/?utm_source=%2Fcloud%2Fjira%2Fplatform%2Frest&utm_medium=302#api-rest-api-3-issuetype-issueTypeId-properties-propertyKey-get) and [set](https://developer.atlassian.com/cloud/jira/platform/rest/v3/?utm_source=%2Fcloud%2Fjira%2Fplatform%2Frest&utm_medium=302#api-rest-api-3-issuetype-issueTypeId-properties-propertyKey-put) them into migrated issue types
          
   3)Delete cloud Xray Issue Types  
          
   4)Reinstall Xray

   5)Perform a [Re-index](https://confluence.xpand-it.com/display/XRAYCLOUD/Project+Settings%3A+Re-Indexing). 
  
 - It may happen that the link type that was linking requirements to tests Onpremise is not recognized in cloud by Xray - makign the requirement coverage fail to provide the correct information. 
  This happens because when the user installs Xray it will look for the existance of the link Type "Test" (with "tests" as outward descriptin and "is tested by" as inward description) if it finds it associates that link type with Xray if it doesn't find it it creates a new Link type with that referred name and associates this Link Type as the Xray Link Type for linking requirements to tests.
  
     **If you didn't install Xray or migrated data to Cloud**
      - Before Migrate rename Onpremise the respective link type to "Test" (with "tests" as outward descriptin and "is tested by" as inward description) 
      - Make sure that a link type "Test" (with "tests" as outward descriptin and "is tested by" as inward description)  already exists before you install Xray.
  
     **If you already migrated and your link type is not recognized**
        If you are on this position it means you will probably have two Link Types one called "Tests" and the other "Test", where "Tests" is the one that was migrated from Onpremise and its the one currently used to link requirements to Tests but its not recognized by Xray on CLoud.

        - Delete the entry Test ( Tests - is tested by) - This should have been the one generated by Xray and no issues using it.
        - Rename the Link type "Tests" that was imported from OnPremise to the same name as the one deleted - Bare in mind this needs to be exactly the same (name, inward and outward)
        - Go To healthcheck ( it should give a error saying its missing the Link Type)
        - Click Reinstall
      There is some cache associated with this as such you might have to wait until a hour to xray recognizes in full the Link Type. As such you might need to wait for a bit until the healthcheck gives you full green.


  
  
- Pre conditions have been properly handled for been compatible with Atlassian Cloud.X-ray uses 'Pre-Condition' issue type On-Premise while in Cloud uses 'Precondition'. Issues need to be moved/update accordingly.
- Projects in the scope of scripts have been [Re-indexed](https://confluence.xpand-it.com/display/XRAYCLOUD/Project+Settings%3A+Re-Indexing). 
- The types of tests in Cloud musts contain all test types that will be sync ( Default are : Generic , Cucumber and Manual )
- Test Status and Step Test Status need to be replicated or mapping need to be done in xray_variables.py
- Issue Types that are handled by Xray need to be properly in Sync as when importing project Xray might not recognize On Premise issue Types ( Test , Test Plan, Test Set ) as Xray Issue Types.
- Enable "Create Inline Test Environments" in Project Test Environments if you are importing and want to have Test Environments migrated.
- Disable "Fail all steps" configuration item.
- If you are running a version of Xray above 4.0.0 be sure to set GLOBAL_XrayVersionIsObove4 to "Yes".This is important as it 4.0.0 contains breaking changes.
- If running a version above 4.0 please update to the latest version of the plugin ( minumium above 4.1 ) 4.0.x has a bug in the rest api that can lead to errors in the "execution finish dates" for tests runs that went through a "reset of the execution".



## What it does ?

- Syncronizes Test Definitions (Manual,Generic , Cucumber) details between a OnPremise and Cloud instance.
- Syncronizes PreConditions details between a OnPremise and Cloud instance.
- Syncronizes Test Executions Definitions between a OnPremise and Cloud instance
- Recreates in Cloud the existent OnPremise associations between Tests andPreConditions
- Recreates in Cloud the existent OnPremise associations between Tests and Test Plans
- Recreates in Cloud the existent OnPremise associations between Tests and Test Sets
- Recreates in Cloud the existent OnPremise associations between Tests and Test Executions
- Recreates in Cloud the existent OnPremise Test runs associated with the Test Execution (including evidences, attachments and comments for the test runs and for indivudual test steps executions)



## What it does not ?

- **It doesn't create any issues in Cloud**. This tool should be seen as a syncronizer of Xray data only. 
- Its not a two way syncronizer. It one way sycronizer OnPremise -> Cloud
- It doesn't import gadgets, dashboards or reports
- It doesn't [Test Runs customfields](https://confluence.xpand-it.com/display/XRAY/Configuring+Test+Run+Custom+Fieldsg)  or   [Test Step customfields](https://docs.getxray.app/display/XRAY/Xray+4.0.0+Release+Notes#Xray4.0.0ReleaseNotes-TestStepCustomFields)

## Limitations

- Attachments and Evidences

If you run 'xray_synctestexecwithtests.py' without the flag "rerun" (that will delete all test associations and reassociate the test and there for recreate new test runs) attachments/evidences of Test Runs will be duplicated.
This is due to limitation on the Jira api that cannot be resolved by this script at this moment.

- Time to migrate
The import of data can take considerable time from **hours to days** to be completed depending on the configurations amount of data and types of tests. Manual tests and test runs associated take considerable more time to import due to the number of calls that are need
to be made. You may want to consider to restrict what you want to import or to start by migrating the Xray information that is more pertinent to current day to day work and then to migrate the rest of past information in the days following the GoLive.

## Limitations ( Cloud product diferences and GraphQL limits)

- Size of reqest body in GraphQL (important for attachments)
20 mb
- Size of Test Environment Types
18 chars

- Size of data inside a Action, Data, Expected Result
8192 chars

-- Mimetypes - we are using mimetypes module and some filesnames are not known.We need to better handle it...for now not known are added as octet-stream


## Wish List

--  Support [Test Runs customfields](https://confluence.xpand-it.com/display/XRAY/Configuring+Test+Run+Custom+Fieldsg)  and   [Test Step customfields](https://docs.getxray.app/display/XRAY/Xray+4.0.0+Release+Notes#Xray4.0.0ReleaseNotes-TestStepCustomFields)


## Logging

- All scripts create a log file that follows their base names plust a time reference to when it was started..
- For performances reasons changes are not commited "one" by "one" they are packed until they reach limit ('GLOBAL_maxMutationsForPack' in xray_variables.py) and commited when limit is achieved.

  While information is been 'packed' the issues that are being processed are written to log. 
  
  You can see when information is being commited when you see the following tags in the logs : '======= Persisting information in Cloud [START] =========' and '======= Persisting information in Cloud [END] ========='
  

  
  
## Auxiliary Files
xray_variables.py - Contains some global information that is then use in scripts. It includes :

- credentials 
- urls
- JQL that define scope of issues to be targeted
- Ids of Xray customfields OnPremise

xray_helper.py - Contains several functions that are shared and used in the syncronizer scripts.

## How to run the scripts

**xray_syncCucumberTestDefinitions**


```bash

user@mig:~$ python xray_syncCucumberTestDefinitions.py --help

usage: xray_syncCucumberTestDefinitions.py [-h] [-ignore IGNORE] [-export EXPORT]

Cucumber test definition Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise keys, to be ignored (default: will try to get test defined in the JQL query).
  -export EXPORT  Export list of issues processed (default: information is logged though the log file but no file is create).

```
_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- You can rerun multiple times the same script over the same scope of issues (however if there are any change in the specification of the tests and they are already added in a test execution then standard [Data Consistency](https://confluence.xpand-it.com/display/XRAYCLOUD/Test+Runs#TestRuns-Dataconsistency) rules apply) 




**xray_syncGenericTestsDefinitions.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncGenericTestsDefinitions.py --help
usage: xray_syncGenericTestsDefinitions.py [-h] [-ignore IGNORE] [-export EXPORT]

Generic test definition Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise keys, to be ignored (default: will try to get test defined in the JQL query).
  -export EXPORT  Export list of issues processed (default: information is logged but no file is created).
```

_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- You can rerun multiple times the same script over the same scope of issues (however if there are any change in the specification of the tests and they are already added in a test execution then standard [Data Consistency](https://confluence.xpand-it.com/display/XRAYCLOUD/Test+Runs#TestRuns-Dataconsistency) rules apply) 

**xray_syncManualTestsDefinitions.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncManualTestsDefinitions.py --help
usage: xray_syncManualTestsDefinitions.py [-h] [-ignore IGNORE] [-export EXPORT]

Manual Test definitions Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise keys, to be ignored (Important: Multiple reruns in same scope of issues will result in duplicated steps
                  for tests)
  -export EXPORT  Export list of processed OnPremisse tests ids (default: no information will be exported). This is particularly important as multiple
                  reruns in same scope of issues will result in duplicated steps for tests
```

_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- If you want to rerun (run the over a scope of issues that were importer before ) you need to use the correct flag. Please note that tests that were already added in a test execution then standard [Data Consistency](https://confluence.xpand-it.com/display/XRAYCLOUD/Test+Runs#TestRuns-Dataconsistency) rules apply

**xray_syncTestExecs.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncTestExecs.py --help
usage: xray_syncTestExecs.py [-h] [-ignore IGNORE] [-export EXPORT]

Cucumber test definition Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise keys, to be ignored (default: will try to get test defined in the JQL query).
  -export EXPORT  Export list of issues processed (default: information is logged though the log file but no file is create).
```

_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- If you want to rerun (run the over a scope of issues that were importer before ) you need to use the correct flag. Please note that tests that were already added in a test execution then standard [Data Consistency](https://confluence.xpand-it.com/display/XRAYCLOUD/Test+Runs#TestRuns-Dataconsistency) rules apply
- This script is not necessary to run if you are planning to execute xray_syncTestExecWithTests.py has this last one also includes adding the Test Execs definitions.

**xray_syncPreCondDefinitions.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncPreCondDefinitions.py --help
usage: xray_syncPreCondDefinitions.py [-h] [-ignore IGNORE] [-export EXPORT]

Cucumber test definition Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise keys, to be ignored (default: will try to get test defined in the JQL query).
  -export EXPORT  Export list of issues processed (default: information is logged though the log file but no file is create).
```

_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- You can rerun multiple times the same script over the same scope of issues (however if there are any change in the specification of the tests and they are already added in a test execution then standard [Data Consistency](https://confluence.xpand-it.com/display/XRAYCLOUD/Test+Runs#TestRuns-Dataconsistency) rules apply)



**xray_syncTestandPrecond.py**


```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncTestandPrecond.py --help
usage: xray_syncTestandPrecond.py [-h] [-ignore IGNORE] [-export EXPORT]

Test Plan and Test Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise issues keys, to be ignored (default: will try to get test defined in the JQL query). The format should
                  be TESTPLANKEY:TESTKEY
  -export EXPORT  Export list of issues processed (default: information is logged though the log file but no file is created). Format can then be used as
                  input of this script
                  
```
_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- You can rerun multiple times the same script over the same scope of issues.




**xray_syncPlanTest.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncPlanTest.py --help
usage: xray_syncPlanTest.py [-h] [-ignore IGNORE] [-export EXPORT]

Test Plan and Test Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise issues keys, to be ignored (default: will try to get test defined in the JQL query). The format should
                  be TESTPLANKEY:TESTKEY
  -export EXPORT  Export list of issues processed (default: information is logged though the log file but no file is created). Format can then be used as
                  input of this script
```


_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- You can rerun multiple times the same script over the same scope of issues.



**xray_syncSetsTest.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncSetsTest.py --help
usage: xray_syncSetsTest.py [-h] [-ignore IGNORE] [-export EXPORT]

Test Plan and Test Syncronizer

optional arguments:
  -h, --help      show this help message and exit
  -ignore IGNORE  Pass as input a list of onpremise issues keys, to be ignored (default: will try to get test defined in the JQL query). The format should
                  be TESTPLANKEY:TESTKEY
  -export EXPORT  Export list of issues processed (default: information is logged though the log file but no file is created). Format can then be used as
                  input of this script
```

_Notes_

- Log information is sent to console and to a log file ( same name as script plus .log ) . Log is appended to file, this fiel can increase considerable.
- The list of exported issues processed can be used as input (as a list of issues to ignore) for this script.
- You can rerun multiple times the same script over the same scope of issues.

**xray_syncTestExecWithTests.py**

```bash
user@mig:/mnt/f/workspace-vsc/XrayImporter$ venv/Scripts/python.exe xray_syncTestExecWithTests.py --help
usage: xray_syncTestExecWithTests.py [-h] [-manualTestlist MANUALTESTLIST] [-export EXPORT] [-ignore IGNORE] [-c] [-d] [-e] [-sc] [-sd] [-se] [-st] [-s]
                                     [-rerun]

Test Execution Syncronizer

optional arguments:
  -h, --help            show this help message and exit
  -manualTestlist MANUALTESTLIST
                        Pass as input the list of test keys, for whom step information will be retrieved (default: will try to get steps for all tests).
  -export EXPORT        Export list of Test Execs fully processed (Important: Only Test Exec that were fully importorted are loogged in this file.If a Test
                        Exec is not present in the file its as not been processed or is in unstable situation.
  -ignore IGNORE        Pass as input a list of onpremise keys, to be ignored (default: will try to get test defined in the JQL query).
  -c, --comments        Do not include Executions comments (default: will include comments).
  -d, --defects         Do not include Executions defects (default: will include defects).
  -e, --evidences       Do not include Executions evidences (default: will include evidences).
  -sc, --stepcomments   Do not include steps comments (default: will include comments).
  -sd, --stepdefects    Do not include steps defects (default: will include defects).
  -se, --stepevidences  Do not include steps evidences (default: will include evidences).
  -st, --stepstatus     Do not include steps status (default: will include status).
  -s, --steps           Do not include steps comments (default: will include comments).
  -rerun                Used when we want to update existing information.Existing test runs will be deleted as part of this.

```

_Notes_

- This script can take a considerable amount of time to run if your instance contains a huge number of test runs associated with Manual tests. When migrating consider to only include global results of the test runs instead of the all detail of the test steps. 
- There is a limit of 60 calls to the GraphQL as such evaluate with carefull the number of scripts you run in parallel as it might backfire and they can start stalling each other.
- Start dates, Execution dates as well assignee and executer are preserved. The time that the test was added to the Execution is not.


## Insights and advices on usage

### Proposed order

1) Run initially the scripts that provide the descriptions of Tests ( Cucumber, Generic , Manual ) and PreConditions (Manual test will take considerable more time than any other of the scripts)
2) Run the scripts that link Pre Conditions with Tests
3) Run the scripts that link Plans and Sets with Tests
4) Run the scripts that recreate the Repository and the plan folders
5) Run the scripts that link Plans with Executions.
6) Run the script that adds Test Execution details and syncs with associated tests ( creating the associated test runs).

## Others
- Do not run more than 3 in parallel, there is a limit of 60 calls per minute to the Xray Cloud GraphQL API and to many scripts in parallel may leed to having them stalling each other.
- There are few set of limits for the Cloud-GraphQL (size of body, unstructured fields, Action, data and expected result). Before migrate consider to work out your data on server so that this will not be a problem.
- The scripts provide statistics about times it takes to perform activities - study them to better plan the Go Live.
- Manual tests and executions associated with it take considerable more time than other activities. If you have a great ammout of these you should plan carefully the migration as if you have several thousands it may take hours to days to achive the total migration.




## Understanding the Global Variables

### JIRA Onpremise

| Variable     | Example    | Notes |
| --------|---------|-------|
| GLOBAL_testEnvironmentsId  | GLOBAL_testEnvironmentsId="10806   | The ID of the Test Environment customfield    |
|GLOBAL_testType|GLOBAL_testType="10100"|The ID of the Test Type customfield|
|GLOBAL_ManualTestSteps|GLOBAL_ManualTestSteps="10104"|The ID of the Manual Test Steps customfield|
|GLOBAL_cucumberTestType|GLOBAL_cucumberTestType="10101"|The ID of the Ccucumber Test Type customfield|
|GLOBAL_cucumberScenario|GLOBAL_cucumberScenario="10102"|The ID of the Cucumber Scenario customfield|
|GLOBAL_genericTestDefinition|GLOBAL_genericTestDefinition="10103"|The ID of the Generic Test Definiiton customfield|
|GLOBAL_preConditionType|GLOBAL_preConditionType="10109"|The ID of the Pre condition type customfield|
|GLOBAL_preConditionDetails|GLOBAL_preConditionDetails="10110"|The ID of the Pre Condition details customfield|

### Defining Scope
| Variable     | Example    | Notes |
| --------|---------|-------|
|GLOBAL_jqlManualTests|GLOBAL_jqlManualTests='type = Test and "Test Type" = "Manual" and project = "Test Project" order by created asc'||
|GLOBAL_jqlCucumber|GLOBAL_jqlCucumber='type = Test and "Test Type" = "Cucumber" and project = "Test Project" order by created asc'||
|GLOBAL_jqlGeneric|GLOBAL_jqlGeneric='type = Test and "Test Type" not in ("Manual","Cucumber") and project = "Test Project" order by created asc'||
|GLOBAL_jqlPlan|GLOBAL_jqlPlan='"issuetype" = "Test Plan" and project = "Test Project" order by created asc'||
|GLOBAL_jqlSet|GLOBAL_jqlSet='"issuetype" = "Test Set" and project = "Test Project" order by created asc'||
|GLOBAL_jqlTestandPreCond|GLOBAL_jqlTestandPreCond='"issuetype" = "Test" and project = "Test Project" order by created asc'||
|GLOBAL_jqlPreCond|GLOBAL_jqlPreCond='"issuetype" = "Pre-Condition" and project = "Test Project" order by created asc'||
|GLOBAL_jqlExec|GLOBAL_jqlExec='"issuetype" = "Test Execution" and  ( project = "Test Project" ) and createdDate  >=  2019-07-07 order by created asc'||
|GLOBAL_projectRepositoryList|GLOBAL_projectRepositoryList=['XRAY']|List of project repositories to sync|
|GLOBAL_jqlPlanFolder|GLOBAL_jqlPlanFolder||
|GLOBAL_defaultUser|GLOBAL_defaultUser="johndoe"|Default user to be use for test runs in case the user linked to the executer no longer exists in the Onpremise instance|
|GLOBAL_StepInitialStatus|GLOBAL_StepInitialStatus="TODO"|Contains the name of the initial status for a step.Uset to avoid update step status in cloud if its in a initial status OnPremise|

### General config

| Variable     | Example    | Notes |
| --------|---------|-------|
| GLOBAL_basic_auth_user  | GLOBAL_basic_auth_user="user"    | Username for basic auth On Premise with full permissions on issues we are migrating    |
| GLOBAL_basic_auth_pass  | GLOBAL_basic_auth_pass = "pass"     | password for basic auth On Premise    |
| GLOBAL_cloudUser  | GLOBAL_cloudUser = "user"    | Username for basic auth Cloud    |
| GLOBAL_statusXray  | GLOBAL_statusXray = {"PASS": "PASSED","TODO": "TO DO","Failing_acceptable": "Failing_acceptable"}    | Mapping of OnPremise status and Cloud Test Run Status    |
| GLOBAL_statusStepXray  | GLOBAL_statusStepXray = {"PASS": "PASSED","TODO": "TO DO","Failing_acceptable": "Failing_acceptable"}    | Mapping of OnPremise status and Cloud Test Run Status    |
| GLOBAL_onCloudMig  | GLOBAL_onCloudMig = "https://target.atlassian.net/"    |     |
| GLOBAL_onPremiseURL  | GLOBAL_onPremiseURL = "https://source.instance.onpremise"    |    |
| GLOBAL_url_xray  | GLOBAL_url_xray = 'https://xray.cloud.xpand-it.com/api/v1/graphql'   |     |
| GLOBAL_client_id  | GLOBAL_client_id = 'XXXXXXX'     | Xray cloud clientID    |
| GLOBAL_client_secret  | GLOBAL_client_secret = 'XXXXX'   | Xray cloud client secret    |
| GLOBAL_apitoken  | GLOBAL_apitoken="yyyyyy"   | API Token for the cloud user    |
| GLOBAL_mutation_counter  | GLOBAL_mutation_counter=0   | Global counter (internal purpose)    |
| GLOBAL_maxMutationsForPack  | GLOBAL_maxMutationsForPack=20    | Max o mutations to push    |
| GLOBAL_MAX_ATTACH_SIZE  | GLOBAL_MAX_ATTACH_SIZE=10000000    | Max size for attachments there is currently a limit   |
| GLOBAL_SIMULATE  | GLOBAL_SIMULATE=False     | Update Xray or it executes without push anything to the cloud.    |
| GLOBAL_XrayVersionIsObove4  | GLOBAL_XrayVersionIsObove4="Yes"     | Flags that we are using Xray 4.0. This is important due to breaking changes in Steps.Default is "No"|



