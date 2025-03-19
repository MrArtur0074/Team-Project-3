bl_info = {
    "name": "Engine Exporter Pro",
    "author": "BEAT",
    "version": (2, 0, 2),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Engine Export",
    "description": "Comprehensive game engine export toolkit with optimization features",
    "category": "Import-Export",
}
bl_info = {
    "name": "Engine Tools",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar",
    "description": "Game engine tools",
    "category": "Object",
}

from . import properties
from . import operators
from . import ui

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