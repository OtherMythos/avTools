bl_info = {
    "name": "Random addon for me",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import subprocess
import os

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

    def viewingInEngine(self):
        print("Viewing single object in engine.")

        devnull = open(os.devnull, 'w')
        pathToEngineExecutable = av_plugin_config["engine_path"]
        pathToMaterialEditor = av_plugin_config["material_editor_av_setup"]
        process = subprocess.Popen([pathToEngineExecutable, pathToMaterialEditor], stdout=devnull, stderr=devnull)
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
