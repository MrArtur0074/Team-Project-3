import bpy
from bpy.types import PropertyGroup
from bpy.props import *
from .utils import load_prefs, save_prefs

class LODItem(PropertyGroup):
    lod_object: PointerProperty(type=bpy.types.Object)

# Custom scene properties
class EngineExportSettings(PropertyGroup):
    export_format: EnumProperty(
        items=[
            ('FBX', "FBX", "Autodesk FBX format"),
            ('GLTF', "GLTF", "GL Transmission Format"),
            ('OBJ', "OBJ", "Wavefront OBJ")
        ],
        default='FBX',
        update=lambda s,c: save_prefs()
    )
    
    export_folder: StringProperty(
        subtype='DIR_PATH',
        update=lambda s,c: save_prefs()
    )
    
    export_apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        default=True,
        update=lambda s,c: save_prefs()
    )
    
    lod_default_ratio: FloatProperty(
        name="LOD Ratio",
        min=0.01, max=1.0,
        default=0.5,
        update=lambda s,c: save_prefs()
    )
    
    merge_distance: FloatProperty(
        name="Merge Distance",
        min=0.0, soft_max=0.1,
        default=0.001,
        precision=4,
        update=lambda s,c: save_prefs()
    )
    
    auto_smooth_angle: FloatProperty(
        name="Auto Smooth Angle",
        min=0.0, max=180.0,
        default=30.0,
        subtype='ANGLE',
        update=lambda s,c: save_prefs()
    )

def register():
    bpy.utils.register_class(LODItem)
    bpy.utils.register_class(EngineExportSettings)
    bpy.types.Scene.engine_export = PointerProperty(type=EngineExportSettings)
    load_prefs()

def unregister():
    save_prefs()
    bpy.utils.unregister_class(EngineExportSettings)
    bpy.utils.unregister_class(LODItem)
    del bpy.types.Scene.engine_export