import os

# Substance 3D Painter modules
import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset

from pathlib import Path
import json

# PySide module to build custom UI
from PySide2 import QtWidgets


plugin_widgets = []


def export_textures() :
    # Verify if a project is open before trying to export something
    if not substance_painter.project.is_open() :
        return

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

    # Setup the export path, in this case the textures
    # will be put next to the spp project file on the disk
    targetPath = substance_painter.project.file_path()
    targetPath = os.path.dirname(targetPath) + "/"

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
    jsonPath = Path(targetPath) / "project.material.json"

    projectName = Path(substance_painter.project.file_path()).stem
    print(projectName + ".material.json")

    data = {
        "pbs": {
            projectName: {
                "workflow": "metallic",
                "normal": {
                    "texture": "targetMesh_None_Normal.png"
                },
                "diffuse": {
                    "texture": "targetMesh_None_AlbedoTransparency.png"
                },
                "metallness": {
                    "texture": "targetMesh_None_Metalic.png"
                },
                "specular": {
                    "texture": "targetMesh_None_Metalic.png"
                },
                "roughness": {
                    "texture": "targetMesh_None_Roughness.png"
                }
            }
        }
    }

    json_string = json.dumps(data)

    print("exporting to " + str(jsonPath))
    with open(str(jsonPath), 'w') as outfile:
        outfile.write(json_string)



def start_plugin():
    # Create a text widget for a menu
    Action = QtWidgets.QAction("avEngine export", triggered=export_textures)

    # Add this widget to the existing File menu of the application
    substance_painter.ui.add_action(
        substance_painter.ui.ApplicationMenu.File,
        Action )

    # Store the widget for proper cleanup later when stopping the plugin
    plugin_widgets.append(Action)


def close_plugin():
    # Remove all widgets that have been added to the UI
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)

    plugin_widgets.clear()


if __name__ == "__main__":
    start_plugin()
