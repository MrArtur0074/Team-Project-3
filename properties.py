import bpy
import json
import os
from bpy.types import PropertyGroup
from bpy.props import *

class LODItem(PropertyGroup):
    lod_object: PointerProperty(type=bpy.types.Object)

class EngineToolsSettings(PropertyGroup):
    export_format: EnumProperty(
        name="Format",
        items=[
            ('FBX', "FBX", "Autodesk FBX"),
            ('GLTF', "GLTF", "GL Transmission Format"),
            ('OBJ', "OBJ", "Wavefront OBJ")
        ],
        default='FBX'
    )
    
    export_folder: StringProperty(
        name="Export Folder",
        subtype='DIR_PATH'
    )
    
    export_apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        default=True
    )
    
    lod_default_ratio: FloatProperty(
        name="LOD Ratio",
        min=0.01, max=1.0,
        default=0.5
    )
    
    merge_distance: FloatProperty(
        name="Merge Distance",
        min=0.0, soft_max=0.1,
        default=0.001,
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
    bpy.utils.register_class(LODItem)
    bpy.utils.register_class(EngineToolsSettings)
    bpy.types.Scene.engine_tools_settings = PointerProperty(type=EngineToolsSettings)
    load_prefs()

def unregister():
    save_prefs()
    del bpy.types.Scene.engine_tools_settings
    bpy.utils.unregister_class(EngineToolsSettings)
    bpy.utils.unregister_class(LODItem)