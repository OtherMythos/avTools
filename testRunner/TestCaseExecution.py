import configparser
import os

import ConfigClass
import subprocess
import time

class TestCaseExecution:
    def __init__(self, testCasePath):
        self.testCasePath = testCasePath
        self.testCaseName = ""

    def valid(self):
        configFilePath = self.testCasePath / "avSetup.cfg"
        if(not os.path.isfile(configFilePath)):
            return False

        #Check the av setup file is actually a test.
        f = open(configFilePath, 'r')
        testModeFileFound = False
        for l in f:
            if("TestMode" in l and ("True" in l or "true" in l or "1" in l)):
                testModeFileFound = True
                break
        f.close()

        if(not testModeFileFound):
            return False

        return True

    def getTestCaseName(self):
        if(self.testCaseName != ""):
            return self.testCaseName

        configFilePath = self.testCasePath / "avSetup.cfg"
        testName = ""
        testFound = False
        f = open(configFilePath, 'r')
        for l in f:
            if("TestName" in l):
                testName = l.split()[1]
                testFound = True
                break

        f.close()

        if(not testFound):
            testName = "Unnamed test"

        return testName

    def cleanupDirectory(self):
        #Remove the old test file if one is still there.
        testFilePath = self.testCasePath / "avTestFile.txt"
        if(os.path.isfile(testFilePath)):
            os.remove(testFilePath)

    def determineTestResults(self):
        #The test process has now ended. Check to see what the results are.
        print("Finishing test case " + self.getTestCaseName())

        testFilePath = self.testCasePath / "avTestFile.txt"
        testFile = open(testFilePath, 'r')

        lines = testFile.readlines()
        #1 - Successfully finished
        #-1 - Test failed
        #0 - Test still in progress (as here means the process ended, it can be assumed that was because of a crash)
        errorCode = int(lines[1])
        print("Test finished with error code " + str(errorCode))

        failure = False
        failureMessageLines = []
        if(errorCode == -1):
            print("Test case " + self.getTestCaseName() + " failed!")
            failure = True
            failureMessageLines = lines[3:]
        elif(errorCode == 1):
            print("Test case " + self.getTestCaseName() + " passed.")
        elif(errorCode == 0):
            print("Engine crash during " + self.getTestCaseName() + " execution!")
            failure = True

        for i in failureMessageLines:
            print(i, end='')
        testFile.close()
        return [errorCode, failure, failureMessageLines]

    def execute(self):
        self.cleanupDirectory()

        print("Executing test case " + self.getTestCaseName())
        #Now I need to start up the engine, passing in the path to the directory.
        command = ConfigClass.pathToEngineExecutable + " " + str(self.testCasePath / "avSetup.cfg") + ' > /dev/null &'

        devnull = open(os.devnull, 'w')
        process = subprocess.Popen([ConfigClass.pathToEngineExecutable, str(self.testCasePath / "avSetup.cfg")], stdout=devnull, stderr=devnull)
        devnull.close()

        print("     with PID " + str(process.pid))

        #Wait for the process to finish.
        process.wait()

        time.sleep(1)

        return self.determineTestResults()
