from bpy.types import Scene, Image
from bpy.props import PointerProperty, IntProperty

REFERENCE_IMAGE_PROPNAME = "refmatcher_reference_image"
ITERATIONS_PROPNAME = "refmatcher_iterations"

SCENE_ATTRIBUTES = {
    REFERENCE_IMAGE_PROPNAME: PointerProperty(name="Reference", description="Reference image", type=Image),
    ITERATIONS_PROPNAME: IntProperty(name="Iterations", description="Maximum number of iterations", default=10, min=1)
}

def register():
    for propname, prop in SCENE_ATTRIBUTES.items():
        setattr(Scene, propname, prop)

def unregister():
    for propname in SCENE_ATTRIBUTES:
        delattr(Scene, propname)