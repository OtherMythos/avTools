from assetModules.AssetModule import *

import subprocess
import os

class AssetModuleXCF(AssetModule):
    def __init__(self):
        self.extension = ".xcf"

    def exportForFile(self, filePath, inputDirectory, outputDirectory):
        retPath = filePath.with_suffix(".png")
        outputTarget = self.prepareOutputDirectoryForFile(retPath, inputDirectory, outputDirectory, True)
        self.exportGimpProject(filePath, str(outputTarget))


    def createXCFExportFile(self):
        data ='''#!/bin/bash
echo $1
echo $2
{
cat <<EOF
(define (convert-xcf-to-jpeg filename outfile)
    (let* (
            (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename )))
            (drawable (car (gimp-image-merge-visible-layers image CLIP-TO-IMAGE)))
            )
        (file-png-save 1 image drawable outfile outfile 1 0 0 0 0 0 0)
        (gimp-image-delete image) ; ... or the memory will explode
    )
)

(gimp-message-set-handler 1) ; Messages to standard output
EOF

#for i in *.xcf; do
#  echo "(gimp-message \\"$i\\")"
#  echo "(convert-xcf-to-jpeg \\"$i\\" \\"${i%%.xcf}.png\\")"
#done
echo "(gimp-message \\"${1}\\")"
echo "(convert-xcf-to-jpeg \\"${1}\\" \\"${2}\\")"

echo "(gimp-quit 0)"

} | gimp -i -b -
'''

        execFile = open("/tmp/export.sh", "w")
        execFile.write(data)
        execFile.close()

    '''
    Export an xcf (gimp) file to a specified location.
    '''
    def exportGimpProject(self, filePath, outputPath):
        print("exporting xcf file at path '%s' to directory '%s'" % (filePath, outputPath))

        self.createXCFExportFile()

        devnull = open(os.devnull, 'w')
        process = subprocess.Popen(["bash", "/tmp/export.sh", filePath, outputPath], stdout=devnull, stderr=devnull)
        process.wait()
        devnull.close()