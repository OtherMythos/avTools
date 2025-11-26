import configparser
import os
import sys
from pathlib import Path
import shutil

import json
import ConfigClass
import subprocess
import time

class colour:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

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
        with open(configFilePath) as f:
            d = json.load(f)
            testName = d["TestName"]
            testFound = True

        if(not testFound):
            testName = "Unnamed test"

        return testName

    def cleanupDirectory(self):
        #Remove the old test file if one is still there.
        testFilePath = self.testCasePath / "avTestFile.txt"
        if(os.path.isfile(testFilePath)):
            os.remove(testFilePath)

    def appsupportdir(self):
        windows = r'%APPDATA%'
        windows = os.path.expandvars(windows)
        if 'APPDATA' not in windows:
            return windows

        user_directory = os.path.expanduser('~')

        macos = os.path.join(user_directory, 'Library', 'Application Support')
        if os.path.exists(macos):
            return macos

        linux = os.path.join(user_directory, '.local', 'share')
        if os.path.exists(linux):
            return linux

        return user_directory

    def determineLogPath(self):
        p = sys.platform
        foundDir = None
        if(p == 'darwin'):
            foundDir = Path(self.appsupportdir()) / "../Logs/av"
        elif(p == 'win32'):
            foundDir = Path(self.appsupportdir()) / "av/logs"
        else:
            foundDir = Path(self.appsupportdir()) / "av/logs/av"

        foundDir = foundDir / "av.log"

        return foundDir

    def destroyLogs(self):
        foundLogPath = self.determineLogPath()
        if(foundLogPath.exists() and foundLogPath.is_file()):
            os.remove(foundLogPath)

    def copyLogToDestination(self):
        outDirPath = ConfigClass.pathToDumpLogs
        if(outDirPath is None):
            return

        foundLogPath = self.determineLogPath()
        if(foundLogPath.exists() and foundLogPath.is_file()):
            outName = self.getTestCaseName() + ".log"
            outPath = Path(outDirPath) / outName
            shutil.copyfile(foundLogPath, outPath)
            print("Copied log to %s" % str(outPath))

    def copyStdoutStderrToDestination(self, stdout_content, stderr_content):
        """Copy stdout and stderr outputs to destination directory"""
        outDirPath = ConfigClass.pathToDumpLogs
        if(outDirPath is None):
            return

        # Save stdout
        if stdout_content:
            stdout_name = self.getTestCaseName() + "_stdout.log"
            stdout_path = Path(outDirPath) / stdout_name
            try:
                with open(stdout_path, 'w') as f:
                    f.write(stdout_content)
                print("Copied stdout to %s" % str(stdout_path))
            except Exception as e:
                print(colour.RED + f"Failed to write stdout log: {e}" + colour.END)

        # Save stderr
        if stderr_content:
            stderr_name = self.getTestCaseName() + "_stderr.log"
            stderr_path = Path(outDirPath) / stderr_name
            try:
                with open(stderr_path, 'w') as f:
                    f.write(stderr_content)
                print("Copied stderr to %s" % str(stderr_path))
            except Exception as e:
                print(colour.RED + f"Failed to write stderr log: {e}" + colour.END)

    def determineTestResults(self):
        #The test process has now ended. Check to see what the results are.
        print("Finishing test case " + self.getTestCaseName())

        testFilePath = self.testCasePath / "avTestFile.txt"
        if(not testFilePath.exists() or not testFilePath.is_file()):
            print(colour.RED)
            print("There was a problem loading the test file from the test run %s. This will be considered a failure." % self.getTestCaseName())
            print(colour.END)
            return None
        testFile = open(testFilePath, 'r')

        lines = testFile.readlines()
        testFile.close()
        if(len(lines) <= 0):
            #If no lines were written to the file at all, something went wrong in the engine. This should be considered a failure.
            print(colour.RED + "Test " + self.getTestCaseName() + " returned an empty avTestFile." + colour.END)
            return [0, True, []]

        #1 - Successfully finished
        #-1 - Test failed
        #0 - Test still in progress (as here means the process ended, it can be assumed that was because of a crash)
        errorCode = int(lines[1])
        print("Test finished with error code " + str(errorCode))

        failure = False
        failureMessageLines = []
        if(errorCode == -1):
            print("Test case " + self.getTestCaseName() + colour.RED + " Failed" + colour.END + "!")
            failure = True
            failureMessageLines = lines[3:]
        elif(errorCode == 1):
            print("Test case " + self.getTestCaseName() + colour.GREEN + " passed" + colour.END + ".")
        elif(errorCode == 0):
            print(colour.RED + "Engine crash during " + self.getTestCaseName() + " execution!" + colour.END)
            failure = True

        print(colour.RED)
        for i in failureMessageLines:
            print(i, end='')
        print(colour.END)

        results = {
            "errorCode": errorCode,
            "failure": failure,
            "failureMessage": failureMessageLines,
            "testName": self.getTestCaseName()
        }

        return results

    def execute(self, setupBasePath, flags):
        self.cleanupDirectory()
        self.destroyLogs()

        print("Executing test case " + self.getTestCaseName())
        #Now I need to start up the engine, passing in the path to the directory.

        argParam = [str(ConfigClass.pathToEngineExecutable)]
        if setupBasePath is not None:
            argParam.append(str(setupBasePath))
        argParam.append(str(self.testCasePath / "avSetup.cfg"))
        if flags is not None:
            argParam = argParam + flags.split(' ')
        print(" ".join(argParam))

        # Use PIPE to capture stdout and stderr
        # Use bytes mode to avoid encoding issues
        process = subprocess.Popen(argParam, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("     with PID " + str(process.pid))

        #Wait for the process to finish and capture output
        stdout_bytes, stderr_bytes = process.communicate()

        # Decode with error handling for non-UTF-8 content
        stdout_content = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
        stderr_content = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""

        time.sleep(1)

        # Copy all logs including stdout and stderr
        self.copyLogToDestination()
        self.copyStdoutStderrToDestination(stdout_content, stderr_content)

        return self.determineTestResults()