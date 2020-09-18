import subprocess
import os
from pathlib import Path

class ExportManager:

    def __init__(self, blenderPath):
        self.blenderPath = blenderPath

        self.blenderExportFile = "../blenderExporter/exportTest.py"

        self.checkFiles()

    def checkFiles(self):
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
        if not os.path.isfile(self.blenderPath):
            return False

        return True

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
