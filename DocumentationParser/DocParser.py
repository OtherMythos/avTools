#!/usr/bin/python3

import configparser
from pathlib import Path
from FileParser import FileParser
from FileWriter import *
import os
import argparse
import sys

def beginFileParse(sourcePath):
    return parseFiles(sourcePath)

def writeRstFiles(namespaces, targetDirectory):
    writeNamespacesRst(targetDirectory, namespaces)

def main():
    helpText = '''
    A script to parse c++ files and generate documentation information.
    It reads in comments left by squirrel function definitions, and uses those to generate the appropriate information.
    '''

    parser = argparse.ArgumentParser(description = helpText)
    #position argument
    parser.add_argument("-p", "--path", help="A path to a directory containing the engine source code.", default="/home/edward/Documents/avEngine/src")
    parser.add_argument("-o", "--out", help="A path to the directory to place the rst files.", default="/tmp")
    args = parser.parse_args()

    sourcePath = Path(args.path).absolute().resolve()
    dirPath = Path(args.out).absolute().resolve()

    print("Searching recursively in path:")
    print(sourcePath)

    if(sourcePath.exists() and sourcePath.is_dir()):
        parser = FileParser()
        parser.parseFiles(sourcePath)

        print("FOUND: " + str(parser.foundData))

        writer = FileWriter(parser.foundData)
        writer.writeRst(dirPath)

main()
