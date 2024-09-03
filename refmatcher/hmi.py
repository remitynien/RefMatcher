import bpy
from bpy.types import Panel, Context, Menu, Property, UIList, UILayout, AnyType
from refmatcher import operators, properties, dependencies, matching_variables

# TODO: fix add/remove display

class REFMATCHER_UL_MatchingProperties(UIList):
    bl_idname = "REFMATCHER_UL_MatchingProperties"

    def draw_item(self, context: Context, layout: UILayout, data: AnyType, item: properties.MatchingProperty, icon: int, active_data: AnyType, active_property: str):
        layout.separator()
        readonly = layout.row()
        readonly.enabled = False
        readonly.scale_x = 4/5
        readonly.prop(item, "datablock", text="")
        readonly.prop(item, "data_path_indexed", text="")
        layout.prop(item, "minimum", text="Min")
        layout.prop(item, "maximum", text="Max")

class REFMATCHER_PT_MainPanel(Panel):
    bl_idname = "REFMATCHER_PT_MainPanel"
    bl_label = "Ref Matcher"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 101 # After color management panel (100)

    def draw(self, context: Context):
        layout = self.layout
        dependencies_ok = dependencies.check_dependencies()
        versions_ok = dependencies.check_versions()

        if not dependencies_ok:
            dependencies_layout = layout.box()
            dependencies_layout.label(text=f"Missing dependencies: {list(dependencies.get_missing_dependencies())}", icon='ERROR')
            dependencies_layout.operator(operators.REFMATCHER_OT_InstallDependencies.bl_idname)

        if dependencies_ok and not versions_ok:
            versions_layout = layout.box()
            versions_layout.label(text="Unexpected dependencies version.", icon='INFO')
            versions_layout.label(text="This may result in unexpected behaviours or crashes.")
            for package_name, (installed_version, required_version) in dependencies.get_unmatched_versions().items():
                versions_layout.label(text=f"{package_name}: installed {installed_version}, required {required_version}")
            versions_layout.operator(operators.REFMATCHER_OT_InstallDependencies.bl_idname)

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
    if not matching_variables.check_context(context):
        return

    data = matching_variables.get_hovered_data(context)
    if data is None:
        return

    property: Property | None = matching_variables.get_hovered_property(context)
    if property is None or not matching_variables.is_optimizable_property(property):
        return

    datablock, data_path, array_index = data
    is_array = matching_variables.is_array(property, array_index)

    layout = self.layout
    layout.separator()
    if matching_variables.is_matching_variable(context, datablock, data_path, array_index):
        if is_array:
            # vector property
            layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariable.bl_idname, text="Remove single matching variable")
            layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariableVector.bl_idname)
        else:
            # single property
            layout.operator(operators.REFMATCHER_OT_RemoveMatchingVariable.bl_idname)
    else:
        if is_array:
            # vector property
            if array_index >= 0:
                layout.operator(operators.REFMATCHER_OT_AddMatchingVariableFloat.bl_idname, text="Add single matching variable")
            layout.operator(operators.REFMATCHER_OT_AddMatchingVariableVector.bl_idname)
        else:
            # single property
            layout.operator(operators.REFMATCHER_OT_AddMatchingVariableFloat.bl_idname)

def register():
    bpy.utils.register_class(REFMATCHER_UL_MatchingProperties)
    bpy.utils.register_class(REFMATCHER_PT_MainPanel)
    bpy.types.UI_MT_button_context_menu.append(draw_variable_menu)

def unregister():
    bpy.types.UI_MT_button_context_menu.remove(draw_variable_menu)
    bpy.utils.unregister_class(REFMATCHER_PT_MainPanel)
    bpy.utils.unregister_class(REFMATCHER_UL_MatchingProperties)