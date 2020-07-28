import bpy
import sys

'''
This script is intended to be run by blender in background mode.
Make sure you have blender2ogre installed as a blender extension, and it is properly enabled and everything.

Read through all visible objects in the scene and export them as a mesh.
'''
def main():
    from io_ogre.ogre.mesh import dot_mesh

    try:
        idx = sys.argv.index('--')
    except:
        print("Include the output path.")
        print("i.e 'blender -b file.blend --python ~/Documents/avTools/exportTest.py -- /tmp/outPath'")
        return

    if idx+1 >= len(sys.argv):
        print("Include the output path.")
        print("i.e 'blender -b file.blend --python ~/Documents/avTools/exportTest.py -- /tmp/outPath'")
        return

    outPath = sys.argv[idx+1]
    print(outPath)

    #for ob in bpy.context.scene.objects:
    for ob in bpy.context.visible_objects:
        if ob.type != 'MESH':
            continue

        dot_mesh(ob, outPath)

if __name__ == "__main__":
    main()
