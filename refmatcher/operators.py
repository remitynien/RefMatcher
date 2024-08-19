import bpy
from bpy.types import Operator, Context, Image, Event
from bpy.props import FloatProperty
from refmatcher import dependencies, optimization, matching_variables
from refmatcher.properties import REFERENCE_IMAGE_PROPNAME, CHANNEL_PROPNAME, DISTANCE_PROPNAME, OPTIMIZER_PROPNAME, \
    ITERATIONS_PROPNAME, MATCHING_PROPERTIES_PROPNAME, MATCHING_PROPERTIES_INDEX_PROPNAME, INCLUDE_ALPHA_PROPNAME, \
    get_scene_vector_propname, get_scene_propname

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
    bl_options = {'REGISTER'} # TODO: should be undoable ?

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
        optimizer: optimization.Optimizer = optimizer_class(channel, distance, reference_image, iterations, context)
        result = optimizer.optimize()
        matching_variables.set_matching_values(context, result)
        return {'FINISHED'}

class REFMATCHER_OT_AddMatchingVariableFloat(Operator):
    bl_idname = "refmatcher.add_matching_variable_float"
    bl_category = 'View'
    bl_label = "Add matching variable"
    bl_description = "Add the property to the list of matching variables"
    bl_options = {'REGISTER', 'UNDO'}

    minimum: FloatProperty(name="Minimum value", default=0.0) # type: ignore
    maximum: FloatProperty(name="Maximum value", default=1.0) # type: ignore

    def __init__(self) -> None:
        super().__init__()
        self.datablock = None
        self.data_path_indexed = ""
        self.min_propname = ""
        self.max_propname = ""

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(context.scene, self.min_propname)
        layout.prop(context.scene, self.max_propname)

    def execute(self, context: Context):
        if not self.datablock or not self.data_path_indexed:
            return {'CANCELLED', 'PASS_THROUGH'}
        min = getattr(context.scene, self.min_propname)
        max = getattr(context.scene, self.max_propname)
        matching_variables.add_matching_variable(context, self.datablock, self.data_path_indexed, min, max)
        return {'FINISHED'}

    def invoke(self, context: Context, event: Event):
        data = matching_variables.get_hovered_data(context)
        property = matching_variables.get_hovered_property(context)
        if data is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        self.datablock, self.data_path_indexed, array_index = data
        if property is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        is_array = matching_variables.is_array(property, array_index)
        if is_array:
            self.data_path_indexed += f"[{min(array_index, 0)}]" # covers edge case where array_index = -1 but is_array is True
        prop = matching_variables.get_hovered_property(context)
        value_type = prop.type
        subtype = prop.subtype
        unit = prop.unit
        self.min_propname = get_scene_propname(context.scene, value_type, subtype, unit, "Min")
        self.max_propname = get_scene_propname(context.scene, value_type, subtype, unit, "Max")
        setattr(context.scene, self.min_propname, prop.soft_min)
        setattr(context.scene, self.max_propname, prop.soft_max)
        return context.window_manager.invoke_props_dialog(self)

