bl_info = {
    "name": "Engine Exporter Pro",
    "author": "BEAT",
    "version": (2, 0, 2),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Engine Export",
    "description": "Comprehensive game engine export toolkit with optimization features",
    "category": "Import-Export",
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