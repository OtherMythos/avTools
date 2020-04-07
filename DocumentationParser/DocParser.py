#!/usr/bin/python3

import configparser
from pathlib import Path
from FileParser import *
import os
import argparse
import sys

def main():
    helpText = '''
    A script to parse c++ files and generate documentation information.
    It reads in comments left by squirrel function definitions, and uses those to generate the appropriate information.
    '''

    parser = argparse.ArgumentParser(description = helpText)
    #position argument
    parser.add_argument("-p", "--path", help="A path to a directory containing the engine source code.", default="/home/edward/Documents/avEngine/src")
    args = parser.parse_args()

    sourcePath = Path(args.path).absolute().resolve()

    print("Searching recursively in path:")
    print(sourcePath)

    if(sourcePath.exists() and sourcePath.is_dir()):
        parseFiles(sourcePath)
    else:
        print("No valid path to a directory was supplied.")
        print("Please try --help for more information.")
        return

main()
