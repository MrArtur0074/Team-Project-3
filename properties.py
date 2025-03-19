import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    FloatProperty
)
from .utils import save_prefs, load_prefs

class LODItem(PropertyGroup):
    lod_object: PointerProperty(type=bpy.types.Object)

def register():
    bpy.utils.register_class(LODItem)
    
    # LOD System
    bpy.types.Object.lod_items = CollectionProperty(type=LODItem)
    bpy.types.Object.lod_index = IntProperty(default=0)
    
    # Preferences
    bpy.types.Scene.selected_export_format = EnumProperty(
        name="Export Format",
        items=[
            ('FBX', "FBX", "FBX format"),
            ('GLTF', "GLTF", "GLTF format"),
            ('OBJ', "OBJ", "OBJ format")
        ],
        default='FBX',
        update=lambda s,c: save_prefs()
    )
    
    bpy.types.Scene.export_folder = StringProperty(
        name="Export Folder",
        subtype='DIR_PATH',
        update=lambda s,c: save_prefs()
    )
    
    bpy.types.Scene.lod_default_ratio = FloatProperty(
        name="LOD Default Ratio",
        default=0.5,
        min=0.0,
        max=1.0,
        update=lambda s,c: save_prefs()
    )
    
    bpy.types.Scene.merge_distance = FloatProperty(
        name="Merge Distance",
        default=0.001,
        min=0.0,
        step=0.0001,
        precision=4,
        update=lambda s,c: save_prefs()
    )
    
    load_prefs()

def unregister():
    save_prefs()
    del bpy.types.Object.lod_items
    del bpy.types.Object.lod_index
    del bpy.types.Scene.selected_export_format
    del bpy.types.Scene.export_folder
    del bpy.types.Scene.lod_default_ratio
    del bpy.types.Scene.merge_distance
    bpy.utils.unregister_class(LODItem)