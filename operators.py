import bpy
import bmesh
import os
from bpy.props import *
from .utils import *
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    StringProperty
)

class OBJECT_OT_apply_lod_modifiers(bpy.types.Operator):
    bl_idname = "object.apply_lod_modifiers"
    bl_label = "Apply LOD Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates LODs(level of detail) for selected mesh"
    
    lod_index: IntProperty(default=-1)
    
    def execute(self, context):
        obj = context.active_object
        if not obj or self.lod_index < 0 or self.lod_index >= len(obj.lod_items):
            self.report({'ERROR'}, "Invalid LOD index")
            return {'CANCELLED'}
        
        lod_item = obj.lod_items[self.lod_index]
        if lod_item.lod_object:
            for mod in lod_item.lod_object.modifiers[:]:
                if mod.type == 'DECIMATE':
                    try:
                        bpy.ops.object.modifier_apply(
                            {"object": lod_item.lod_object}, 
                            modifier=mod.name
                        )
                    except RuntimeError as e:
                        self.report({'ERROR'}, f"Apply failed: {str(e)}")
                    finally:
                        lod_item.lod_object.modifiers.remove(mod)
        return {'FINISHED'}

class OBJECT_OT_create_convex_hull(bpy.types.Operator):
    bl_idname = "object.create_convex_hull"
    bl_label = "Create Convex Hull"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates convex hull for selected object"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if not bm.verts:
            self.report({'ERROR'}, "Mesh has no vertices")
            bm.free()
            return {'CANCELLED'}

        bmesh.ops.convex_hull(bm, input=list(bm.verts))
        new_mesh = bpy.data.meshes.new(f"{obj.name}_ConvexHull")
        bm.to_mesh(new_mesh)
        bm.free()

        new_obj = bpy.data.objects.new(f"{obj.name}_ConvexHull", new_mesh)
        context.collection.objects.link(new_obj)
        new_obj.location = obj.location
        return {'FINISHED'}

class OBJECT_OT_triangulate_mesh(bpy.types.Operator):
    bl_idname = "object.triangulate_mesh"
    bl_label = "Triangulate Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Converts quads to triangles"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(obj.data)
            bm.free()
        return {'FINISHED'}

class OBJECT_OT_correct_normals(bpy.types.Operator):
    bl_idname = "object.correct_normals"
    bl_label = "Correct Normals"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Corrects(flips) normals"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    
class OBJECT_OT_merge_vertices(bpy.types.Operator):
    bl_idname = "object.merge_vertices"
    bl_label = "Merge Vertices"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges verticles that are located too close too each other"

    def execute(self, context):
        settings = context.scene.engine_tools_settings
        threshold = settings.merge_distance / context.scene.unit_settings.scale_length
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=threshold)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class OBJECT_OT_add_lod(bpy.types.Operator):
    bl_idname = "object.add_lod"
    bl_label = "Add LOD"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Adds new LOD object"

    def execute(self, context):
        base_obj = context.active_object
        settings = context.scene.engine_tools_settings
        
        if not base_obj or base_obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        lod_obj = base_obj.copy()
        lod_obj.data = base_obj.data.copy()
        lod_obj.name = f"{base_obj.name}_LOD_{len(base_obj.lod_items)+1}"
        context.collection.objects.link(lod_obj)

        mod = lod_obj.modifiers.new(name="LOD_Decimate", type='DECIMATE')
        mod.ratio = settings.lod_default_ratio

        item = base_obj.lod_items.add()
        item.lod_object = lod_obj
        return {'FINISHED'}

class OBJECT_OT_remove_lod(bpy.types.Operator):
    bl_idname = "object.remove_lod"
    bl_label = "Remove LOD"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Removes last created LOD object"

    def execute(self, context):
        base_obj = context.active_object
        if not base_obj.lod_items:
            self.report({'ERROR'}, "No LODs to remove")
            return {'CANCELLED'}

        last_lod = base_obj.lod_items[-1].lod_object
        if last_lod:
            bpy.data.objects.remove(last_lod)
        base_obj.lod_items.remove(len(base_obj.lod_items)-1)
        return {'FINISHED'}
    
class OBJECT_OT_select_lod_object(bpy.types.Operator):
    bl_idname = "object.select_lod_object"
    bl_label = "Select LOD Object"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Selects a LOD object"
    
    lod_index: IntProperty(default=-1)

    def execute(self, context):
        obj = context.active_object
        if obj and self.lod_index < len(obj.lod_items):
            lod_obj = obj.lod_items[self.lod_index].lod_object
            if lod_obj:
                bpy.ops.object.select_all(action='DESELECT')
                lod_obj.select_set(True)
                context.view_layer.objects.active = lod_obj
        return {'FINISHED'}
    
class OBJECT_OT_export_selected(bpy.types.Operator):
    bl_idname = "export.engine_selected"
    bl_label = "Export Selected"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Exports selected objects in selected format"

    def execute(self, context):
        settings = context.scene.engine_tools_settings
        
        # Add safety check for modifiers
        if settings.export_apply_modifiers:
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    for mod in obj.modifiers:
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        export_selected_objects(
            settings.export_format,
            settings.export_folder,
            apply_modifiers=False 
        )
        return {'FINISHED'}

class OBJECT_OT_batch_export(bpy.types.Operator):
    bl_idname = "export.batch_engine"
    bl_label = "Batch Export"
    bl_description = "Exports selected objects as seperate files in selected format"
    
    def execute(self, context):
        settings = context.scene.engine_tools_settings
        original_selection = context.selected_objects
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                select_only(obj)
                export_selected_objects(
                    settings.export_format,
                    settings.export_folder,
                    apply_modifiers=settings.export_apply_modifiers
                )
        select_objects(original_selection)
        return {'FINISHED'}

classes = (
    OBJECT_OT_apply_lod_modifiers,
    OBJECT_OT_create_convex_hull,
    OBJECT_OT_triangulate_mesh,
    OBJECT_OT_correct_normals,
    OBJECT_OT_add_lod,
    OBJECT_OT_remove_lod,
    OBJECT_OT_select_lod_object,
    OBJECT_OT_merge_vertices,
    OBJECT_OT_export_selected,
    OBJECT_OT_batch_export
)

def register():
    for cls in classes:
        if not hasattr(bpy.types, cls.__name__):  # Prevent duplicate registration
            bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):  # Prevent unregistration errors
            bpy.utils.unregister_class(cls)