from pathlib import Path
from exportManager import ExportManager
from resourceMetaFile import *
import shutil
import fnmatch

import os

class DirectoryScanner:

    def __init__(self, exportManager, resourceMetaBase, settings):
        self.exportManager = exportManager
        self.resourceMetaBase = resourceMetaBase

        self.input = Path(settings.inputDir)
        self.output = Path(settings.outputDir)
        self.targetProfile = settings.targetProfile
        self.linkFiles = settings.linkFiles

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

    def determineTargetProfile(self):
        if self.targetProfile is not None:
            return self.targetProfile

        return self.resourceMetaBase.defaultProfile

    def isPathBlacklistedByResourceMeta(self, filePath):
        for f in self.resourceMetaBase.blacklistedFiles:
            if fnmatch.fnmatch(filePath, f):
                return True

        return False

    '''
    Traverse the input directory for files to convert.
    '''
    def traverseInputDirectory(self, path):
        targetProfile = self.determineTargetProfile()

        for root, subdirs, files in os.walk( str(path) ):
            rootPath = Path(root)
            if self.isPathBlacklistedByResourceMeta(rootPath.stem):
                print("Skipping directory %s as blacklisted by resourceMetaBase" % root)
                continue

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
                if self.isPathBlacklistedByResourceMeta(file):
                    print("Skipping file %s as blacklisted by resourceMetaBase" % file)
                    continue

                resSettings = currentDirMetaFile.determineResourceEntrySettings(self.resourceMetaBase, file, targetProfile)
                filePath = rootPath / file

                if resSettings.ignore:
                    print("ignoring %s" % filePath)
                    continue

                if(filePath.suffix in self.blacklistSuffixes):
                    print("skipping %s" % filePath)
                    continue

                #outputTargetDirectory = self.prepareOutputDirectoryForFile(filePath)
                successful = self.exportManager.exportAssetOfExtension(filePath.suffix, filePath)
                if not successful:
                    #The file extension was not recognised, so just copy the file over.
                    self.exportManager.copyFile(filePath, resSettings)

    '''
    When execution finishes, perform some final checks.
    '''
    def finishExecutionRun(self):
        print("Finishing export")
        #Check whether any xml files were left without a .mesh result
        self.findOrphanedMeshXMLFiles(self.output)


    def findOrphanedMeshXMLFiles(self, path):
        print("scanning for orphaned mesh XML files")
        for root, subdirs, files in os.walk( str(path) ):
            rootPath = Path(root)
            for file in files:
                filePath = rootPath / file
                suffix = ''.join(filePath.suffixes)
                if(".mesh.xml" in suffix):
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
