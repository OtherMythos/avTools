import subprocess
import os
from pathlib import Path

class ExportManager:

    def __init__(self, blenderPath):
        self.blenderPath = blenderPath

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
        print("exporting blender file at path '%s' to directory '%s'" % (filePath, outputPath))

        #./blender -b ~/Documents/meshTests/newMesh/Grave.blend --python ~/Documents/avTools/exportTest.py -- /tmp/3
        devnull = open(os.devnull, 'w')
        process = subprocess.Popen([str(self.blenderPath), "-b", str(filePath), "--python", "../blenderExporter/exportTest.py", "--", str(outputPath)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        devnull.close()
