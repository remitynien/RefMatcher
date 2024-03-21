bl_info = {
    "name": "Ref Matcher",
    "description": "Makes your render match your reference image.",
    "author": "Rémi Tynien",
    "version": (0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Right Panel > Ref Matcher",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Render"
}

import importlib

from refmatcher import properties, operators, hmi
for module in [properties, operators, hmi]:
    importlib.reload(module)

def register():
    properties.register()
    operators.register()
    hmi.register()


def unregister():
    hmi.unregister()
    operators.unregister()
    properties.unregister()
