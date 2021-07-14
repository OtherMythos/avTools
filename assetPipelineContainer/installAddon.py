#!/usr/bin/python3

#A script to setup the blender2ogre extension inside the container.

import bpy
bpy.ops.preferences.addon_enable(module="io_ogre")
bpy.ops.wm.save_userpref()
