import bpy
from bpy.types import Panel, Context, Menu, Property, UIList, UILayout, AnyType
from refmatcher import operators, properties, dependencies, matching_variables

class REFMATCHER_UL_MatchingProperties(UIList):
    bl_idname = "REFMATCHER_UL_MatchingProperties"

    def draw_item(self, context: Context, layout: UILayout, data: AnyType, item: properties.MatchingProperty, icon: int, active_data: AnyType, active_property: str):
        layout.separator()
        readonly = layout.row()
        readonly.enabled = False
        readonly.scale_x = 4/5
        readonly.prop(item, "datablock", text="")
        readonly.prop(item, "data_path", text="")
        layout.prop(item, "minimum", text="Min")
        layout.prop(item, "maximum", text="Max")

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

        interactive_layout.template_list(REFMATCHER_UL_MatchingProperties.bl_idname, "", context.scene, properties.MATCHING_PROPERTIES_PROPNAME, context.scene, properties.MATCHING_PROPERTIES_INDEX_PROPNAME)
        interactive_layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariableFromList.bl_idname, icon='REMOVE', text="")
        interactive_layout.separator()

        interactive_layout.operator(operators.REFMATCHER_OT_MatchReference.bl_idname)

def draw_variable_menu(self: Menu, context: Context):
    if context.property is None:
        return

    property: Property = matching_variables.get_hovered_property(context)
    if not matching_variables.is_optimizable_property(property):
        return

    layout = self.layout
    datablock, data_path, array_index = context.property
    layout.separator()
    if matching_variables.is_matching_variable(context, datablock, data_path, array_index):
        if array_index < 0:
            # single property
            layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariable.bl_idname)
        else:
            # vector property
            layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariable.bl_idname, text="Remove single matching variable")
            layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariableVector.bl_idname)
    else:
        if array_index < 0:
            # single property
            layout.operator(operators.REFMATCHER_OT_AddMatchingVariableFloat.bl_idname)
        else:
            # vector property
            layout.operator(operators.REFMATCHER_OT_AddMatchingVariableFloat.bl_idname, text="Add single matching variable")
            layout.operator(operators.REFMATCHER_OT_AddMatchingVariableVector.bl_idname)

def register():
    bpy.utils.register_class(REFMATCHER_UL_MatchingProperties)
    bpy.utils.register_class(REFMATCHER_PT_MainPanel)
    bpy.types.UI_MT_button_context_menu.append(draw_variable_menu)

def unregister():
    bpy.types.UI_MT_button_context_menu.remove(draw_variable_menu)
    bpy.utils.unregister_class(REFMATCHER_PT_MainPanel)
    bpy.utils.unregister_class(REFMATCHER_UL_MatchingProperties)