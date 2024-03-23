import bpy
from bpy.types import Operator, Context, Image
from refmatcher import image_comparison
from refmatcher.properties import REFERENCE_IMAGE_PROPNAME, CHANNEL_PROPNAME, DISTANCE_PROPNAME

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

def register():
    bpy.utils.register_class(REFMATCHER_OT_MatchReference)

def unregister():
    bpy.utils.unregister_class(REFMATCHER_OT_MatchReference)