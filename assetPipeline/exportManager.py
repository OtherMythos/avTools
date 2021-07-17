import subprocess
import os
from pathlib import Path
import shutil

class ExportManager:

    def __init__(self, blenderPath):
        self.blenderPath = blenderPath
        #If at any point we tried to export a blend file, some checks might be performed later.
        self.exportedBlenderFile = False

        self.blenderExportFile = "../blenderExporter/exportTest.py"

        self.checkFiles()

    def checkFiles(self):
        #TODO there's a bug here if not in a same directory as this file.
        self.blenderExportFileExists = Path(self.blenderExportFile).exists()

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

    '''
    Export a blender file to a specified output.
    '''
    def exportBlenderFile(self, filePath, outputPath):
        if not self.blenderExportFileExists:
            print("Blender export file at path %s does not exist" % self.blenderExportFile)
            return
        print("exporting blender file at path '%s' to directory '%s'" % (filePath, outputPath))

        #./blender -b ~/Documents/meshTests/newMesh/Grave.blend --python ~/Documents/avTools/exportTest.py -- /tmp/3
        devnull = open(os.devnull, 'w')
        process = subprocess.Popen([str(self.blenderPath), "-b", str(filePath), "--python", self.blenderExportFile, "--", str(outputPath)], stdout=devnull, stderr=devnull)
        process.wait()
        #print(process.communicate())
        devnull.close()

        self.exportedBlenderFile = True