class REFMATCHER_OT_AddMatchingVariableVector(Operator):
    bl_idname = "refmatcher.add_matching_variable_vector"
    bl_category = 'View'
    bl_label = "Add all matching variables"
    bl_description = "Add the properties to the list of matching variables"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self) -> None:
        super().__init__()
        self.datablock = None
        self.data_path = ""
        self.vector_size = -1
        self.min_propname = ""
        self.max_propname = ""
        self.subtype = ""

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(context.scene, self.min_propname)
        layout.prop(context.scene, self.max_propname)
        if self.subtype == 'COLOR':
            layout.prop(context.scene, INCLUDE_ALPHA_PROPNAME)

    def execute(self, context: Context):
        if not self.datablock or not self.data_path or self.vector_size < 0:
            return {'CANCELLED', 'PASS_THROUGH'}
        min = getattr(context.scene, self.min_propname)
        max = getattr(context.scene, self.max_propname)
        size = self.vector_size -1 if self.subtype == 'COLOR' and getattr(context.scene, INCLUDE_ALPHA_PROPNAME) is False else self.vector_size
        for i in range(size):
            data_path_indexed = f"{self.data_path}[{i}]"
            matching_variables.add_matching_variable(context, self.datablock, data_path_indexed, min[i], max[i])
        return {'FINISHED'}

    def invoke(self, context: Context, event: Event):
        data = matching_variables.get_hovered_data(context)
        if data is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        self.datablock, self.data_path, _ = data
        prop = matching_variables.get_hovered_property(context)
        if not prop.is_array:
            return {'CANCELLED', 'PASS_THROUGH'}
        self.vector_size = prop.array_length
        vector_type = prop.type
        self.subtype = prop.subtype
        unit = prop.unit
        self.min_propname = get_scene_vector_propname(context.scene, vector_type, self.vector_size, self.subtype, unit, "Min")
        self.max_propname = get_scene_vector_propname(context.scene, vector_type, self.vector_size, self.subtype, unit, "Max")
        setattr(context.scene, self.min_propname, [prop.soft_min] * self.vector_size)
        setattr(context.scene, self.max_propname, [prop.soft_max] * self.vector_size)
        return context.window_manager.invoke_props_dialog(self)

class REFMATCHER_OT_RemoveMatchingVariable(Operator):
    bl_idname = "refmatcher.remove_matching_variable"
    bl_category = 'View'
    bl_label = "Remove matching variable"
    bl_description = "Remove the property from the list of matching variables"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context):
        data = matching_variables.get_hovered_data(context)
        if data is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        datablock, data_path_indexed, array_index = data
        if array_index >= 0:
            data_path_indexed += f"[{array_index}]"
        matching_variables.remove_matching_variable(context, datablock, data_path_indexed)
        return {'FINISHED'}

class REFMATCHER_OT_RemoveMatchingVariableVector(Operator):
    bl_idname = "refmatcher.remove_matching_variable_vector"
    bl_category = 'View'
    bl_label = "Remove all matching variables"
    bl_description = "Removes the properties from the list of matching variables"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context):
        data = matching_variables.get_hovered_data(context)
        if data is None:
            return {'CANCELLED', 'PASS_THROUGH'}
        datablock, data_path, _ = data
        prop = matching_variables.get_hovered_property(context)
        if not prop.is_array:
            return {'CANCELLED', 'PASS_THROUGH'}
        matching_variables.remove_matching_variables(context, datablock, [f"{data_path}[{i}]" for i in range(prop.array_length)])
        return {'FINISHED'}

class REFMATCHER_OT_RemoveMatchingVariableFromList(Operator):
    bl_idname = "refmatcher.remove_matching_variable_from_list"
    bl_category = 'View'
    bl_label = "Remove matching variable"
    bl_description = "Remove the selected property from the list of matching variables"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return 0 <= getattr(context.scene, MATCHING_PROPERTIES_INDEX_PROPNAME) < len(getattr(context.scene, MATCHING_PROPERTIES_PROPNAME))

    def execute(self, context: Context):
        index = getattr(context.scene, MATCHING_PROPERTIES_INDEX_PROPNAME)
        matching_properties = getattr(context.scene, MATCHING_PROPERTIES_PROPNAME)
        matching_properties.remove(index)
        if index >= len(matching_properties):
            setattr(context.scene, MATCHING_PROPERTIES_INDEX_PROPNAME, index - 1)
        return {'FINISHED'}

OPERATORS = [
    REFMATCHER_OT_InstallDependencies,
    REFMATCHER_OT_MatchReference,
    REFMATCHER_OT_AddMatchingVariableFloat,
    REFMATCHER_OT_AddMatchingVariableVector,
    REFMATCHER_OT_RemoveMatchingVariable,
    REFMATCHER_OT_RemoveMatchingVariableVector,
    REFMATCHER_OT_RemoveMatchingVariableFromList,
]

def register():
    for operator in OPERATORS:
        bpy.utils.register_class(operator)

def unregister():
    for operator in OPERATORS:
        bpy.utils.unregister_class(operator)
