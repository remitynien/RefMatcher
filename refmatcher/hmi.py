import bpy
from bpy.types import Panel, Context
from refmatcher import operators

class REFMATCHER_PT_MainPanel(Panel):
    bl_idname = "REFMATCHER_PT_MainPanel"
    bl_label = "Ref Matcher"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_options = set()

    def draw(self, context: Context):
        layout = self.layout
        layout.label(text="Example label")
        layout.operator(operators.REFMATCHER_OT_ExampleOperator.bl_idname)

def register():
    bpy.utils.register_class(REFMATCHER_PT_MainPanel)

def unregister():
    bpy.utils.unregister_class(REFMATCHER_PT_MainPanel)