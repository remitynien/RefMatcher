import bpy
from bpy.types import Scene, Image, PropertyGroup, ID
from bpy.props import PointerProperty, IntProperty, EnumProperty, FloatProperty, CollectionProperty, \
                      StringProperty, FloatVectorProperty, IntVectorProperty, BoolProperty

class MatchingProperty(PropertyGroup):
    datablock: PointerProperty(name="Datablock", type=ID) # type: ignore
    data_path_indexed: StringProperty(name="Data Path") # type: ignore
    minimum: FloatProperty(name="Minimum") # type: ignore
    maximum: FloatProperty(name="Maximum") # type: ignore

CHANNEL_PROPNAME = "refmatcher_channel"
DISTANCE_PROPNAME = "refmatcher_distance"
ITERATIONS_PROPNAME = "refmatcher_iterations"
MATCHING_PROPERTIES_PROPNAME = "refmatcher_matching_properties"
MATCHING_PROPERTIES_INDEX_PROPNAME = "refmatcher_matching_properties_index"
OPTIMIZER_PROPNAME = "refmatcher_optimizer"
REFERENCE_IMAGE_PROPNAME = "refmatcher_reference_image"
INCLUDE_ALPHA_PROPNAME = "refmatcher_use_alpha"

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
    ITERATIONS_PROPNAME: IntProperty(name="Iterations", description="Target number of evaluations", default=10, min=1),
    MATCHING_PROPERTIES_PROPNAME: CollectionProperty(type=MatchingProperty, name="Variables", description="Variables to be optimized for matching"),
    MATCHING_PROPERTIES_INDEX_PROPNAME: IntProperty(name="Index", description="Index of the selected variable", default=-1),
    OPTIMIZER_PROPNAME: EnumProperty(name="Optimizer", description="Optimizer to be used for matching", default="DUAL_ANNEALING",
                                    items=[
                                        ('DUAL_ANNEALING', "Dual Annealing", "?"),
                                        ('DIFFERENTIAL_EVOLUTION', "Differential Evolution", "Good for large numbers of parameters ?"),
                                    ]),
    REFERENCE_IMAGE_PROPNAME: PointerProperty(name="Reference", description="Reference image", type=Image),
    INCLUDE_ALPHA_PROPNAME: BoolProperty(name="Include alpha", description="Include alpha channel", default=False),
}

scene_vector_properties = set()
def get_scene_vector_propname(scene: Scene, type: str, size: int, subtype: str, unit: str, name: str) -> str:
    assert type in {'FLOAT', 'INT'}, f"Invalid type: {type}"
    propname = f"refmatcher_{type.lower()}_vector_{size}_{subtype.lower()}_{unit.lower()}_{name.lower()}"
    if not hasattr(scene, propname):
        if type == 'FLOAT':
            prop = FloatVectorProperty(name=name, size=size, subtype=subtype, unit=unit)
        elif type == 'INT':
            prop = IntVectorProperty(name=name, size=size, subtype=subtype, unit=unit)
        setattr(Scene, propname, prop)
        scene_vector_properties.add(propname)
    return propname

def register():
    bpy.utils.register_class(MatchingProperty)
    for propname, prop in SCENE_ATTRIBUTES.items():
        setattr(Scene, propname, prop)

def unregister():
    for propname in SCENE_ATTRIBUTES:
        delattr(Scene, propname)
    for propname in scene_vector_properties:
        delattr(Scene, propname)
    scene_vector_properties.clear()
    bpy.utils.unregister_class(MatchingProperty)