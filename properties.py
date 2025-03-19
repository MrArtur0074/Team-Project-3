import bpy
import json
import os
from bpy.types import PropertyGroup
from bpy.props import *

class LODItem(PropertyGroup):
    lod_object: PointerProperty(
        name="LOD Object",
        type=bpy.types.Object,
        description="Reference to a LOD object"
    )

class EngineToolsSettings(PropertyGroup):
    export_format: EnumProperty(
        name="Export Format",
        items=[
            ('FBX', "FBX", "Export in FBX format"),
            ('GLTF', "GLTF", "Export in GLTF format"),
            ('OBJ', "OBJ", "Export in OBJ format")
        ],
        default='FBX'
    )
    
    export_folder: StringProperty(
        name="Export Folder",
        description="Path to export directory",
        subtype='DIR_PATH'
    )
    
    export_apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers before exporting",
        default=True
    )
    
    lod_default_ratio: FloatProperty(
        name="LOD Default Ratio",
        description="Default decimation ratio for new LODs",
        default=0.5,
        min=0.01,
        max=1.0,
        step=0.1
    )
    
    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Distance threshold for merging vertices",
        default=0.001,
        min=0.0,
        soft_max=0.1,
        precision=4
    )

def get_prefs_path():
    config_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(config_dir, "Team-Project-3", "preferences.json")

def load_prefs():
    prefs_path = get_prefs_path()
    if os.path.exists(prefs_path):
        try:
            with open(prefs_path, 'r') as f:
                prefs = json.load(f)
                settings = bpy.context.scene.engine_tools_settings
                for key, value in prefs.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
        except Exception as e:
            print(f"Error loading preferences: {str(e)}")

def save_prefs():
    settings = bpy.context.scene.engine_tools_settings
    prefs = {
        'export_format': settings.export_format,
        'export_folder': settings.export_folder,
        'export_apply_modifiers': settings.export_apply_modifiers,
        'lod_default_ratio': settings.lod_default_ratio,
        'merge_distance': settings.merge_distance
    }
    
    prefs_path = get_prefs_path()
    os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
    
    try:
        with open(prefs_path, 'w') as f:
            json.dump(prefs, f, indent=2)
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")

def register():
    # Register property groups first
    bpy.utils.register_class(LODItem)
    bpy.utils.register_class(EngineToolsSettings)
    
    # Attach LOD system to Object type
    bpy.types.Object.lod_items = CollectionProperty(type=LODItem)
    bpy.types.Object.lod_index = IntProperty(default=0)
    
    # Create scene-level settings
    bpy.types.Scene.engine_tools_settings = PointerProperty(type=EngineToolsSettings)
    
    # Load saved preferences
    load_prefs()

def unregister():
    # Save preferences before unloading
    save_prefs()
    
    # Clean up object properties first
    del bpy.types.Object.lod_items
    del bpy.types.Object.lod_index
    
    # Clean up scene properties
    del bpy.types.Scene.engine_tools_settings
    
    # Unregister classes
    bpy.utils.unregister_class(EngineToolsSettings)
    bpy.utils.unregister_class(LODItem)