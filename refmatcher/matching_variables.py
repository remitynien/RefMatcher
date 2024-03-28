import bpy
from bpy.types import Context, Property, ID
from refmatcher.properties import MatchingProperty, MATCHING_PROPERTIES_PROPNAME
from typing import Iterable

def is_optimizable_property(property: Property) -> bool:
    # return property.type in {"FLOAT", "INT"}
    return property.type == "FLOAT" # TODO: accept more types

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

def is_matching_variable(context: Context, datablock: ID, data_path: str, array_index: int = -1) -> bool:
    scene = context.scene
    if array_index >= 0:
        data_path = data_path + f"[{array_index}]"
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    return any(matching_property.datablock is datablock and matching_property.data_path == data_path for matching_property in matching_properties)

def add_matching_variable(context: Context, datablock: ID, data_path: str, minimum: float, maximum: float):
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    try:
        matching_property = next(matching_property for matching_property in matching_properties if matching_property.datablock is datablock and matching_property.data_path == data_path)
        # variable already exists, update it
        matching_property.minimum = minimum
        matching_property.maximum = maximum
    except StopIteration:
        # variable does not exist, add it
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

def remove_matching_variables(context: Context, datablock: ID, data_pathes: list[str]):
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    # backward iteration since we are removing elements. Convert to list because enumerate returns a generator, which can't be reversed.
    for i, matching_property in reversed(list(enumerate(matching_properties))):
        if matching_property.datablock is datablock and matching_property.data_path in data_pathes:
            matching_properties.remove(i)