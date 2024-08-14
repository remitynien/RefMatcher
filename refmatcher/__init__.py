bl_info = {
    "name": "Ref Matcher",
    "description": "Makes your render match your reference image.",
    "author": "Rémi Tynien",
    "version": (0, 0),
    "blender": (4, 0, 0),
    "location": "Render panel",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Render"
}

import importlib

from refmatcher import properties, operators, hmi, image_comparison, dependencies, optimization, matching_variables, server
for module in [properties, operators, hmi, image_comparison, dependencies, optimization, matching_variables, server]:
    importlib.reload(module)

def register():
    properties.register()
    operators.register()
    hmi.register()


def unregister():
    hmi.unregister()
    operators.unregister()
    properties.unregister()
