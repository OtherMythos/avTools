from pathlib import Path
from exportManager import ExportManager
from resourceMetaFile import *
import shutil

import os

class DirectoryScanner:

    def __init__(self, exportManager, resourceMetaBase, inputPath, outputPath, targetProfile):
        self.input = Path(inputPath)
        self.output = Path(outputPath)
        self.exportManager = exportManager
        self.resourceMetaBase = resourceMetaBase
        self.targetProfile = targetProfile

        self.blacklistSuffixes = [".blend1", ".swp"]
        self.blacklistFiles = ["resourceMetaBase.json", "resourceMeta.json"]

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

    def determinTargetProfile(self):
        if self.targetProfile is not None:
            return self.targetProfile

        return self.resourceMetaBase.defaultProfile

    '''
    Traverse the input directory for files to convert.
    '''
    def traverseInputDirectory(self, path):
        targetProfile = self.determineTargetProfile()

        for root, subdirs, files in os.walk( str(path) ):
            rootPath = Path(root)
            targetDirectoryResFile = rootPath / Path("resourceMeta.json")
            currentDirMetaFile = ResourceMetaFile()
            currentDirMetaFileValid = False

            if self.resourceMetaBase.valid:
                #Only check for resourceMeta files if the meta base file is valid.
                if targetDirectoryResFile.exists() and targetDirectoryResFile.is_file():
                    currentDirMetaFileValid = currentDirMetaFile.parseFile(str(targetDirectoryResFile))
                else:
                    print("Could not find a valid resourceMeta.json in directory %s" % root)

            if currentDirMetaFileValid:
                print("Found resourceMeta.json at path %s" % targetDirectoryResFile)
                result = currentDirMetaFile.validateAgainstProfiles(self.resourceMetaBase)
                if not result:
                    print("Skipping directory due to invalid resourceMeta file.")
                    continue


            for file in files:
                if file in self.blacklistFiles:
                    continue

                resSettings = currentDirMetaFile.determineResourceEntrySettings(self.resourceMetaBase, file, targetProfile)
                filePath = rootPath / file

                if resSettings.ignore:
                    print("ignoring %s" % filePath)
                    continue

                if(filePath.suffix in self.blacklistSuffixes):
                    print("skipping %s" % filePath)
                    continue
                elif(filePath.suffix == ".blend"):
                    #Blender file.
                    outputTargetDirectory = self.prepareOutputDirectoryForFile(filePath)
                    self.exportManager.exportBlenderFile(filePath, outputTargetDirectory)
                elif(filePath.suffix == ".xcf"):
                    retPath = filePath.with_suffix(".png")
                    outputTarget = self.prepareOutputDirectoryForFile(retPath, True)
                    self.exportManager.exportGimpProject(filePath, str(outputTarget))
                else:
                    #TODO implement width, height, widthDiv, heightDiv
                    outPath = filePath
                    if resSettings.outDir != "":
                        outPath = rootPath / resSettings.outDir
                    #Copy the file over.
                    outputTarget = self.prepareOutputDirectoryForFile(outPath, True)
                    shutil.copyfile(filePath, outputTarget)
                    print("copied %s to %s" % (filePath, outputTarget))


    '''
    When execution finishes, perform some final checks.
    '''
    def finishExecutionRun(self):
        print("Finishing export")
        #Check whether any xml files were left without a .mesh result
        self.findOrphanedMeshXMLFiles(self.output)


    def findOrphanedMeshXMLFiles(self, path):
        print("scanning")
        for root, subdirs, files in os.walk( str(path) ):
            rootPath = Path(root)
            for file in files:
                filePath = rootPath / file
                suffix = ''.join(filePath.suffixes)
                if(suffix == ".mesh.xml"):
                    #Found a mesh.xml file, now check if it has no .mesh file.
                    #Remove the suffix
                    targetFile = filePath.with_suffix("")
                    if targetFile.exists():
                        continue
                    print("Found orphan mesh.xml file: %s" % str(filePath))
                    self.exportManager.exportOgreMeshXML(filePath, targetFile)
                elif(suffix == ".skeleton.xml"):
                    #Same as above but with skeletons.
                    targetFile = filePath.with_suffix("")
                    if targetFile.exists():
                        continue
                    print("Found orphan skeleton.xml file: %s" % str(filePath))
                    self.exportManager.exportOgreSkeletonXML(filePath, targetFile)

    '''
    When it's time to write an output file from the input, check the output directory contains the correct structure, similar to the input.
    If it does not, create the appropriate directory structure.
    '''
    def prepareOutputDirectoryForFile(self, inputFilePath, includeFileName = False):
        relativePath = inputFilePath.relative_to(self.input)
        outputTargetPath = self.output / relativePath

        #Just the parent directory, without the file name.
        parentPath = outputTargetPath.parents[0]
        if not parentPath.exists():
            parentPath.mkdir(parents=True)

        if includeFileName:
            parentPath = parentPath / inputFilePath.name

        return parentPath
