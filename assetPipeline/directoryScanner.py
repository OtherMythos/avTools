from pathlib import Path
from exportManager import ExportManager

import os

class DirectoryScanner:

    def __init__(self, exportManager, inputPath, outputPath):
        self.input = Path(inputPath)
        self.output = Path(outputPath)
        self.exportManager = exportManager;
        pass

    def scanPaths(self):
        #First check if the input directory actually exists.
        if not self.input.exists():
            print("ERROR: Input directory '%s' does not exist." % self.input)
            return False
        if not self.input.is_dir():
            print("ERROR: Input directory '%s' is not a directory." % self.input)
            return False

        self.traverseInputDirectory(self.input)

        return True

    '''
    Traverse the input directory for files to convert.
    '''
    def traverseInputDirectory(self, path):
        for root, subdirs, files in os.walk( str(path) ):
            rootPath = Path(root)
            for file in files:
                filePath = rootPath / file
                if(filePath.suffix == ".blend"):
                    #Blender file.
                    outputTargetDirectory = self.prepareOutputDirectoryForFile(filePath)
                    self.exportManager.exportBlenderFile(filePath, outputTargetDirectory);

    '''
    When it's time to write an output file from the input, check the output directory contains the correct structure, similar to the input.
    If it does not, create the appropriate directory structure.
    '''
    def prepareOutputDirectoryForFile(self, inputFilePath):
        relativePath = inputFilePath.relative_to(self.input)
        outputTargetPath = self.output / relativePath

        #Just the parent directory, without the file name.
        parentPath = outputTargetPath.parents[0]
        if not parentPath.exists():
            parentPath.mkdir(parents=True)

        return parentPath
