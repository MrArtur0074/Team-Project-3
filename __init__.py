bl_info = {
    "name": "Engine Exporter Pro",
    "author": "Your Name",
    "version": (2, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Engine Tools",
    "description": "Comprehensive game engine export toolkit with optimization features",
    "category": "Import-Export",
}

from . import operators, properties, ui, utils

def register():
    utils.register()
    properties.register()
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
    utils.unregister()

if __name__ == "__main__":
    register()