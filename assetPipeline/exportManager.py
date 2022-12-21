import subprocess
import os
from pathlib import Path
import shutil

'''
Contains functions relating to the exportation of resources.
This class contains little logic about which files to export,
just the logic of how to export a provided path.
'''
class ExportManager:

    def __init__(self, blenderPath):
        self.assetModules = {}
        self.copyAssetModule = None

        self.loadCopyAssetModule()
        self.loadAssetModule("AssetModuleSVG")
        self.loadAssetModule("AssetModuleXCF")
        self.loadAssetModule("AssetModuleBlend")

        self.assetModules[".blend"].setBlendPath(blenderPath)

    def loadCopyAssetModule(self):
        module = __import__("assetModules.AssetModuleCopy", fromlist=["assetModules"])
        assetClass = getattr(module, "AssetModuleCopy")
        self.copyAssetModule = assetClass()

    def loadAssetModule(self, name):
        module = __import__("assetModules." + name, fromlist=["assetModules"])
        assetClass = getattr(module, name)
        assetModule = assetClass()
        self.assetModules[assetModule.getExtension()] = assetModule

    def exportAssetOfExtension(self, extension, filePath, inputDir, outputDir):
        if not extension in self.assetModules:
            return False

        print("Exporting %s" % filePath)
        self.assetModules[extension].exportForFile(filePath, inputDir, outputDir)

        return True




    def recursivePurgeXMLMeshes(self, targetDirectory):
        print("Purging .mesh.xml files in directory: %s" % str(targetDirectory) )
        for root, subdirs, files in os.walk( str(targetDirectory) ):
            for i in files:
                if ".mesh.xml" in i:
                    #Delete the file
                    targetFile = Path(root) / i
                    os.remove(targetFile)

    def executableValid(self):
        if os.path.isfile(self.blenderPath):
            return True
        if shutil.which(self.blenderPath) is not None:
            return True

        return False

    '''
    Export an Ogre .mesh.xml file to a .mesh format.
    '''
    def exportOgreMeshXML(self, filePath, outputPath):
        print("Exporting %s to %s" % (str(filePath), str(outputPath)))
        devnull = open(os.devnull, 'w')
        process = subprocess.Popen(["OgreMeshTool", "-e", "-t", "-ts", "4", "-v2", "-O", "puqs", str(filePath), str(outputPath)], stdout=devnull, stderr=devnull)
        process.wait()

    def exportOgreSkeletonXML(self, filePath, outputPath):
        print("Exporting %s to %s" % (str(filePath), str(outputPath)))
        devnull = open(os.devnull, 'w')
        process = subprocess.Popen(["OgreMeshTool", "-e", "-t", "-ts", "4", "-v2", "-O", "puqs", str(filePath), str(outputPath)], stdout=devnull, stderr=devnull)
        process.wait()

    #TODO maybe I should separate inputDir and outputDir as parameters for the class, and assets just have access to it somehow.
    def copyFile(self, filePath, inputDir, outputDir, resSettings):
        #TODO implement width, height, widthDiv, heightDiv
        self.copyAssetModule.copyFile(filePath, inputDir, outputDir, resSettings)