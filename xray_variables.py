# Copyright (c) 2020, Xpand IT
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
#    This product includes software developed by the <organization>.
# 4. Neither the name of the <organization> nor the
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

# CustomFields teams in space
GLOBAL_testEnvironmentsId="10806"
GLOBAL_testType="10100"
GLOBAL_ManualTestSteps="10104"
GLOBAL_cucumberTestType="10101"
GLOBAL_cucumberScenario="10102"
GLOBAL_genericTestDefinition="10103"
GLOBAL_preConditionType="10109"
GLOBAL_preConditionDetails="10110"


#General config
GLOBAL_basic_auth_user="admin"
GLOBAL_basic_auth_pass = "Charlie!"
GLOBAL_cloudUser = "charlie@mydomain.com"
GLOBAL_statusXray = {
  "PASS": "PASSED",
  "TODO": "TO DO",
  "EXECUTING": "EXECUTING",
  "FAIL": "FAILED",
  "ABORTED": "ABORTED",
  "BLOCKED": "BLOCKED",
  "NOTTESTABLE": "NOTTESTABLE",
  "Failing_acceptable": "Failing_acceptable"
}


GLOBAL_statusStepXray = {
  "PASS": "PASS",
  "TODO": "TODO",
  "EXECUTING": "EXECUTING",
  "FAIL": "FAIL",
  "ABORTED": "ABORTED",
  "BLOCKED": "BLOCKED",
  "NOTTESTABLE": "NOTTESTABLE",
  "Failing_acceptable": "Failing_acceptable"
}
GLOBAL_onCloudMig = "https://cloudmig.atlassian.net/"
GLOBAL_onPremiseURL = "https://jira.mydomain.com"
GLOBAL_url_xray = 'https://xray.cloud.xpand-it.com/api/v1/graphql'
GLOBAL_client_id = 'DXXXXXXXXXXXXXXXXXXX'
GLOBAL_client_secret = '8asd8asdasdasdasdasdasdasdasdadsdasdsadsadadasd'
GLOBAL_apitoken="1q2w3e4r5t"
GLOBAL_mutation_counter=0
GLOBAL_maxMutationsForPack=20
GLOBAL_MAX_ATTACH_SIZE=10000000
GLOBAL_SIMULATE=False


# JQL queries that define the scope of scripts.
GLOBAL_jqlManualTests='type = Test and "Test Type" = "Manual" and project = "Test Project" order by created asc'
GLOBAL_jqlCucumber='type = Test and "Test Type" = "Cucumber" and project = "Test Project" order by created asc'
GLOBAL_jqlGeneric='type = Test and "Test Type" not in ("Manual","Cucumber") and project = "Test Project" order by created asc'
GLOBAL_jqlPlan='"issuetype" = "Test Plan" and project = "Test Project" order by created asc'
GLOBAL_jqlSet='"issuetype" = "Test Set" and project = "Test Project" order by created asc'
GLOBAL_jqlExec='"issuetype" = "Test Execution" and  ( projec = "Test Project" )  order by created asc'
GLOBAL_jqlTestandPreCond='"issuetype" = "Test" and project = "Test Project" order by created asc'
GLOBAL_jqlPreCond='"issuetype" = "Pre-Condition" and project = "Test Project" order by created asc'
GLOBAL_jqlTests='type = Test and project = "Test Project" order by created asc'



GLOBAL_projectRepositoryList = ['TP']
GLOBAL_jqlPlanFolder='"issuetype" = "Test Plan" and project = "Test Project" order by created asc'

GLOBAL_defaultUser="admin"
GLOBAL_StepInitialStatus="TODO"