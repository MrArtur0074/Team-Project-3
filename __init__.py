bl_info = {
    "name": "Engine Exporter Pro",
    "author": "BEAT",
    "version": (2, 0, 5),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Engine Export",
    "description": "Comprehensive game engine export toolkit with optimization features",
    "category": "Import-Export",
}

from . import material_baker
from . import properties
from . import operators
from . import ui

def register():
    properties.register()
    operators.register()
    ui.register()
    material_baker.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
    material_baker.unregister()

if __name__ == "__main__":
    register()