from assetModules.AssetModule import *

from cairosvg import svg2png

class AssetModuleSVG(AssetModule):
    def __init__(self, settings):
        super().__init__(settings)
        self.extension = ".svg"

    def exportForFile(self, filePath):
        retPath = filePath.with_suffix(".png")
        outputTarget = self.prepareOutputDirectoryForFile(retPath, True)

        svg2png(url=str(filePath),write_to=str(outputTarget))