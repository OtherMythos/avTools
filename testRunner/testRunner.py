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
    file = Path(path)
    targetPath = file.absolute().parent / testProjectPath
    if(not targetPath.exists()):
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
        execution.execute()

    return True

def beginRun(testConfig):
    ConfigClass.pathToEngineExecutable = "/home/edward/Documents/avEngine/build/av"
    parseTestMasterFile(testConfig)
    runTestProject(testConfig, "integration")

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
    print(enginePath)
    if(enginePath.exists() and enginePath.is_file()):
        ConfigClass.pathToEngineExecutable = enginePath.resolve()
    else:
        print("No valid path to the engine executable was supplied. Failing.")

    beginRun(args.path)

main()
