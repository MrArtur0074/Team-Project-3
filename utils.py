import os
import bpy

def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def select_only(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def select_objects(objects):
    for obj in objects:
        obj.select_set(True)

def export_selected_objects(format, folder, apply_modifiers=True):
    ensure_folder_exists(folder)
    
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            continue
        
        filepath = os.path.join(folder, f"{obj.name}.{format.lower()}")
        
        try:
            if format == 'FBX':
                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=True,
                    apply_scale_options='FBX_SCALE_UNITS',
                    bake_space_transform=apply_modifiers
                )
            elif format == 'GLTF':
                bpy.ops.export_scene.gltf(
                    filepath=filepath,
                    export_format='GLB',
                    use_selection=True,
                    export_apply=apply_modifiers
                )
            elif format == 'OBJ':
                bpy.ops.export_scene.obj(
                    filepath=filepath,
                    use_selection=True,
                    use_materials=False,
                    apply_modifiers=apply_modifiers
                )
        except Exception as e:
            print(f"Export failed for {obj.name}: {str(e)}")

def register():
    pass

def unregister():
    pass