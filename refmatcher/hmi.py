import bpy
from bpy.types import Panel, Context
from refmatcher import operators, properties, dependencies

class REFMATCHER_PT_MainPanel(Panel):
    bl_idname = "REFMATCHER_PT_MainPanel"
    bl_label = "Ref Matcher"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_options = set()

    def draw(self, context: Context):
        layout = self.layout
        dependencies_ok = dependencies.check_dependencies()

        if not dependencies_ok:
            dependencies_layout = layout.box()
            dependencies_layout.label(text=f"Missing dependencies: {list(dependencies.get_missing_dependencies())}", icon='ERROR')
            dependencies_layout.operator(operators.REFMATCHER_OT_InstallDependencies.bl_idname)

        interactive_layout = layout.column(align=True)
        interactive_layout.enabled = dependencies_ok
        interactive_layout.label(text="Parameters")
        interactive_layout.prop(context.scene, properties.ITERATIONS_PROPNAME)
        interactive_layout.prop(context.scene, properties.CHANNEL_PROPNAME)
        interactive_layout.prop(context.scene, properties.DISTANCE_PROPNAME)
        interactive_layout.prop(context.scene, properties.OPTIMIZER_PROPNAME)
        interactive_layout.separator()

        interactive_layout.label(text="Reference")
        interactive_layout.template_ID(context.scene, properties.REFERENCE_IMAGE_PROPNAME,
                        new="image.new", open="image.open")
        interactive_layout.separator()

        interactive_layout.operator(operators.REFMATCHER_OT_MatchReference.bl_idname)

def register():
    bpy.utils.register_class(REFMATCHER_PT_MainPanel)

def unregister():
    bpy.utils.unregister_class(REFMATCHER_PT_MainPanel)