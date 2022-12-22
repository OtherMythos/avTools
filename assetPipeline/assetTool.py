#!/usr/bin/python3

import argparse
from directoryScanner import DirectoryScanner
from exportManager import ExportManager
from settings import Settings
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

    parser.add_argument('-i', '--input', type=str, nargs='?', help='A path to the input directory.', default=None)
    parser.add_argument('-o', '--output', type=str, nargs='?', help='A path to the output directory.', default=None)

    parser.add_argument('--link', help="Symlink files rather than copying them to the output directory.", action='store_true')
    parser.add_argument('--clean', help="Clean the output directory.", action='store_true')
    parser.add_argument("-p", "--profile", help="Target profile to use during export", default=None)
    parser.add_argument("-m", "--modules", help="Define the custom asset modules to use for this export.", nargs='*', default=[])

    parser.add_argument("-b", "--blender", help="The path to a blender executable.", default="blender")
    args = parser.parse_args()

    if args.input is None or args.output is None:
        print("Please provide both an input and output directory path")
        return

    settings = Settings(args.input, args.output, args.blender, args.profile, args.link, args.modules)
    if not settings.blenderExecutableValid():
        print("Invalid path passed for blender executable.")
        return

    exporter = ExportManager(settings)

    resourceMetaBase = ResourceMetaBase()
    resBasePath = Path(args.input) / Path("resourceMetaBase.json")
    if resBasePath.exists() and resBasePath.is_file():
        print("Found resBase file at path %s" % str(resBasePath))
        result = resourceMetaBase.parseFile(str(resBasePath))
        if not result:
            print("Error when parsing resourceMetaBase.json\nResource profiles will be disabled.")
    else:
        print("Could not find resourceMetaBase.json in path %s\nResource profiles will be disabled." % str(resBasePath))

    scanner = DirectoryScanner(exporter, resourceMetaBase, settings)
    result = scanner.scanPaths()
    if not result:
        #Something failed
        return

    outputPath = Path(args.output)
    scanner.finishExecutionRun()
    if args.clean:
        exporter.recursivePurgeXMLMeshes(outputPath)

if __name__ == "__main__":
    main()
