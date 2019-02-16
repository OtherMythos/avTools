#!/usr/bin/python3

import configparser
from pathlib import Path
from TestPlanExecution import *
import ConfigClass
import os

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

def main(testConfig):
    ConfigClass.pathToEngineExecutable = "/home/edward/Documents/avEngine/build/av"
    parseTestMasterFile(testConfig)
    runTestProject(testConfig, "integration")

main("/home/edward/Documents/avTests/avTests.cfg")
