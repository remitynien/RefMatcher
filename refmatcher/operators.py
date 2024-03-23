import bpy
from bpy.types import Operator, Context, Image
from refmatcher import image_comparison, dependencies
from refmatcher.properties import REFERENCE_IMAGE_PROPNAME, CHANNEL_PROPNAME, DISTANCE_PROPNAME

class REFMATCHER_OT_InstallDependencies(Operator):
    bl_idname = "refmatcher.install_dependencies"
    bl_category = 'View'
    bl_label = "Install dependencies"
    bl_description = 'Installs the required dependencies for the Ref Matcher addon'
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
    bl_description = 'Matches the reference by adjusting given parameters'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return getattr(context.scene, REFERENCE_IMAGE_PROPNAME) is not None

    def execute(self, context: Context):
        bpy.ops.render.render(write_still=True)
        rendered_image = image_comparison.rendered_image()
        reference_image = getattr(context.scene, REFERENCE_IMAGE_PROPNAME)
        channel = getattr(context.scene, CHANNEL_PROPNAME)
        distance = getattr(context.scene, DISTANCE_PROPNAME)
        result = image_comparison.compare_images(reference_image, rendered_image, channel, distance)
        self.report({'INFO'}, f"Comparison result: {result}")
        return {'FINISHED'}

OPERATORS = [
    REFMATCHER_OT_InstallDependencies,
    REFMATCHER_OT_MatchReference
]

def register():
    for operator in OPERATORS:
        bpy.utils.register_class(operator)

def unregister():
    for operator in OPERATORS:
        bpy.utils.unregister_class(operator)
