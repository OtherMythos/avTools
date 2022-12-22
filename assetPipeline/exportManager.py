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

    def __init__(self, settings):
        self.settings = settings

        self.assetModules = {}
        self.copyAssetModule = None

        #Default modules
        self.loadCopyAssetModule()
        self.loadAssetModule("AssetModuleSVG")
        self.loadAssetModule("AssetModuleXCF")
        self.loadAssetModule("AssetModuleBlend")

        self.loadUserModules()

    def loadCopyAssetModule(self):
        module = __import__("assetModules.AssetModuleCopy", fromlist=["assetModules"])
        assetClass = getattr(module, "AssetModuleCopy")
        self.copyAssetModule = assetClass(self.settings)

    def loadUserModules(self):
        if self.settings.modules is None:
            return

        for i in self.settings.modules:
            self.loadAssetModule(i)

    def loadAssetModule(self, name):
        module = __import__("assetModules." + name, fromlist=["assetModules"])
        assetClass = getattr(module, name)
        assetModule = assetClass(self.settings)
        self.assetModules[assetModule.getExtension()] = assetModule

    def exportAssetOfExtension(self, extension, filePath):
        if not extension in self.assetModules:
            return False

        print("Exporting %s" % filePath)
        self.assetModules[extension].exportForFile(filePath)

        return True




    def recursivePurgeXMLMeshes(self, targetDirectory):
        print("Purging .mesh.xml files in directory: %s" % str(targetDirectory) )
        for root, subdirs, files in os.walk( str(targetDirectory) ):
            for i in files:
                if ".mesh.xml" in i:
                    #Delete the file
                    targetFile = Path(root) / i
                    os.remove(targetFile)

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

    def copyFile(self, filePath, resSettings):
        #TODO implement width, height, widthDiv, heightDiv
        self.copyAssetModule.copyFile(filePath, resSettings)