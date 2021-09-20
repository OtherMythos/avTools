#!/usr/bin/python3

import argparse
from directoryScanner import DirectoryScanner
from exportManager import ExportManager
from pathlib import Path
from resourceMetaBase import *

def main():
    helpText = '''A script capable of taking asset project files and producing resources which can be accepted by the avEngine.
    For instance, producing a .mesh file from a .blend file.
    This tool is intended to automate the procedure of creating these objects manually.

    This tool accepts an input and output directory. The input directory will be scanned for resource project files, and the output from the conversion will be written to the output directory.
    A copy of the directory structure will be produced for the output.
    '''

    parser = argparse.ArgumentParser(description = helpText)

    parser.add_argument('InputDirectory', metavar='I', type=str, nargs='?', help='A path to the input directory.', default=None)
    parser.add_argument('OutputDirectory', metavar='O', type=str, nargs='?', help='A path to the output directory.', default=None)

    parser.add_argument("-p", "--purge", help="Purge XML files produced from blender export", default=True, type=bool, nargs='?')

    parser.add_argument("-b", "--blender", help="The path to a blender executable.", default="blender")
    args = parser.parse_args()

    if args.InputDirectory is None or args.OutputDirectory is None:
        print("Please provide both an input and output directory path")
        return


    shouldPurgeXML = False
    if args.purge is None:
        shouldPurgeXML = True

    exporter = ExportManager(args.blender)
    if not exporter.executableValid():
        print("Invalid path passed for blender executable.")
        return

    resourceMetaBase = ResourceMetaBase()
    resBasePath = Path(args.InputDirectory) / Path("resourceMetaBase.json")
    if resBasePath.exists() and resBasePath.is_file():
        print("Found resBase file at path %s" % str(resBasePath))
        resourceMetaBase.parseFile(str(resBasePath))
    else:
        print("Could not find resourceMetaBase.json in path %s\nResource profiles will be disabled." % str(resBasePath))


    scanner = DirectoryScanner(exporter, resourceMetaBase, args.InputDirectory, args.OutputDirectory)
    result = scanner.scanPaths()
    if not result:
        #Something failed
        return

    outputPath = Path(args.OutputDirectory)
    scanner.finishExecutionRun()
    if shouldPurgeXML:
        exporter.recursivePurgeXMLMeshes(outputPath)

if __name__ == "__main__":
    main()
