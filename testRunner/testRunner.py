#!/usr/bin/python3

import configparser
from pathlib import Path
from TestPlanExecution import *
from TestProjectEntry import *
from JUnitFileWriter import *
import ConfigClass
import os
import argparse
import sys

#Parse the test config file and store its values as classes in an array somewhere
#Iterate the entries and perform the actions, ensuring there is a function call
#Add a recursive flag to search for avSetup.cfg files.

def parseTestConfigFile(path):
    config = configparser.ConfigParser()
    config.read(path)

    entries = []
    for testPlanKey in config:
        if(testPlanKey == "DEFAULT"):
            continue
        entry = TestProjectEntry(testPlanKey)
        plan = config[testPlanKey]
        for i in plan:
            if(i == "path"):
                entry.setPath(plan[i], path)
            elif(i == "recursive"):
                entry.recursive = True if plan[i] == "true" else False
            elif(i == "setupfilebase"):
                resolvedBase = str(Path(path).parent / plan[i])
                entry.baseSetupFile = resolvedBase
        entries.append(entry)

    return entries

def runTestProjectWithPlans(testProjectEntry):
    targetPath = testProjectEntry.path
    results = []
    if(not targetPath.exists()):
        print("Target path %s as specified in the avTests.cfg file does not exist." % targetPath)
        return False

    testPlanPaths = []
    #Find the paths to the test plans
    for d in os.listdir(targetPath):
        testPlanPath = targetPath / d
        if(not os.path.isdir(testPlanPath)):
            continue

        testPlanPaths.append(testPlanPath)

    for d in testPlanPaths:
        execution = TestPlanExecution(d, False, testProjectEntry.baseSetupFile)
        result = execution.execute()
        results.append(result)

    return results

def runTestProjectRecursive(testProjectEntry):
    execution = TestPlanExecution(testProjectEntry.path, True, testProjectEntry.baseSetupFile)
    result = execution.execute()
    return [result]

def runTestProject(testProjectEntry):
    if(testProjectEntry.recursive):
        return runTestProjectRecursive(testProjectEntry)
    else:
        return runTestProjectWithPlans(testProjectEntry)

def beginRun(testConfig):
    configEntries = parseTestConfigFile(testConfig)
    results = []
    for i in configEntries:
        result = runTestProject(i)
        results.append(result)

    return results

def gatherResultsInfo(results):
    totalTestsRan = 0
    totalFailures = 0
    for i in results:
        totalTestsRan += i["totalTests"]
        totalFailures += i["totalFailures"]

    failureTestPlanCount = 0
    for i in results:
        if(i["totalFailures"] > 0):
            failureTestPlanCount += 1

    info = {
        "totalTestsRan":totalTestsRan,
        "totalFailures":totalFailures,
        "failureTestPlanCount":failureTestPlanCount
    }
    return info

def printWithPadding(text, bannerString):
    spaceDiff = int((len(bannerString) - len(text)) / 2)
    print((" " * spaceDiff) + text)

def printResults(results):
    for i in results:
        info = gatherResultsInfo(i)
        sideBanner = "=" * 9
        titleBanner = sideBanner + " Test Run Summary " + sideBanner
        print("\n")
        print(titleBanner)

        if(info["totalFailures"] <= 0):
            noFailString = "You have no failing tests"
            #Figure out how many spaces is needed to centre this.

            printWithPadding("Ran %i tests in total" % info["totalTestsRan"], titleBanner)
            print(colour.GREEN)
            printWithPadding(noFailString, titleBanner)
            print(colour.END)
        else:
            #Failing tests.
            print(colour.RED)
            print("%i tests failed across %i test plans." % (info["totalFailures"], info["failureTestPlanCount"]))
            printWithPadding("You have failing tests.", titleBanner)
            print(colour.END)

def processExitCode(results):
    totalFailures = 0
    for i in results:
        for y in i:
            totalFailures += y["totalFailures"]

    sys.exit(0 if totalFailures == 0 else 1)

def main():
    helpText = '''A script to help batch run avEngine tests.
    The engine allows the creation of tests using a built in framework.
    It is based on the squirrel scripting system, and is intended to provide a means to perform integration testing.

    This test runner script accepts an avTests.cfg file which describes the various test cases which should be run as part of the test execution.
    When finished this script will output a file describing the results of the test.
    '''

    parser = argparse.ArgumentParser(description = helpText)
    #position argument
    parser.add_argument("-p", "--path", help="The path to the avTests.cfg file. This file will describe to the test runner what it should actually do.", default="/home/edward/Documents/avTests/avTests.cfg")
    parser.add_argument("-e", "--engine", help="The path to the engine executable.", default="/home/edward/Documents/avEngine/build/av")
    parser.add_argument("-o", "--output", help="Output file in JUnit format", default=None)
    parser.add_argument("-l", "--log", help="Directory in which to place test log files.", default=None)
    args = parser.parse_args()

    enginePath = Path(args.engine).absolute().resolve()
    ConfigClass.pathToEngineExecutable = ""
    ConfigClass.pathToDumpLogs = None

    print("Trying engine path:")
    print(enginePath)

    if(enginePath.exists() and enginePath.is_file()):
        ConfigClass.pathToEngineExecutable = enginePath.resolve()
        print("Engine path valid!")
    else:
        print("No valid path to the engine executable was supplied.")
        print("Please try --help for more information.")
        return

    configPath = Path(args.path).absolute().resolve()
    if(configPath.exists() and configPath.is_file()):
        print("avTests.cfg file valid!")
    else:
        print("The avTests.cfg file provided was not found.")
        print("Please try --help for more information.")
        return

    if(args.log != None):
        dumpLogsPath = Path(args.log).absolute().resolve()
        if(dumpLogsPath.exists() and dumpLogsPath.is_dir()):
            print("Dumping logs to path %s" % str(dumpLogsPath))
            ConfigClass.pathToDumpLogs = dumpLogsPath
        else:
            print("Unable to dump logs to path %s" % str(dumpLogsPath))

    results = beginRun(configPath.resolve())
    printResults(results)

    if(args.output):
        writer = JUnitFileWriter()
        writer.write(results, Path(args.output))

    processExitCode(results)

if __name__ == "__main__":
    main()
