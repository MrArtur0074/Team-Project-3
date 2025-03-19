import bpy
from bpy.types import Panel

class VIEW3D_PT_mesh_tools(Panel):
    bl_label = "Engine Exporter"
    bl_idname = "VIEW3D_PT_mesh_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mesh Tools"

    def draw(self, context):
        layout = self.layout
        
        # Mesh Tools
        layout.label(text="Mesh Processing:")
        col = layout.column()
        col.operator("object.create_convex_hull", icon='MESH_CUBE')
        col.operator("object.triangulate_mesh", icon='MESH_DATA')
        col.operator("object.correct_normals", icon='NORMALS_FACE')
        col.operator("object.apply_all_transforms", icon='ORIENTATION_GLOBAL')
        col.operator("object.merge_vertices_by_distance", icon='VERTEXSEL')
        
        # LOD Management
        layout.separator()
        layout.label(text="LOD System:")
        row = layout.row(align=True)
        row.operator("object.add_lod", icon='ADD')
        row.operator("object.remove_lod", icon='REMOVE')
        
        if lod_items := context.active_object.lod_items:
            box = layout.box()
            for i, item in enumerate(lod_items):
                if obj := item.lod_object:
                    row = box.row()
                    row.label(text=f"LOD {i+1}: {obj.name}")
                    if mod := next((m for m in obj.modifiers if m.type == 'DECIMATE'), None):
                        row.prop(mod, "ratio", text="")
        
        # Export System
        layout.separator()
        layout.label(text="Export Settings:")
        box = layout.box()
        box.prop(context.scene, "selected_export_format", text="Format")
        box.prop(context.scene, "export_folder", text="Folder")
        layout.operator("object.export_format", icon='EXPORT')

        # Preferences
        layout.separator()
        layout.label(text="Preferences:")
        prefs_box = layout.box()
        prefs_box.prop(context.scene, "lod_default_ratio")
        prefs_box.prop(context.scene, "merge_distance")

def register():
    bpy.utils.register_class(VIEW3D_PT_mesh_tools)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_mesh_tools)