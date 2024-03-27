import bpy
from bpy.types import Context, Property, ID
from refmatcher.properties import MatchingProperty, MATCHING_PROPERTIES_PROPNAME
from typing import Iterable

def is_optimizable_property(property: Property) -> bool:
    # return property.type in {"FLOAT", "INT"}
    return property.type == "FLOAT" and property.is_array is False # TODO: accept more types

def get_hovered_property(context: Context) -> Property | None:
    if context.property is None:
        return
    datablock: ID
    data_path: str
    array_index: int
    datablock, data_path, array_index = context.property
    return datablock.path_resolve(data_path, False).data.bl_rna.properties[data_path.split(".")[-1]] # couldn't find a better way to get the property :/

def get_hovered_value(context: Context) -> float | None:
    if context.property is None:
        return
    datablock: bpy.types.ID
    data_path: str
    array_index: int
    datablock, data_path, array_index = context.property
    return datablock.path_resolve(data_path)

def is_matching_variable(context: Context, datablock: ID, data_path: str) -> bool:
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    return any(matching_property.datablock is datablock and matching_property.data_path == data_path for matching_property in matching_properties)

def add_matching_variable(context: Context, datablock: ID, data_path: str, minimum: float, maximum: float):
    if is_matching_variable(context, datablock, data_path):
        return
    scene = context.scene
    matching_properties = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    matching_property: MatchingProperty = matching_properties.add()
    matching_property.datablock = datablock
    matching_property.data_path = data_path
    matching_property.minimum = minimum
    matching_property.maximum = maximum

def remove_matching_variable(context: Context, datablock: ID, data_path: str):
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    for i, matching_property in enumerate(matching_properties):
        if matching_property.datablock is datablock and matching_property.data_path == data_path:
            matching_properties.remove(i)
            break