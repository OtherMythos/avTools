import os
from TestCaseExecution import *
from pathlib import Path

class TestPlanExecution:

    def __init__(self, testPlanPath, recursive):
        self.testPlanName = testPlanPath.name
        self.testPlanPath = testPlanPath
        self.testCaseExecutions = []
        self.testCaseResults = []

        if recursive:
            self.recursiveFindTestCases()
        else:
            self.findTestCases()

    def recursiveFindTestCases(self):
        for root, dirs, files in os.walk(self.testPlanPath):
            for file in files:
                if(file == "avSetup.cfg"):
                    outPath = Path(root) / file
                    testCase = TestCaseExecution(Path(root))
                    if(testCase.valid()):
                        self.testCaseExecutions.append(testCase)

    def findTestCases(self):
        for d in os.listdir(self.testPlanPath):
            path = self.testPlanPath / d
            if(not os.path.isdir(self.testPlanPath)):
                continue

            testCase = TestCaseExecution(path)
            if(testCase.valid()):
                self.testCaseExecutions.append(testCase)

    def processResults(self):
        totalFailure = 0
        totalTests = len(self.testCaseResults)
        for i in self.testCaseResults:
            if(i == None):
                #Assume a none returned (unable to read the test file) is a failure.
                totalFailure += 1
                continue

            if(i["failure"]):
                totalFailure += 1

        passPercentage = 100
        if(totalTests > 0):
            passPercentage = 100 - (totalFailure / totalTests) * 100

        beginningColour = None
        if(passPercentage == 100):
            beginningColour = colour.GREEN
        elif(passPercentage < 100 and passPercentage > 25):
            beginningColour = colour.YELLOW
        else:
            beginningColour = colour.RED


        print("Total failures in test plan: " + str(totalFailure))
        print("Test Pass percentage: " + beginningColour + str("%.2f" % passPercentage) + "%" + colour.END)

        resultsDict = {
            "testPlanName": self.testPlanName,
            "totalTests": totalTests,
            "totalFailures": totalFailure,
            "results": self.testCaseResults
        }

        return resultsDict

    def execute(self):
        print("Executing test plan " + self.testPlanName)

        for testCase in self.testCaseExecutions:
            caseResult = testCase.execute()
            self.testCaseResults.append(caseResult)

        #All the test cases are now complete. Process the results.
        print("Test plan " + self.testPlanName + " completed.")
        return self.processResults()
