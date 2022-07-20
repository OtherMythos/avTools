bl_info = {
    "name": "avEngine helper",
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

import xml.etree.cElementTree as ET

_CONFIG_TAGS_ = ['AV_ENGINE_PATH', 'MATERIAL_EDITOR_AV_SETUP', 'PROJECT_AV_SETUP']
av_plugin_config = {
    _CONFIG_TAGS_[0]: "/Users/edward/Documents/avEngine/build/Debug/av.app/Contents/MacOS/av",
    _CONFIG_TAGS_[1]: "/Users/edward/Documents/materialEditor/avSetup.cfg",
    _CONFIG_TAGS_[2]: "/Users/edward/Documents/rpgGame/avSetup.cfg",
}

#A helper script in the substance directory.
#This will automatically copy all textures and materials from the substance directory to the expected place.
copyInResourcesScript = '''
# #############################
#  avEngine helper script v1.0
#      copyInResources.py
# #############################

#This script will copy all textures and materials into the assets directory scructure.
#It assumes you have followed the suggested avEngine project structure, involving an assets directory.
#The resources will be added in a directory structure which mirrors how they were places in the meshes directory.

import os
from pathlib import Path
import shutil

def traceParentDirectory(startDir):
    tmpPath = startDir
    localPath = Path("")
    while(tmpPath != Path("/")):
        if tmpPath.name == "meshes":
            if tmpPath.parent.name == "assets":
                #Get the parent of local path to avoid the substance directory.
                return (tmpPath.parent, localPath.parent)
        localPath = Path(tmpPath.name) / localPath
        tmpPath = tmpPath.parent

    return None

def _copy(path, localPath, targetPath):
    parentPath = targetPath / localPath
    if not parentPath.exists():
        parentPath.mkdir(parents=True)

    totalPath = parentPath / str(path.name)
    print("Copying %s to %s" % (path, totalPath))
    shutil.copyfile(path, totalPath)

def copyInTexture(parent, localPath, path):
    targetPath = parent / "meshTextures"
    _copy(path, localPath, targetPath)

def copyInMaterial(parent, localPath, path):
    targetPath = parent / "meshMaterials"
    _copy(path, localPath, targetPath)

def main():
    startPath = Path(__file__).parent

    parentDir = traceParentDirectory(startPath)
    if parentDir is None:
        print("Could not find the location to place resources in.")
        print("This script expects an assets directory containing a meshes directory i.e res://assets/meshes/__substance_")
        return

    print("Parent dir: " + str(parentDir[0]))
    print("local path: " + str(parentDir[1]))

    for root, subdirs, files in os.walk( str(startPath) ):
        for file in files:
            if file.endswith(".png"):
                copyInTexture(parentDir[0], parentDir[1], startPath / file)
            elif file.endswith(".material.json"):
                copyInMaterial(parentDir[0], parentDir[1], startPath / file)



if __name__ == "__main__":
    main()
'''

def isEngineSettingsValid():
    global av_plugin_config

    targetPath = Path(av_plugin_config[_CONFIG_TAGS_[0]])
    if not targetPath.exists() or not targetPath.is_file():
        return False
    targetPath = Path(av_plugin_config[_CONFIG_TAGS_[1]])
    if not targetPath.exists() or not targetPath.is_file():
        return False

    return True

class avEngineBlenderAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def apply_preferences_to_config(self, context):
        global av_plugin_config
        addon_preferences = context.preferences.addons[__name__].preferences

        for key in _CONFIG_TAGS_:
            addon_pref_value = getattr(addon_preferences,key,None)
            if addon_pref_value is not None:
                av_plugin_config[key] = addon_pref_value

    AV_ENGINE_PATH: bpy.props.StringProperty(
        name=_CONFIG_TAGS_[0],
        subtype='FILE_PATH',
        default=av_plugin_config[_CONFIG_TAGS_[0]],
        update=apply_preferences_to_config
    )
    MATERIAL_EDITOR_AV_SETUP: bpy.props.StringProperty(
        name=_CONFIG_TAGS_[1],
        subtype='FILE_PATH',
        default=av_plugin_config[_CONFIG_TAGS_[1]],
        update=apply_preferences_to_config
    )
    PROJECT_AV_SETUP: bpy.props.StringProperty(
        name=_CONFIG_TAGS_[2],
        subtype='FILE_PATH',
        default=av_plugin_config[_CONFIG_TAGS_[2]],
        update=apply_preferences_to_config
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, _CONFIG_TAGS_[0])
        layout.prop(self, _CONFIG_TAGS_[1])
        layout.prop(self, _CONFIG_TAGS_[2])

class avEngineExportBase(bpy.types.Operator):

    def __init__(self):
        self.mAnimData = {}

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

    def getSubstancePainterPath(self):
        attemptFiles = [
            "/Applications/Adobe Substance 3D Painter/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter",
            "/Users/edward/Library/Application Support/Steam/steamapps/common/Substance 3D Painter 2022/Adobe Substance 3D Painter.app/Contents/MacOS/Adobe Substance 3D Painter"
        ]

        for i in attemptFiles:
            p = Path(i)
            if p.exists() and p.is_file():
                return i

        return None

    def createAvSetupFile(self, basePath, targetMesh=None, targetMaterialFile=None, targetStartScene=None, targetAnimFile=None):
        targetPath = basePath / Path("avSetupAddition.cfg")
        data = {
            'OgreResources':{
                'General': [
                    ['FileSystem', '/tmp/avEngineBlender']
                ]
            },
            'UserSettings':{
                'StartMesh': targetMesh,
                'StartFile': targetMaterialFile,
                'StartScene': targetStartScene,
                'StartAnimFile': targetAnimFile,
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

    def getProjectAvSceneFile(self):
        if bpy.context.blend_data.filepath == '':
            return 'scene.avscene'
        return str(Path(bpy.context.blend_data.filepath).parent / Path(bpy.path.basename(bpy.context.blend_data.filepath)).stem) + ".avscene"

    def getProjectAnimationFile(self):
        if bpy.context.blend_data.filepath == '':
            return 'avAnimation.xml'
        return str(Path(bpy.context.blend_data.filepath).parent / Path(bpy.path.basename(bpy.context.blend_data.filepath)).stem) + ".xml"

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

    def exportMeshes(self, tempDir, objects, exportMaterials=True):
        materialData = {
            "pbs":{
            }
        }

        firstMesh = None
        for ob in objects:
            if ob.type != 'MESH':
                continue
            meshName = ob.data.name + ".mesh"

            for mat in ob.material_slots:
                materialData["pbs"][mat.name] = { }

            meshPath = tempDir / meshName
            #I might have a linked mesh where multiple objects use the same mesh, so don't try and re-export it.
            if meshPath.exists():
                continue

            dot_mesh(ob, tempDir)
            dot_skeleton(ob, tempDir / (ob.data.name + ".skeleton"))

            if firstMesh is None:
                firstMesh = meshName

        if exportMaterials:
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
        firstMesh = self.exportMeshes(tempDir, bpy.context.selected_objects)

        createdSetupFile = self.createAvSetupFile(tempDir, targetMesh=firstMesh, targetMaterialFile=str(tempDir / self.getProjectMaterialFile()))

        pathToEngineExecutable = av_plugin_config[_CONFIG_TAGS_[0]]
        pathToMaterialEditor = av_plugin_config[_CONFIG_TAGS_[1]]
        self._openEngineWithArgs([pathToEngineExecutable, pathToMaterialEditor, createdSetupFile])


    ###
    def processCollection(self, idx, parent, col, exportAnimIds=False):
        # if not layerCol.is_visible:
        #     return
        # col = layerCol.collection
        #print("Processing collection with name " + layerCol.data.name)
        elem = ET.SubElement(parent, "empty")

        for ob in col.objects:
            if ob.type != 'MESH':
                continue
            if ob.hide_get():
                continue

            meshName = ob.data.name + ".mesh"
            print("Adding name with " +meshName)
            meshElem = ET.SubElement(elem, "mesh", name=ob.name, mesh=meshName)

            if exportAnimIds:
                if ob.animation_data is not None and len(self.mAnimData) < 15:
                    #This object has an animation
                    print(ob.name)
                    animIdx = len(self.mAnimData)
                    self.mAnimData[ob.name] = animIdx
                    meshElem.set("animIdx", str(animIdx))

            posElem = ET.SubElement(meshElem, "position", x=str(ob.location[0]), y=str(ob.location[2]), z=str(-ob.location[1]))
            scaleElem = ET.SubElement(meshElem, "scale", x=str(ob.scale[0]), y=str(ob.scale[2]), z=str(ob.scale[1]))
            ob.rotation_mode = 'QUATERNION'
            #0(w) goes first, z(3) and y(2) are flipped.
            quaternionElem = ET.SubElement(meshElem, "orientation", x=str(ob.rotation_quaternion[1]), y=str(ob.rotation_quaternion[3]), z=str(-(ob.rotation_quaternion[2])), w=str(ob.rotation_quaternion[0]))

        print(col.children)
        for ob in col.children:
            #for ob in col.children:
            #assert type(ob) is bpy.types.LayerCollection
            assert type(ob) is bpy.types.Collection
            print("collection: " + ob.name)
            self.processCollection(idx + 1, elem, ob, exportAnimIds=exportAnimIds)
    ###

    def exportAvSceneFile(self, path, exportAnimIds=False):
        c = bpy.context.scene.collection
        #c = bpy.context.collection

        root = ET.Element("scene")
        self.processCollection(0, root, c, exportAnimIds)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(path)

    def _openEngineWithArgs(self, args):
        print(" ".join([str(x) for x in args]))
        devnull = open(os.devnull, 'w')
        process = subprocess.Popen(args, stdout=devnull, stderr=devnull)
        devnull.close()

class avEngineExportSceneFile(avEngineExportBase):
    """Export avScene"""
    bl_idname = "avengine.export_scene"
    bl_label = "Export scene"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return isEngineSettingsValid()

    def execute(self, context):
        #TODO add a popup to select the proper path.
        self.exportAvSceneFile("/tmp/test.avscene")

        return {'FINISHED'}

class avEngineViewAnimationInEngine(avEngineExportBase):
    """View animation in engine"""
    bl_idname = "avengine.view_animation_in_engine"
    bl_label = "View animation in engine"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return isEngineSettingsValid()

    def exportAnimationForEngine(self, context, targetPath):
        print("Viewing animation scene in engine")

        animName = "testName"

        root = ET.Element("AnimationSequence")
        dataContainer = ET.SubElement(root, "data")
        animContainer = ET.SubElement(root, "animations")

        animTag = ET.SubElement(animContainer, animName)
        animTag.set("repeat", "true")
        animTag.set("end", str(context.scene.frame_end))

        startFrame = context.scene.frame_current
        for ob in bpy.context.visible_objects:
            animIdx = -1
            if ob.name in self.mAnimData:
                animIdx = self.mAnimData[ob.name]
            else:
                #has no animation
                continue

            #TODO change this to something else.
            dataEntry = ET.SubElement(dataContainer, "targetNode"+str(animIdx))
            dataEntry.set("type", "SceneNode")
            dataEntry.set("name", "SceneNode")

            track = ET.SubElement(animTag, "t")
            track.set("type", "transform")
            track.set("target", str(animIdx))

            if ob.animation_data is None:
                continue

            f = ob.animation_data.action.fcurves
            for i in f[0].keyframe_points:
                fr = int(i.co[0])
                context.scene.frame_set(fr)

                key = ET.SubElement(track, "k")
                key.set("t", str(fr))
                key.set("position", "%f, %f, %f" % (ob.location.x, ob.location.z, -ob.location.y))
                key.set("quat", "%f, %f, %f, %f" % (ob.rotation_quaternion.w, ob.rotation_quaternion.x, ob.rotation_quaternion.y, ob.rotation_quaternion.z))
                key.set("scale", "%f, %f, %f" % (ob.scale.x, ob.scale.z, ob.scale.y))

        context.scene.frame_set(startFrame)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(targetPath)

    def execute(self, context):
        tempDir = self.getTemporaryDir()

        projName = Path(bpy.path.basename(bpy.context.blend_data.filepath)).stem
        #targetScenePath = tempDir / self.getProjectAvSceneFile()
        targetScenePath = Path("/tmp/avEngineBlender/scene.avscene")
        print("Exporting scene to %s" % targetScenePath)
        self.exportAvSceneFile(str(targetScenePath), exportAnimIds=True)

        self.exportMeshes(tempDir, bpy.context.visible_objects)

        #targetAnimPath = tempDir / self.getProjectAnimationFile()
        targetAnimPath = Path("/tmp/avEngineBlender/avAnimation.xml")
        print("Exporting animation to %s" % targetAnimPath)
        self.exportAnimationForEngine(context, str(targetAnimPath))

        #View the exported anim in the engine.
        createdSetupFile = self.createAvSetupFile(tempDir, targetStartScene=str(targetScenePath), targetAnimFile=str(targetAnimPath))

        pathToEngineExecutable = av_plugin_config[_CONFIG_TAGS_[0]]
        pathToMaterialEditor = av_plugin_config[_CONFIG_TAGS_[1]]
        projectSetupFile = av_plugin_config[_CONFIG_TAGS_[2]]
        self._openEngineWithArgs([pathToEngineExecutable, projectSetupFile, pathToMaterialEditor, createdSetupFile])

        return {'FINISHED'}

class avEngineViewSceneInEngine(avEngineExportBase):
    """View scene in project"""
    bl_idname = "avengine.view_scene_in_project"
    bl_label = "View scene in project"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return isEngineSettingsValid()

    def viewingSceneInEngine(self):
        print("Viewing scene in engine.")

        #Generate avSetup file.
        tempDir = self.getTemporaryDir()

        projName = Path(bpy.path.basename(bpy.context.blend_data.filepath)).stem
        targetPath = tempDir / self.getProjectAvSceneFile()
        self.exportAvSceneFile(str(targetPath))

        self.exportMeshes(tempDir, bpy.context.visible_objects)

        createdSetupFile = self.createAvSetupFile(tempDir, targetStartScene=str(targetPath))

        pathToEngineExecutable = av_plugin_config[_CONFIG_TAGS_[0]]
        pathToMaterialEditor = av_plugin_config[_CONFIG_TAGS_[1]]
        projectSetupFile = av_plugin_config[_CONFIG_TAGS_[2]]
        self._openEngineWithArgs([pathToEngineExecutable, projectSetupFile, pathToMaterialEditor, createdSetupFile])

    def execute(self, context):
        self.viewingSceneInEngine()

        return {'FINISHED'}

class avEngineViewInEngine(avEngineExportBase):
    """View in avEngine"""
    bl_idname = "avengine.view_in_engine"
    bl_label = "View in engine"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return isEngineSettingsValid()

    def execute(self, context):
        scene = context.scene
        self.viewingInEngine()

        return {'FINISHED'}

class avEngineViewInProject(avEngineExportBase):
    """View in project, loading the various resources of the project."""
    bl_idname = "avengine.view_in_project"
    bl_label = "View in project"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        firstValid = isEngineSettingsValid()

        #Check the project file exists.
        targetPath = Path(av_plugin_config[_CONFIG_TAGS_[2]])
        secondValue = False
        if targetPath.exists() and targetPath.is_file():
            secondValue = True

        return firstValid and secondValue

    def viewingInEngine(self):
        print("Viewing single object in engine with project.")

        #Generate avSetup file.
        tempDir = self.getTemporaryDir()
        firstMesh = self.exportMeshes(tempDir, bpy.context.selected_objects)

        createdSetupFile = self.createAvSetupFile(tempDir, targetMesh=firstMesh, targetMaterial=str(tempDir / self.getProjectMaterialFile()))

        pathToEngineExecutable = av_plugin_config[_CONFIG_TAGS_[0]]
        pathToMaterialEditor = av_plugin_config[_CONFIG_TAGS_[1]]
        projectSetupFile = av_plugin_config[_CONFIG_TAGS_[2]]
        self._openEngineWithArgs([pathToEngineExecutable, projectSetupFile, pathToMaterialEditor, createdSetupFile])

    def execute(self, context):
        scene = context.scene
        self.viewingInEngine()

        return {'FINISHED'}


class avEngineCreateSubstancePainterProject(avEngineExportBase):
    """Export the mesh and create a substance painter project from it."""
    bl_idname = "avengine.view_in_substance_painter"
    bl_label = "View in substance painter"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def createSubstanceDir(self, meshName):
        if bpy.context.blend_data.filepath == '':
            raise Exception("Save project before viewing in substance painter.")

        projName = Path(bpy.path.basename(bpy.context.blend_data.filepath)).stem
        parentPath = Path(bpy.context.blend_data.filepath).parent
        substanceName = "__substance_" + str(projName) + "_" + meshName

        targetPath = parentPath / substanceName
        if targetPath.exists():
            raise Exception("Substance directory already exists %s" % str(targetPath))

        targetPath.mkdir(parents=True)

        #Copy in the script to submit textures.
        with open(targetPath / Path("copyInResources.py"), "w") as text_file:
            text_file.write(copyInResourcesScript)

        return targetPath

    def getSelectedMeshName(self):
        retVal = None
        #Just take the first of the selected meshes.
        for ob in bpy.context.selected_objects:
            retVal = ob.data.name
            break

        return retVal

    def exportSingleOgreMesh(self, targetDir):
        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH':
                continue
            #meshName = ob.data.name + ".mesh"

            dot_mesh(ob, targetDir)
            dot_skeleton(ob, targetDir)
            break

    def viewInSubstancePainter(self):
        print("viewing substance")
        substancePath = self.getSubstancePainterPath()
        if substancePath is None:
            raise Exception("Substance painter not found.")

        targetMeshName = self.getSelectedMeshName()
        if(targetMeshName is None):
            raise Exception("No selected mesh")
        targetDir = self.createSubstanceDir(targetMeshName)

        #Export an obj file for substance painter
        objPath = targetDir / (targetMeshName + ".obj")
        bpy.ops.export_scene.obj(filepath=str(objPath), use_selection=True)

        #Also export an ogre mesh so substance painter can use the material editor at a later date.
        self.exportSingleOgreMesh(str(targetDir))

        projFile = targetDir / (targetMeshName + ".spp")

        substanceVars = [substancePath, "--mesh", str(objPath), str(projFile)]
        print("executing substance process:")
        print(" ".join(substanceVars))

        devnull = open(os.devnull, 'w')
        process = subprocess.Popen(substanceVars, stdout=devnull, stderr=devnull)
        devnull.close()

    def execute(self, context):
        scene = context.scene
        self.viewInSubstancePainter()

        return {'FINISHED'}

class VIEW3D_MT_menu(bpy.types.Menu):
    bl_label = "avEngine"

    def draw(self, context):
        self.layout.operator(avEngineViewInEngine.bl_idname)
        self.layout.operator(avEngineViewInProject.bl_idname)
        self.layout.operator(avEngineExportSceneFile.bl_idname)
        self.layout.operator(avEngineViewSceneInEngine.bl_idname)
        self.layout.operator(avEngineViewAnimationInEngine.bl_idname)
        self.layout.operator(avEngineCreateSubstancePainterProject.bl_idname)

def addmenu_callback(self, context):
    self.layout.menu("VIEW3D_MT_menu")

def add_preview_button(self, context):
    layout = self.layout
    op = layout.operator( avEngineViewInEngine.bl_idname, text='', icon='VIEWZOOM' )

def register():
    bpy.utils.register_class(avEngineViewInEngine)
    bpy.utils.register_class(avEngineViewInProject)
    bpy.utils.register_class(avEngineExportSceneFile)
    bpy.utils.register_class(avEngineViewSceneInEngine)
    bpy.utils.register_class(avEngineViewAnimationInEngine)
    bpy.utils.register_class(avEngineCreateSubstancePainterProject)
    bpy.utils.register_class(VIEW3D_MT_menu)
    bpy.utils.register_class(avEngineBlenderAddonPreferences)

    bpy.types.VIEW3D_HT_header.append(addmenu_callback)

    bpy.types.VIEW3D_PT_tools_active.append(add_preview_button)

def unregister():
    bpy.utils.unregister_class(avEngineViewInEngine)
    bpy.utils.unregister_class(avEngineBlenderAddonPreferences)
    bpy.utils.unregister_class(avEngineViewInProject)
    bpy.utils.unregister_class(avEngineExportSceneFile)
    bpy.utils.unregister_class(avEngineViewSceneInEngine)
    bpy.utils.unregister_class(avEngineCreateSubstancePainterProject)

    bpy.types.VIEW3D_HT_header.remove(addmenu_callback)
    bpy.utils.unregister_class(VIEW3D_MT_menu)

    bpy.types.VIEW3D_PT_tools_active.remove(add_preview_button)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
