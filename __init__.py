bl_info = {
    "name": "Engine Export",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Mesh Tools",
    "description": "Game engine export tools with mesh processing",
    "category": "Object",
}

from . import operators, properties, ui, utils

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()