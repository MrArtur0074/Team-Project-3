import bpy
import bmesh
from bpy.props import FloatProperty, EnumProperty, StringProperty
from .utils import export_selected_objects

class OBJECT_OT_create_convex_hull(bpy.types.Operator):
    bl_idname = "object.create_convex_hull"
    bl_label = "Create Convex Hull"
    bl_options = {'REGISTER', 'UNDO'}

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

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class OBJECT_OT_add_lod(bpy.types.Operator):
    bl_idname = "object.add_lod"
    bl_label = "Add LOD"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base_obj = context.active_object
        if not base_obj or base_obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        lod_obj = base_obj.copy()
        lod_obj.data = base_obj.data.copy()
        lod_obj.name = f"{base_obj.name}_LOD_{len(base_obj.lod_items)+1}"
        context.collection.objects.link(lod_obj)

        mod = lod_obj.modifiers.new(name="LOD_Decimate", type='DECIMATE')
        mod.ratio = context.scene.lod_default_ratio

        item = base_obj.lod_items.add()
        item.lod_object = lod_obj
        return {'FINISHED'}

class OBJECT_OT_remove_lod(bpy.types.Operator):
    bl_idname = "object.remove_lod"
    bl_label = "Remove LOD"
    bl_options = {'REGISTER', 'UNDO'}

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

class OBJECT_OT_apply_all_transforms(bpy.types.Operator):
    bl_idname = "object.apply_all_transforms"
    bl_label = "Apply Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {'FINISHED'}

class OBJECT_OT_merge_vertices_by_distance(bpy.types.Operator):
    bl_idname = "object.merge_vertices_by_distance"
    bl_label = "Merge Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        threshold = context.scene.merge_distance / context.scene.unit_settings.scale_length
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=threshold)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class OBJECT_OT_export_format(bpy.types.Operator):
    bl_idname = "object.export_format"
    bl_label = "Export Selected"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='DIR_PATH')
    export_format: EnumProperty(
        items=[
            ('FBX', "FBX", "Export as FBX"),
            ('GLTF', "GLTF", "Export as GLTF"),
            ('OBJ', "OBJ", "Export as OBJ")
        ],
        default='FBX'
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        export_selected_objects(self.export_format, self.filepath)
        return {'FINISHED'}

def register():
    classes = [
        OBJECT_OT_create_convex_hull,
        OBJECT_OT_triangulate_mesh,
        OBJECT_OT_correct_normals,
        OBJECT_OT_add_lod,
        OBJECT_OT_remove_lod,
        OBJECT_OT_apply_all_transforms,
        OBJECT_OT_merge_vertices_by_distance,
        OBJECT_OT_export_format
    ]
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    classes = [
        OBJECT_OT_create_convex_hull,
        OBJECT_OT_triangulate_mesh,
        OBJECT_OT_correct_normals,
        OBJECT_OT_add_lod,
        OBJECT_OT_remove_lod,
        OBJECT_OT_apply_all_transforms,
        OBJECT_OT_merge_vertices_by_distance,
        OBJECT_OT_export_format
    ]
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)