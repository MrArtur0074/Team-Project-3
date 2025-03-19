import bpy
import json
import os
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty
)

class LODItem(PropertyGroup):
    lod_object: PointerProperty(
        name="LOD Object",
        type=bpy.types.Object,
        description="Linked LOD object"
    )

class EngineToolsSettings(PropertyGroup):
    export_format: EnumProperty(
        items=[
            ('FBX', "FBX", "FBX format"),
            ('GLTF', "GLTF", "GLTF format"),
            ('OBJ', "OBJ", "OBJ format")
        ],
        default='FBX'
    )
    export_folder: StringProperty(
        subtype='DIR_PATH',
        name="Export Folder"
    )
    export_apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        default=True
    )
    lod_default_ratio: FloatProperty(
        name="LOD Ratio",
        default=0.5,
        min=0.01,
        max=1.0
    )
    merge_distance: FloatProperty(
        name="Merge Distance",
        default=0.001,
        min=0.0,
        precision=4
    )

def register():
    bpy.utils.register_class(LODItem)
    bpy.utils.register_class(EngineToolsSettings)
    bpy.types.Object.lod_items = CollectionProperty(type=LODItem)
    bpy.types.Object.lod_index = IntProperty(default=0)
    
    classes = (
        OBJECT_OT_apply_lod_modifiers,
    )
    for cls in classes:
        bpy.utils.register_class(cls)
    # Scene-level settings
    bpy.types.Scene.engine_tools_settings = PointerProperty(type=EngineToolsSettings)

def unregister():
    # Clean up object properties
    del bpy.types.Object.lod_items
    del bpy.types.Object.lod_index
    
    # Clean up scene properties
    del bpy.types.Scene.engine_tools_settings
    
    # Unregister classes
    bpy.utils.unregister_class(EngineToolsSettings)
    bpy.utils.unregister_class(LODItem)