import bpy
from bpy.types import Operator, Context, Image
from bpy.props import IntProperty, PointerProperty

class REFMATCHER_OT_MatchReference(Operator):
    bl_idname = "refmatcher.match_reference"
    bl_category = 'View'
    bl_label = "Match reference"
    bl_description = 'Matches the reference by adjusting given parameters'
    bl_options = {'REGISTER'}

    def execute(self, context: Context):
        bpy.ops.render.render(write_still=True)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(REFMATCHER_OT_MatchReference)

def unregister():
    bpy.utils.unregister_class(REFMATCHER_OT_MatchReference)