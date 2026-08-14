import os
from pathlib import Path

import json
import ConfigClass
import signal
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

def describeReturnCode(returnCode):
    #The engine's main() returns 0 down every path it can reach, so any other status means the
    #process died rather than shut down. Returns None for a clean exit, otherwise a verb phrase
    #that reads after "The engine".
    if(returnCode is None or returnCode == 0):
        return None

    if(returnCode < 0):
        #POSIX: killed by a signal, which subprocess reports as the negated signal number.
        signalNumber = -returnCode
        try:
            signalName = signal.Signals(signalNumber).name
        except ValueError:
            signalName = "unknown signal"
        return "was killed by signal %i (%s)" % (signalNumber, signalName)

    #Windows reports a crash as a large positive status, such as 0xC0000005 for an access
    #violation, which is far more recognisable in hex than in decimal.
    if(returnCode > 0xFF):
        return "exited with status 0x%08X" % returnCode

    return "exited with code %i" % returnCode


class TestCaseExecution:
    def __init__(self, testCasePath):
        self.testCasePath = testCasePath
        self.testCaseName = ""

        #When test cases run concurrently their output is buffered and flushed as a single
        #block once the case finishes, so simultaneous tests don't interleave their lines.
        #Running serially this stays True and output streams as it happens, as it always has.
        self.liveOutput = True
        self.output = []

    def log(self, message=""):
        if(self.liveOutput):
            print(message)
        else:
            self.output.append(str(message))

    def flushOutput(self):
        text = "\n".join(self.output)
        self.output = []
        return text

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

    def engineLogPath(self):
        #The engine is told to write its log straight to its final destination with --logFile,
        #rather than to the single shared av.log every engine process would otherwise truncate.
        return Path(ConfigClass.pathToEngineLogs) / (self.getTestCaseName() + ".log")

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
                self.log("Copied stdout to %s" % str(stdout_path))
            except Exception as e:
                self.log(colour.RED + f"Failed to write stdout log: {e}" + colour.END)

        # Save stderr
        if stderr_content:
            stderr_name = self.getTestCaseName() + "_stderr.log"
            stderr_path = Path(outDirPath) / stderr_name
            try:
                with open(stderr_path, 'w') as f:
                    f.write(stderr_content)
                self.log("Copied stderr to %s" % str(stderr_path))
            except Exception as e:
                self.log(colour.RED + f"Failed to write stderr log: {e}" + colour.END)

    def buildFailureResult(self, errorCode, failureMessageLines, returnCode=None):
        #Every path out of determineTestResults returns this same shape, so the results
        #processing and the JUnit writer never have to special case a failed run.
        return {
            "errorCode": errorCode,
            "failure": True,
            "failureMessage": failureMessageLines,
            "testName": self.getTestCaseName(),
            "returnCode": returnCode,
            "engineCrashed": describeReturnCode(returnCode) is not None
        }

    def determineTestResults(self, returnCode=None):
        #The test process has now ended. Check to see what the results are.
        self.log("Finishing test case " + self.getTestCaseName())

        crashDescription = describeReturnCode(returnCode)

        testFilePath = self.testCasePath / "avTestFile.txt"
        if(not testFilePath.exists() or not testFilePath.is_file()):
            self.log(colour.RED)
            self.log("There was a problem loading the test file from the test run %s. This will be considered a failure." % self.getTestCaseName())
            self.log(colour.END)
            return self.buildFailureResult(0, self.buildCrashMessage(
                "No avTestFile.txt was produced by the test run.", crashDescription), returnCode)
        testFile = open(testFilePath, 'r')

        lines = testFile.readlines()
        testFile.close()
        if(len(lines) <= 0):
            #If no lines were written to the file at all, something went wrong in the engine. This should be considered a failure.
            self.log(colour.RED + "Test " + self.getTestCaseName() + " returned an empty avTestFile." + colour.END)
            return self.buildFailureResult(0, self.buildCrashMessage(
                "The test run produced an empty avTestFile.txt.", crashDescription), returnCode)

        #1 - Successfully finished
        #-1 - Test failed
        #0 - Test still in progress (as here means the process ended, it can be assumed that was because of a crash)
        try:
            errorCode = int(lines[1])
        except (IndexError, ValueError):
            #A crash partway through writing the file leaves it without a readable verdict. That
            #is itself the result, so report it rather than letting the scheduler catch a
            #ValueError and blame the runner.
            self.log(colour.RED + "Test " + self.getTestCaseName() + " wrote an unreadable avTestFile." + colour.END)
            return self.buildFailureResult(0, self.buildCrashMessage(
                "The avTestFile.txt holds no readable result code, so the engine stopped while writing it.",
                crashDescription), returnCode)
        self.log("Test finished with error code " + str(errorCode))

        failure = False
        failureMessageLines = []
        if(errorCode == -1):
            self.log("Test case " + self.getTestCaseName() + colour.RED + " Failed" + colour.END + "!")
            failure = True
            failureMessageLines = [l.rstrip("\n") for l in lines[3:]]
        elif(errorCode == 1):
            self.log("Test case " + self.getTestCaseName() + colour.GREEN + " passed" + colour.END + ".")
        elif(errorCode == 0):
            self.log(colour.RED + "Engine crash during " + self.getTestCaseName() + " execution!" + colour.END)
            failure = True
            failureMessageLines = self.buildCrashMessage(
                "The engine stopped before the test reached a verdict.", crashDescription)

        if(crashDescription is not None):
            #A case whose timeout doesn't mean failure writes its pass the moment the timeout is
            #reached and then keeps running until shutdown, so a crash can land after the file
            #already says 1. Without this the runner would report those runs as passes.
            self.log(colour.RED + "The engine " + crashDescription + " running " + self.getTestCaseName() + "!" + colour.END)
            if(not failure):
                failureMessageLines = self.buildCrashMessage(
                    "The test reached its verdict, but the engine did not shut down cleanly afterwards.",
                    crashDescription)
            elif(errorCode != 0):
                failureMessageLines = failureMessageLines + ["In addition, the engine " + crashDescription + "."]
            failure = True

        if(failureMessageLines):
            self.log(colour.RED + "\n".join(failureMessageLines) + colour.END)

        results = {
            "errorCode": errorCode,
            "failure": failure,
            "failureMessage": failureMessageLines,
            "testName": self.getTestCaseName(),
            "returnCode": returnCode,
            "engineCrashed": crashDescription is not None
        }

        return results

    def buildCrashMessage(self, summary, crashDescription):
        #Shaped like the engine's own failure messages - a title line, a separator, then the
        #detail - so everything reading failureMessage sees one format.
        lines = [
            "Test Case " + self.getTestCaseName(),
            "===ENGINE CRASH===",
            summary
        ]
        if(crashDescription is not None):
            lines.append("The engine " + crashDescription + ".")

        return lines

    def execute(self, setupBasePath, flags):
        self.cleanupDirectory()

        self.log("Executing test case " + self.getTestCaseName())
        #Now I need to start up the engine, passing in the path to the directory.

        argParam = [str(ConfigClass.pathToEngineExecutable)]
        if setupBasePath is not None:
            argParam.append(str(setupBasePath))
        argParam.append(str(self.testCasePath / "avSetup.cfg"))
        #Placed ahead of the user supplied flags so its value can never be mistaken for one of them.
        argParam += ["--logFile", str(self.engineLogPath())]
        if flags is not None:
            #split() rather than split(' ') so a leading or doubled space doesn't produce an
            #empty argument, which the engine would take as a positional setup file path.
            argParam = argParam + flags.split()
        self.log(" ".join(argParam))

        # Use PIPE to capture stdout and stderr
        # Use bytes mode to avoid encoding issues
        process = subprocess.Popen(argParam, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.log("     with PID " + str(process.pid))

        #Wait for the process to finish and capture output
        stdout_bytes, stderr_bytes = process.communicate()

        # Decode with error handling for non-UTF-8 content
        stdout_content = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
        stderr_content = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""

        #time.sleep(1)

        #The engine log was written straight to its destination by --logFile, so only
        #the captured stdout and stderr need placing.
        self.copyStdoutStderrToDestination(stdout_content, stderr_content)

        return self.determineTestResults(process.returncode)