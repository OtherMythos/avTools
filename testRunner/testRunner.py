#!/usr/bin/python3

import configparser
from pathlib import Path
from TestPlanExecution import *
import ConfigClass
import os
import argparse
import sys

def parseTestMasterFile(path):
    config = configparser.ConfigParser()
    config.read(path)

    for key in config:
        if(key == "DEFAULT"):
            continue

def runTestProject(path, testProjectPath):
    targetPath = path.absolute().parent / testProjectPath
    results = []
    if(not targetPath.exists()):
        print("Target path %s as specified in the avTests.cfg file does not exist." % testProjectPath)
        return False

    testPlanPaths = []
    #Find the paths to the test plans
    for d in os.listdir(targetPath):
        testPlanPath = targetPath / d
        if(not os.path.isdir(testPlanPath)):
            continue

        testPlanPaths.append(testPlanPath)

    for d in testPlanPaths:
        execution = TestPlanExecution(d)
        result = execution.execute()
        results.append(result)

    printResults(results)

    return True

def beginRun(testConfig):
    parseTestMasterFile(testConfig)
    runTestProject(testConfig, "integration")

def gatherResultsInfo(results):
    totalTestsRan = 0
    totalFailures = 0
    for i in results:
        totalTestsRan += i["TotalTests"]
        totalFailures += i["TotalFailures"]

    failureTestPlanCount = 0
    for i in results:
        if(i["TotalFailures"] > 0):
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
    info = gatherResultsInfo(results)
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
    args = parser.parse_args()

    enginePath = Path(args.engine).absolute().resolve()
    ConfigClass.pathToEngineExecutable = ""

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

    beginRun(configPath.resolve())

main()
