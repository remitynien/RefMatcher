import bpy
from bpy.types import Context, Property, ID
from refmatcher.properties import MatchingProperty, MATCHING_PROPERTIES_PROPNAME
from typing import Iterable
import re

def node_tree_data_collection() -> Iterable[Iterable[ID]]:
    # TODO: access through context.blend_data instead of bpy.data ?
    yield bpy.data.materials
    yield bpy.data.worlds
    yield bpy.data.textures
    yield bpy.data.linestyles
    yield bpy.data.lights
    yield bpy.data.scenes


def get_root_ID_from_embedded_ID(datablock: ID) -> tuple[ID, str]:
    """Tries to fix embedded data which are handled in this function and returns a tuple (root_id, path_to_embedded_id), raise a ValueError otherwise."""
    if not datablock.is_embedded_data:
        return (datablock, "")
    # TODO: find a better and generic way to access root ID. Might cause lags in huge Blender projects ?
    if datablock.id_type == 'NODETREE':
        for data_collection in node_tree_data_collection():
            for data in data_collection:
                node_tree = getattr(data, "node_tree")
                if node_tree is datablock:
                    return (data, "node_tree")
    raise ValueError(f"Unable to get parent data of embedded data {datablock}")

def check_ID(datablock: ID) -> bool:
    """Check if this datablock is usable for matching variables"""
    return not datablock.is_embedded_data and \
        not datablock.is_evaluated and \
        not datablock.is_library_indirect and \
        not datablock.is_missing and \
        not datablock.is_runtime_data

def check_context(context: Context) -> bool:
    """Check if current context is usable for adding or removing matching variables"""
    data = get_hovered_data(context)
    if data is None:
        return False
    datablock, _, _ = data
    return check_ID(datablock)

def is_optimizable_property(property: Property) -> bool:
    # return property.type in {"FLOAT", "INT"}
    return property.type == "FLOAT" # TODO: accept more types

def get_hovered_property(context: Context) -> Property | None:
    return getattr(context, 'button_prop', None)

def get_hovered_data(context: Context) -> tuple[bpy.types.AnyType, str, int] | None:
    prop = getattr(context, 'button_prop', None) # property struct of hovered property
    ptr = getattr(context, 'button_pointer', None) # bpy_struct direct or indirect parent of prop. Might or might not be parent datablock.
    if prop is None or ptr is None:
        return None

    try:
        data_path = ptr.path_from_id(prop.identifier) # path from datablock to the property
    except ValueError: # does not support path creation for this type
        return None
    except AttributeError: # path from id not found
        if prop.identifier in ptr: # if this is a custom property
            data_path = f"[\"{prop.identifier}\"]"
        else:
            return None

    datablock, _, array_index = context.property # data_path isn't taken from context.property since it doesn't return full data path on modifiers or nodes.
    if datablock.is_embedded_data:
        try:
            root_datablock, path = get_root_ID_from_embedded_ID(datablock)
            return (root_datablock, ".".join([path, data_path]), array_index)
        except ValueError:
            return None
    return (datablock, data_path, array_index)

def is_array(property: Property, array_index: int) -> bool:
    # determine if it is a vector property with array_length rather than array_index to handle colors better
    array_length = getattr(property, 'array_length', None)
    return array_length > 0 if array_length is not None else array_index != -1

def get_value(datablock: ID, data_path_indexed: str) -> float | None:
    return datablock.path_resolve(data_path_indexed)

def set_value(datablock: ID, data_path_indexed: str, value: float):
    match = re.match("^(.*)\\[([0-9]+)\\]$", data_path_indexed) # check if the data path is indexed
    if match:
        # if indexed, set the value in the array
        data_path = match.group(1)
        index = int(match.group(2))
        vector = datablock.path_resolve(data_path)
        vector[index] = value
    else:
        # if not indexed, set the value directly
        setattr(datablock.path_resolve(data_path_indexed, False).data, data_path_indexed.split(".")[-1], value)

def set_matching_values(context: Context, values: Iterable[float]):
    matching_properties: Iterable[MatchingProperty] = getattr(context.scene, MATCHING_PROPERTIES_PROPNAME)
    assert len(values) == len(matching_properties)
    for matching_property, value in zip(matching_properties, values):
        datablock, data_path_indexed = matching_property.datablock, matching_property.data_path_indexed
        set_value(datablock, data_path_indexed, value)

def check_matching_values(context: Context):
    matching_properties: Iterable[MatchingProperty] = getattr(context.scene, MATCHING_PROPERTIES_PROPNAME)
    for matching_property in matching_properties:
        datablock, data_path_indexed = matching_property.datablock, matching_property.data_path_indexed
        try:
            datablock.path_resolve(data_path_indexed)
        except ValueError:
            return False
    return True

def is_matching_variable(context: Context, datablock: ID, data_path: str, array_index: int = -1) -> bool:
    scene = context.scene
    data_path_indexed = data_path + f"[{array_index}]" if array_index >= 0 else data_path
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    return any(matching_property.datablock is datablock and matching_property.data_path_indexed == data_path_indexed for matching_property in matching_properties)

def add_matching_variable(context: Context, datablock: ID, data_path_indexed: str, minimum: float, maximum: float):
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    try:
        matching_property = next(matching_property for matching_property in matching_properties if matching_property.datablock is datablock and matching_property.data_path_indexed == data_path_indexed)
        # variable already exists, update it
        matching_property.minimum = minimum
        matching_property.maximum = maximum
    except StopIteration:
        # variable does not exist, add it
        matching_property: MatchingProperty = matching_properties.add()
        matching_property.datablock = datablock
        matching_property.data_path_indexed = data_path_indexed
        matching_property.minimum = minimum
        matching_property.maximum = maximum

def remove_matching_variable(context: Context, datablock: ID, data_path_indexed: str):
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    for i, matching_property in enumerate(matching_properties):
        if matching_property.datablock is datablock and matching_property.data_path_indexed == data_path_indexed:
            matching_properties.remove(i)
            break

def remove_matching_variables(context: Context, datablock: ID, data_pathes_indexed: list[str]):
    scene = context.scene
    matching_properties: Iterable[MatchingProperty] = getattr(scene, MATCHING_PROPERTIES_PROPNAME)
    # backward iteration since we are removing elements. Convert to list because enumerate returns a generator, which can't be reversed.
    for i, matching_property in reversed(list(enumerate(matching_properties))):
        if matching_property.datablock is datablock and matching_property.data_path_indexed in data_pathes_indexed:
            matching_properties.remove(i)