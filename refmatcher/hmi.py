import bpy
from bpy.types import Panel, Context
from refmatcher import operators, properties

class REFMATCHER_PT_MainPanel(Panel):
    bl_idname = "REFMATCHER_PT_MainPanel"
    bl_label = "Ref Matcher"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_options = set()

    def draw(self, context: Context):
        layout = self.layout
        layout.label(text="Parameters")
        layout.prop(context.scene, properties.ITERATIONS_PROPNAME)
        layout.prop(context.scene, properties.CHANNEL_PROPNAME)
        layout.prop(context.scene, properties.DISTANCE_PROPNAME)
        layout.separator()

        layout.label(text="Reference")
        layout.template_ID(context.scene, properties.REFERENCE_IMAGE_PROPNAME,
                           new="image.new", open="image.open")
        layout.separator()

        layout.operator(operators.REFMATCHER_OT_MatchReference.bl_idname)

def register():
    bpy.utils.register_class(REFMATCHER_PT_MainPanel)

def unregister():
    bpy.utils.unregister_class(REFMATCHER_PT_MainPanel)