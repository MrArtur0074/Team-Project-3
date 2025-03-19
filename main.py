bl_info = {
    "name": "Engine Exporter",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Engine Exporter",
    "description": """Add-on for exporting to game engines. 
                    It supports multiple export formats (FBX, GLTF, OBJ), 
                    material handling, and game engine configurations.""",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import bmesh
import os
from bpy.props import FloatProperty, IntProperty, PointerProperty, CollectionProperty, EnumProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup

# ---------------------------------------------------
# Utility Functions
# ---------------------------------------------------
def ensure_folder_exists(folder_path):
    """Ensure the export folder exists, creating it if necessary."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def export_selected_objects(export_format, export_folder):
    """Export selected objects in the specified format."""
    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        print("No objects selected for export.")
        return
    
    ensure_folder_exists(export_folder)

    for obj in selected_objects:
        filepath = os.path.join(export_folder, f"{obj.name}.{export_format.lower()}")
        print(f"Exporting {obj.name} as {export_format} to {filepath}")
        
        if export_format == 'FBX':
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
        elif export_format == 'GLTF':
            bpy.ops.export_scene.gltf_export(filepath=filepath, export_format='GLB', use_selection=True)
        elif export_format == 'OBJ':
            bpy.ops.export_scene.obj(filepath=filepath, use_selection=True, use_materials=False)

# ---------------------------------------------------
# Operator: Create Convex Hull
# ---------------------------------------------------
class OBJECT_OT_create_convex_hull(Operator):
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
        verts = list(bm.verts)
        if not verts:
            self.report({'ERROR'}, "Mesh has no vertices")
            bm.free()
            return {'CANCELLED'}

        bmesh.ops.convex_hull(bm, input=verts)

        new_mesh = bpy.data.meshes.new(obj.name + "_ConvexHull")
        bm.to_mesh(new_mesh)
        bm.free()

        new_obj = bpy.data.objects.new(obj.name + "_ConvexHull", new_mesh)
        context.collection.objects.link(new_obj)
        new_obj.location = obj.location

        self.report({'INFO'}, "Convex hull created")
        return {'FINISHED'}

# ---------------------------------------------------
# Operator: Triangulate Mesh
# ---------------------------------------------------
class OBJECT_OT_triangulate_mesh(Operator):
    bl_idname = "object.triangulate_mesh"
    bl_label = "Triangulate Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        bm.free()

        self.report({'INFO'}, "Mesh triangulated")
        return {'FINISHED'}

# ---------------------------------------------------
# Operator: Correct Normals
# ---------------------------------------------------
class OBJECT_OT_correct_normals(Operator):
    bl_idname = "object.correct_normals"
    bl_label = "Correct Normals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Normals recalculated")
        return {'FINISHED'}

# ---------------------------------------------------
# LOD Item PropertyGroup
# ---------------------------------------------------
class LODItem(PropertyGroup):
    lod_object: PointerProperty(
        name="LOD Object",
        type=bpy.types.Object,
        description="Reference to a LOD object"
    )  # type: ignore

# ---------------------------------------------------
# Operator: Add LOD
# ---------------------------------------------------
class OBJECT_OT_add_lod(Operator):
    """Add a new LOD object with a decimation modifier"""
    bl_idname = "object.add_lod"
    bl_label = "Add LOD"
    bl_options = {'REGISTER', 'UNDO'}

    default_ratio: FloatProperty(
        name="Default Ratio",
        description="Starting decimation ratio for the new LOD",
        default=0.5,
        min=0.0,
        max=1.0,
    ) # type: ignore

    def execute(self, context):
        base_obj = context.active_object
        if not base_obj or base_obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object to add LODs to")
            return {'CANCELLED'}

        # Duplicate the base object.
        lod_obj = base_obj.copy()
        lod_obj.data = base_obj.data.copy()
        lod_obj.name = f"{base_obj.name}_LOD_{len(base_obj.lod_items)+1}"
        context.collection.objects.link(lod_obj)

        # Add a decimate modifier (leave it unapplied so it can be adjusted)
        mod = lod_obj.modifiers.new(name="LOD_Decimate", type='DECIMATE')
        mod.ratio = self.default_ratio

        # Optionally store the ratio as a custom property.
        lod_obj["lod_decimation_ratio"] = self.default_ratio

        # Store a reference in the base object's collection of LOD items.
        item = base_obj.lod_items.add()
        item.lod_object = lod_obj

        self.report({'INFO'}, f"LOD object '{lod_obj.name}' created")
        return {'FINISHED'}

# ---------------------------------------------------
# Operator: Remove LOD
# ---------------------------------------------------
class OBJECT_OT_remove_lod(Operator):
    """Remove the last added LOD object"""
    bl_idname = "object.remove_lod"
    bl_label = "Remove LOD"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        base_obj = context.active_object
        if not base_obj or not hasattr(base_obj, "lod_items") or len(base_obj.lod_items) == 0:
            self.report({'ERROR'}, "No LOD objects found for the active object")
            return {'CANCELLED'}

        idx = len(base_obj.lod_items) - 1
        lod_item = base_obj.lod_items[idx]
        lod_obj = lod_item.lod_object
        if lod_obj:
            bpy.data.objects.remove(lod_obj, do_unlink=True)
        base_obj.lod_items.remove(idx)

        self.report({'INFO'}, "Last LOD object removed")
        return {'FINISHED'}

# ---------------------------------------------------
# Operator: Apply All Transforms
# ---------------------------------------------------
class OBJECT_OT_apply_all_transforms(Operator):
    bl_idname = "object.apply_all_transforms"
    bl_label = "Apply All Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        # Apply location, rotation, and scale
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        self.report({'INFO'}, "All transforms applied")
        return {'FINISHED'}

# ---------------------------------------------------
# Operator: Merge Duplicate Vertices
# ---------------------------------------------------
class OBJECT_OT_merge_vertices_by_distance(Operator):
    bl_idname = "object.merge_vertices_by_distance"
    bl_label = "Merge Duplicate Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    merge_distance: FloatProperty(
        name="Merge Distance",
        description="The maximum distance between vertices to merge them",
        default=0.001,
    ) # type: ignore

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.select_all(action='SELECT')

        recalculated_threshold = 0.001 / context.scene.unit_settings.scale_length
        bpy.ops.mesh.remove_doubles(threshold=recalculated_threshold, use_unselected=False)

        return {'FINISHED'}

# ---------------------------------------------------
# Operator: Export Format
# ---------------------------------------------------
class OBJECT_OT_export_format(Operator):
    bl_idname = "object.export_format"
    bl_label = "Choose Export Format and Folder"
    
    export_format: EnumProperty(
        name="Export Format",
        description="Choose the format for export",
        items=[
            ('FBX', "FBX", "Export in FBX format"),
            ('GLTF', "GLTF", "Export in GLTF format"),
            ('OBJ', "OBJ", "Export in OBJ format")
        ],
        default='FBX'
    )

    filepath: StringProperty(subtype='DIR_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        export_folder = self.filepath
        export_format = self.export_format
        print(f"Chosen format: {export_format}")
        print(f"Chosen export folder: {export_folder}")
        export_selected_objects(export_format, export_folder)
        return {'FINISHED'}

# ---------------------------------------------------
# UI Panel in the 3D View Sidebar
# ---------------------------------------------------
class VIEW3D_PT_mesh_tools(Panel):
    """Panel for Engine Exporter and LOD management"""
    bl_label = "Engine Exporter"
    bl_idname = "VIEW3D_PT_mesh_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Engine Exporter"

    def draw(self, context):
        layout = self.layout

        # Engine Exporter Section
        layout.label(text="Engine Exporter:")
        layout.operator("object.create_convex_hull", icon='MESH_CUBE')
        layout.operator("object.triangulate_mesh", icon='MESH_DATA')
        layout.operator("object.correct_normals", icon='TRACKING')
        layout.operator("object.apply_all_transforms", icon='FILE_TICK')
        layout.operator("object.merge_vertices_by_distance", icon='SNAP_VERTEX')
        layout.separator()

        # LOD Management Section
        layout.label(text="LOD Manager:")
        row = layout.row(align=True)
        row.operator("object.add_lod", text="", icon='ADD')
        row.operator("object.remove_lod", text="", icon='REMOVE')

        # List existing LOD objects (if any)
        base_obj = context.active_object
        if base_obj and hasattr(base_obj, "lod_items") and len(base_obj.lod_items) > 0:
            for idx, lod_item in enumerate(base_obj.lod_items):
                lod_obj = lod_item.lod_object
                if lod_obj:
                    box = layout.box()
                    row = box.row()
                    row.label(text=f"LOD {idx+1}: {lod_obj.name}")
                    # Find the decimate modifier in the LOD object.
                    mod = next((m for m in lod_obj.modifiers if m.type == 'DECIMATE'), None)
                    if mod:
                        row = box.row()
                        row.prop(mod, "ratio", text="Decimation Ratio")
        else:
            layout.label(text="No LOD objects found.")
        layout.separator()

        # Export Section
        layout.label(text="Export Tools:")
        layout.operator("object.export_format", text="Export Selected Objects")

# ---------------------------------------------------
# Registration
# ---------------------------------------------------
classes = [
    OBJECT_OT_create_convex_hull,
    OBJECT_OT_triangulate_mesh,
    OBJECT_OT_correct_normals,
    LODItem,
    OBJECT_OT_add_lod,
    OBJECT_OT_remove_lod,
    OBJECT_OT_apply_all_transforms,
    OBJECT_OT_merge_vertices_by_distance,
    OBJECT_OT_export_format,
    VIEW3D_PT_mesh_tools,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.lod_items = CollectionProperty(type=LODItem)
    bpy.types.Object.lod_index = IntProperty(default=0)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.lod_items
    del bpy.types.Object.lod_index

if __name__ == "__main__":
    register()