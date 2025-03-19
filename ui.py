import bpy
from bpy.types import Panel

class VIEW3D_PT_engine_tools(Panel):
    bl_label = "Engine Tools"
    bl_idname = "VIEW3D_PT_engine_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Engine Tools"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.engine_tools_settings
        
        # Mesh Tools
        box = layout.box()
        box.label(text="Mesh Processing")
        box.operator("object.create_convex_hull", icon='MESH_CUBE')
        box.operator("object.triangulate_mesh", icon='MESH_DATA')
        box.operator("object.correct_normals", icon='NORMALS_FACE')
        box.operator("object.merge_vertices", icon='VERTEXSEL')
        
        # LOD System
        box = layout.box()
        box.label(text="LOD Management")
        row = box.row()
        row.operator("object.add_lod", icon='ADD')
        row.operator("object.remove_lod", icon='REMOVE')
        
        if context.active_object and context.active_object.lod_items:
            for idx, item in enumerate(context.active_object.lod_items):
                if obj := item.lod_object:
                    box.label(text=f"LOD {idx+1}: {obj.name}", icon='MOD_DECIM')
        
        # Export System
        box = layout.box()
        box.label(text="Export Settings")
        box.prop(settings, "export_format", text="Format")
        box.prop(settings, "export_folder", text="Folder")
        box.prop(settings, "export_apply_modifiers", toggle=1)
        row = box.row()
        row.operator("export.engine_selected", icon='EXPORT')
        row.operator("export.batch_engine", icon='EXPORT')

        # Preferences
        box = layout.box()
        box.label(text="Preferences")
        box.prop(settings, "lod_default_ratio")
        box.prop(settings, "merge_distance")

def register():
    bpy.utils.register_class(VIEW3D_PT_engine_tools)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_engine_tools)