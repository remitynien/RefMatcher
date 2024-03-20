import bpy
from bpy.types import Operator, Context

class REFMATCHER_OT_ExampleOperator(Operator):
    bl_idname = "refmatcher.example_operator"
    bl_category = 'View'
    bl_label = "Example operator"
    bl_description = 'This is an example operator.'
    bl_options = {'REGISTER'}

    def execute(self, context: Context):
        print("This is an example.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(REFMATCHER_OT_ExampleOperator)

def unregister():
    bpy.utils.unregister_class(REFMATCHER_OT_ExampleOperator)