from bpy.types import Scene, Image
from bpy.props import PointerProperty, IntProperty, EnumProperty

CHANNEL_PROPNAME = "refmatcher_channel"
DISTANCE_PROPNAME = "refmatcher_distance"
ITERATIONS_PROPNAME = "refmatcher_iterations"
REFERENCE_IMAGE_PROPNAME = "refmatcher_reference_image"

SCENE_ATTRIBUTES = {
    CHANNEL_PROPNAME: EnumProperty(name="Channel", description="Color channel to be used for comparison", default="LUMINANCE",
                                   items=[
                                        ('LUMINANCE', "Luminance", "Luminance channel"),
                                        ('RED', "Red", "Red channel"),
                                        ('GREEN', "Green", "Green channel"),
                                        ('BLUE', "Blue", "Blue channel"),
                                        ('RGB', "RGB", "RGB channels"),
                                      ]),
    DISTANCE_PROPNAME: EnumProperty(name="Distance", description="Distance metric to be used for comparison", default="BHATTACHARYYA",
                                    items=[
                                        ('BHATTACHARYYA', "Bhattacharyya", "Bhattacharyya distance"),
                                        ('EARTH_MOVERS', "Earth Movers", "Earth Movers distance"),
                                    ]),
    ITERATIONS_PROPNAME: IntProperty(name="Iterations", description="Maximum number of iterations", default=10, min=1),
    REFERENCE_IMAGE_PROPNAME: PointerProperty(name="Reference", description="Reference image", type=Image),
}

def register():
    for propname, prop in SCENE_ATTRIBUTES.items():
        setattr(Scene, propname, prop)

def unregister():
    for propname in SCENE_ATTRIBUTES:
        delattr(Scene, propname)