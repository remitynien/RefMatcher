import bpy
import os
import zipfile

# command line usage: blender -P install.py

def package(directory_path):
    with zipfile.ZipFile("refmatcher.zip", 'w', zipfile.ZIP_STORED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path)

package("refmatcher")
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refmatcher.zip")
bpy.ops.preferences.addon_install(overwrite=True, filepath=path)
bpy.ops.preferences.addon_enable(module="refmatcher")