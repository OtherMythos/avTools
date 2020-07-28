import subprocess
import os


class ExportManager:

    def __init__(self, blenderPath):
        self.blenderPath = blenderPath

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
        process = subprocess.Popen([str(self.blenderPath), "-b", str(filePath), "--python", "../blenderExporter/exportTest.py", "--", str(outputPath)], stdout=devnull, stderr=devnull)
        devnull.close()
