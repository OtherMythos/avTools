import os

# Substance 3D Painter modules
import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset

from pathlib import Path
import json
import subprocess

# PySide module to build custom UI
from PySide2 import QtWidgets


plugin_widgets = []


def getExpectedMaterialFilePath():
    rootPath = Path(substance_painter.project.file_path()).parent
    projectName = Path(substance_painter.project.file_path()).stem
    jsonPath = rootPath / (projectName + ".material.json")
    return jsonPath

def openEngineWithArgs(setupArgs):
    enginePath = "/Users/edward/Documents/avEngine/build/Debug/av.app/Contents/MacOS/av"
    args = [enginePath]
    args.extend(setupArgs)

    devnull = open(os.devnull, 'w')
    process = subprocess.Popen(args, stdout=devnull, stderr=devnull)
    devnull.close()


def createAvSetupFile(basePath, targetMesh, targetMaterialFile):
    targetPath = basePath / Path("avSetupAddition.cfg")
    data = {
        'OgreResources':{
            'General': [
                ['FileSystem', str(basePath)]
            ]
        },
        'UserSettings':{
            'StartMesh': str(targetMesh) + ".mesh",
            'StartFile': str(targetMaterialFile)
        }
    }

    json_string = json.dumps(data)

    with open(str(targetPath), 'w') as outfile:
        outfile.write(json_string)

    return targetPath

def exportTextures() :
    # Verify if a project is open before trying to export something
    if not substance_painter.project.is_open() :
        return

    # Setup the export path, in this case the textures
    # will be put next to the spp project file on the disk
    targetPath = substance_painter.project.file_path()
    print(targetPath)
    if(targetPath is None):
        return
    targetPath = os.path.dirname(targetPath) + "/"

    # Get the currently active layer stack (paintable)
    stack = substance_painter.textureset.get_active_stack()

    # Get the parent Texture Set of this layer stack
    material = stack.material()

    # Build Export Preset resource URL
    # - Context: name of the library where the resource is located
    # - Name: name of the resource (filename without extension or Substance graph path)
    export_preset = substance_painter.resource.ResourceID(
                        context="your_assets",
                        name="Ogre" )

    print( "Preset:" )
    print( export_preset.url() )

    # Setup the export settings
    resolution = material.get_resolution()

    # Build the configuration
    config = {
        "exportShaderParams"     : False,
        "exportPath"             : targetPath,
        "exportList"            : [ { "rootPath" : str(stack) } ],
        "exportPresets"         : [ { "name" : "default", "maps" : [] } ],
        "defaultExportPreset"     : export_preset.url(),
        "exportParameters"         : [
            {
                "parameters"    : { "paddingAlgorithm": "infinite" }
            }
        ]
    }

    substance_painter.export.export_project_textures( config )



    #write the json data.
    jsonPath = getExpectedMaterialFilePath()

    projectName = Path(substance_painter.project.file_path()).stem

    data = {
        "pbs": {
            projectName: {
                "workflow": "metallic",
                "normal": {
                    "texture": str(projectName) + "_" + str(stack) + "_Normal.png"
                },
                "diffuse": {
                    "texture": str(projectName) + "_" + str(stack) + "_AlbedoTransparency.png"
                },
                "metallness": {
                    "texture": str(projectName) + "_" + str(stack) + "_Metalic.png"
                },
                "specular": {
                    "texture": str(projectName) + "_" + str(stack) + "_Metalic.png"
                },
                "roughness": {
                    "texture": str(projectName) + "_" + str(stack) + "_Roughness.png"
                }
            }
        }
    }

    json_string = json.dumps(data)

    print("exporting to " + str(jsonPath))
    with open(str(jsonPath), 'w') as outfile:
        outfile.write(json_string)

def viewInEngine():
    if substance_painter.project.file_path() is None:
        return

    #Export the latest textures so the engine reflects what's on screen.
    exportTextures()

    projectDir = Path(substance_painter.project.file_path()).parent
    projectName = Path(substance_painter.project.file_path()).stem
    materialName = getExpectedMaterialFilePath()

    setupFilePath = createAvSetupFile(projectDir, projectName, materialName)
    openEngineWithArgs(["/Users/edward/Documents/materialEditor/avSetup.cfg", str(setupFilePath)])

def start_plugin():
    # Create a text widget for a menu
    Action = QtWidgets.QAction("avEngine export", triggered=exportTextures)
    ActionViewInEngine = QtWidgets.QAction("View in avEngine", triggered=viewInEngine)

    # Add this widget to the existing File menu of the application
    substance_painter.ui.add_action(
        substance_painter.ui.ApplicationMenu.File,
        Action )
    substance_painter.ui.add_action(
        substance_painter.ui.ApplicationMenu.File,
        ActionViewInEngine)

    # Store the widget for proper cleanup later when stopping the plugin
    plugin_widgets.append(Action)
    plugin_widgets.append(ActionViewInEngine)


def close_plugin():
    # Remove all widgets that have been added to the UI
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)

    plugin_widgets.clear()


if __name__ == "__main__":
    start_plugin()
