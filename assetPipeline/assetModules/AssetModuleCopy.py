from assetModules.AssetModule import *

'''
A special type of asset module, dealing with copying a file from one location to another.
'''
class AssetModuleCopy(AssetModule):
    def __init__(self):
        self.extension = None
