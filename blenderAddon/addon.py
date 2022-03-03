bl_info = {
    "name": "Random addon for me",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import subprocess
import os
from pathlib import Path
import json
import shutil

from io_ogre.ogre.mesh import dot_mesh
from io_ogre.ogre.skeleton import dot_skeleton


av_plugin_config = {
    "engine_path": "/Users/edward/Documents/avEngine/build/Debug/av.app/Contents/MacOS/av",
    "material_editor_av_setup": "/Users/edward/Documents/materialEditor/avSetup.cfg",
}
_CONFIG_TAGS_ = ['AV_ENGINE_PATH', 'MATERIAL_EDITOR_AV_SETUP']

class avEngineBlenderAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def apply_preferences_to_config(self, context):
        addon_preferences = context.preferences.addons[__name__].preferences

        for key in _CONFIG_TAGS_:
            addon_pref_value = getattr(addon_preferences,key,None)
            if addon_pref_value is not None:
                av_plugin_config[key] = addon_pref_value
                print(addon_pref_value)

    AV_ENGINE_PATH: bpy.props.StringProperty(
        name=_CONFIG_TAGS_[0],
        subtype='FILE_PATH',
        default=av_plugin_config["engine_path"],
        update=apply_preferences_to_config
    )
    MATERIAL_EDITOR_AV_SETUP: bpy.props.StringProperty(
        name=_CONFIG_TAGS_[1],
        subtype='FILE_PATH',
        default=av_plugin_config["material_editor_av_setup"],
        update=apply_preferences_to_config
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, _CONFIG_TAGS_[0])
        layout.prop(self, _CONFIG_TAGS_[1])

class avEngineViewInEngine(bpy.types.Operator):
    """View in avEngine"""
    bl_idname = "avengine.view_in_engine"
    bl_label = "View in engine"
    bl_options = {'REGISTER'}

    def getTemporaryDir(self):
        #For unix alone.
        start = "/tmp"
        targetPath = Path(start) / Path("avEngineBlender")
        if(targetPath.exists()):
            try:
                shutil.rmtree(targetPath)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

        targetPath.mkdir(parents=True)
        return targetPath

    def createAvSetupFile(self, basePath, targetMesh, targetMaterialFile):
        targetPath = basePath / Path("avSetupAddition.cfg")
        data = {
            'OgreResources':{
                'General': [
                    ['FileSystem', '/tmp/avEngineBlender']
                ]
            },
            'UserSettings':{
                'StartMesh': targetMesh,
                'StartFile': targetMaterialFile
            }
        }

        json_string = json.dumps(data)

        with open(str(targetPath), 'w') as outfile:
            outfile.write(json_string)

        return targetPath

    def getProjectMaterialFile(self):
        #if not saved make it save to /tmp and alert the user to that.
        if bpy.context.blend_data.filepath == '':
            return '/tmp/material.material.json'
        return str(Path(bpy.context.blend_data.filepath).parent / Path(bpy.path.basename(bpy.context.blend_data.filepath)).stem) + ".material.json"

    '''
    Parse the json data of a material file which already exists, trying to insert the missing values from inputData.
    This is used to make sure the extension doesn't destroy any material settings which already exist in a material file, while also being able to add new data.
    '''
    def determineSharedMaterialData(self, inputData, targetPath):
        path = Path(targetPath)
        if not path.exists() or not path.is_file():
            #The file does not exist so no need to change the data.
            return inputData

        readData = None
        with open(path, 'r') as outfile:
            readData = json.load(outfile)

        if "pbs" in readData:
            #Go through the provided list, checking if those values are present in it.
            for i in inputData["pbs"]:
                if not i in readData["pbs"]:
                    readData["pbs"][i] = inputData["pbs"][i]

        return readData

    def exportMeshes(self, tempDir):
        materialData = {
            "pbs":{
            }
        }

        firstMesh = None
        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH':
                continue
            meshName = ob.data.name + ".mesh"

            for mat in ob.material_slots:
                materialData["pbs"][mat.name] = { }

            dot_mesh(ob, tempDir)
            dot_skeleton(ob, tempDir / (ob.data.name + ".skeleton"))

            if firstMesh is None:
                firstMesh = meshName

        outMaterialFilePath = self.getProjectMaterialFile()
        processedMaterialData = self.determineSharedMaterialData(materialData, outMaterialFilePath)
        json_string = json.dumps(processedMaterialData)

        with open(outMaterialFilePath, 'w') as outfile:
            outfile.write(json_string)

        return firstMesh

    def viewingInEngine(self):
        print("Viewing single object in engine.")

        #Generate avSetup file.
        tempDir = self.getTemporaryDir()
        firstMesh = self.exportMeshes(tempDir)

        createdSetupFile = self.createAvSetupFile(tempDir, firstMesh, str(tempDir / self.getProjectMaterialFile()))

        devnull = open(os.devnull, 'w')
        pathToEngineExecutable = av_plugin_config["engine_path"]
        pathToMaterialEditor = av_plugin_config["material_editor_av_setup"]
        process = subprocess.Popen([pathToEngineExecutable, pathToMaterialEditor, createdSetupFile], stdout=devnull, stderr=devnull)
        devnull.close()


    def execute(self, context):
        scene = context.scene
        self.viewingInEngine()

        return {'FINISHED'}

class VIEW3D_MT_menu(bpy.types.Menu):
    bl_label = "avEngine"

    def draw(self, context):
        self.layout.operator(avEngineViewInEngine.bl_idname)

def addmenu_callback(self, context):
    self.layout.menu("VIEW3D_MT_menu")

def add_preview_button(self, context):
    layout = self.layout
    op = layout.operator( avEngineViewInEngine.bl_idname, text='', icon='VIEWZOOM' )

def register():
    bpy.utils.register_class(avEngineViewInEngine)
    bpy.utils.register_class(VIEW3D_MT_menu)
    bpy.utils.register_class(avEngineBlenderAddonPreferences)

    bpy.types.VIEW3D_HT_header.append(addmenu_callback)

    bpy.types.VIEW3D_PT_tools_active.append(add_preview_button)

def unregister():
    bpy.utils.unregister_class(avEngineViewInEngine)
    bpy.utils.unregister_class(avEngineBlenderAddonPreferences)

    bpy.types.VIEW3D_HT_header.remove(addmenu_callback)
    bpy.utils.unregister_class(VIEW3D_MT_menu)

    bpy.types.VIEW3D_PT_tools_active.remove(add_preview_button)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
