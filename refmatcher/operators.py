import bpy
from bpy.types import Operator, Context, Image, Event
from bpy.props import FloatProperty
from refmatcher import dependencies, optimization, matching_variables
from refmatcher.properties import REFERENCE_IMAGE_PROPNAME, CHANNEL_PROPNAME, DISTANCE_PROPNAME, OPTIMIZER_PROPNAME, ITERATIONS_PROPNAME

class REFMATCHER_OT_InstallDependencies(Operator):
    bl_idname = "refmatcher.install_dependencies"
    bl_category = 'View'
    bl_label = "Install dependencies"
    bl_description = "Installs the required dependencies for the Ref Matcher addon"
    bl_options = {'REGISTER'}

    def execute(self, context: Context):
        success = dependencies.install_dependencies()
        if success:
            self.report({'INFO'}, f"Successfully installed dependencies: {list(dependencies.DEPENDENCIES.keys())}")
        else:
            self.report({'WARNING'}, "Unexpected error occurred while installing dependencies. Please check the console for more information.")
        return {'FINISHED'}

class REFMATCHER_OT_MatchReference(Operator):
    bl_idname = "refmatcher.match_reference"
    bl_category = 'View'
    bl_label = "Match reference"
    bl_description = "Matches the reference by adjusting given parameters"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return getattr(context.scene, REFERENCE_IMAGE_PROPNAME) is not None

    def execute(self, context: Context):
        reference_image: Image = getattr(context.scene, REFERENCE_IMAGE_PROPNAME)
        channel: str = getattr(context.scene, CHANNEL_PROPNAME)
        distance: str = getattr(context.scene, DISTANCE_PROPNAME)
        iterations: int = getattr(context.scene, ITERATIONS_PROPNAME)
        optimizer_name = getattr(context.scene, OPTIMIZER_PROPNAME)
        optimizer_class = optimization.OPTIMIZER_BY_NAME[optimizer_name]
        optimizer: optimization.Optimizer = optimizer_class(channel, distance, reference_image, iterations)
        optimizer.optimize()
        return {'FINISHED'}

class REFMATCHER_OT_AddMatchingVariable(Operator):
    bl_idname = "refmatcher.add_matching_variable"
    bl_category = 'View'
    bl_label = "Add matching variable"
    bl_description = "Adds the property to the list of matching variables"
    bl_options = {'REGISTER'}

    minimum: FloatProperty(name="Minimum value", default=0.0) # type: ignore
    maximum: FloatProperty(name="Maximum value", default=1.0) # type: ignore

    def execute(self, context: Context):
        try:
            matching_variables.add_matching_variable(context, self.datablock, self.data_path, self.minimum, self.maximum)
        except Exception as e:
            return {'CANCELLED', 'PASS_THROUGH'}
        return {'FINISHED'}

    def invoke(self, context: Context, event: Event):
        if context.property is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        self.datablock, self.data_path, self.array_index = context.property
        return context.window_manager.invoke_props_dialog(self)

class REFMATCHER_OT_RemoveMatchingVariable(Operator):
    bl_idname = "refmatcher.remove_matching_variable"
    bl_category = 'View'
    bl_label = "Remove matching variable"
    bl_description = "Removes the property from the list of matching variables"
    bl_options = {'REGISTER'}

    def execute(self, context: Context):
        if context.property is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        datablock, data_path, array_index = context.property
        matching_variables.remove_matching_variable(context, datablock, data_path)
        return {'FINISHED'}

OPERATORS = [
    REFMATCHER_OT_InstallDependencies,
    REFMATCHER_OT_MatchReference,
    REFMATCHER_OT_AddMatchingVariable,
    REFMATCHER_OT_RemoveMatchingVariable,
]

def register():
    for operator in OPERATORS:
        bpy.utils.register_class(operator)

def unregister():
    for operator in OPERATORS:
        bpy.utils.unregister_class(operator)
