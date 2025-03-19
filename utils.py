import os
import json
import bpy
from bpy import context

def get_addon_prefs():
    """Get add-on preferences from Blender's registry"""
    return context.preferences.addons[__package__].preferences

def get_config_path():
    """Get platform-specific config path"""
    config_dir = bpy.utils.user_resource('CONFIG')
    addon_dir = os.path.join(config_dir, "Team-Project-3")
    os.makedirs(addon_dir, exist_ok=True)
    return os.path.join(addon_dir, "preferences.json")

def save_prefs():
    """Save preferences to JSON with error handling"""
    prefs = {
        'export_settings': {
            'format': context.scene.export_format,
            'folder': context.scene.export_folder,
            'apply_modifiers': context.scene.export_apply_modifiers
        },
        'mesh_settings': {
            'lod_ratio': context.scene.lod_default_ratio,
            'merge_distance': context.scene.merge_distance,
            'auto_smooth': context.scene.auto_smooth_angle
        }
    }
    
    try:
        with open(get_config_path(), 'w') as f:
            json.dump(prefs, f, indent=2)
    except Exception as e:
        print(f"Failed to save preferences: {str(e)}")

def load_prefs():
    """Load preferences from JSON with version checking"""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return

    try:
        with open(config_path, 'r') as f:
            prefs = json.load(f)
            
            # Export settings
            if 'export_settings' in prefs:
                es = prefs['export_settings']
                context.scene.export_format = es.get('format', 'FBX')
                context.scene.export_folder = es.get('folder', '')
                context.scene.export_apply_modifiers = es.get('apply_modifiers', True)
                
            # Mesh settings
            if 'mesh_settings' in prefs:
                ms = prefs['mesh_settings']
                context.scene.lod_default_ratio = ms.get('lod_ratio', 0.5)
                context.scene.merge_distance = ms.get('merge_distance', 0.001)
                context.scene.auto_smooth_angle = ms.get('auto_smooth', 30.0)
                
    except Exception as e:
        print(f"Error loading preferences: {str(e)}")