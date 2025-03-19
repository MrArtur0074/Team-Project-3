import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

class VIEW3D_PT_engine_tools(Panel):
    bl_label = "Engine Tools"
    bl_idname = "VIEW3D_PT_engine_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Engine Tools"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.engine_tools_settings
        obj = context.active_object

        # Mesh Processing Tools (vertical layout)
        mesh_box = layout.box()
        mesh_box.label(text="Mesh Processing", icon='MESH_DATA')
        
        col = mesh_box.column(align=True)
        col.operator("object.create_convex_hull", icon='MESH_CUBE')
        col.operator("object.triangulate_mesh", icon='MOD_TRIANGULATE')
        col.operator("object.correct_normals", icon='NORMALS_FACE')
        col.operator("object.merge_vertices", icon='AUTOMERGE_ON')

        # LOD Management
        lod_box = layout.box()
        lod_box.label(text="LOD System", icon='MOD_DECIM')
        
        if obj and hasattr(obj, 'lod_items'):
            row = lod_box.row()
            row.operator("object.add_lod", icon='ADD')
            row.operator("object.remove_lod", icon='REMOVE')

            # In the LOD section:
            if obj.lod_items:
                for idx, item in enumerate(obj.lod_items):
                    if item.lod_object:
                        row = lod_box.row()
                        row.label(text=f"LOD {idx+1}: {item.lod_object.name}")
                        
                        if "LOD_Decimate" in item.lod_object.modifiers:
                            row.prop(item.lod_object.modifiers["LOD_Decimate"], "ratio", text="")
                            apply_op = row.operator(
                                "object.apply_lod_modifiers",  # Use bl_idname as string
                                text="", 
                                icon='CHECKMARK'
                            )
                            apply_op.lod_index = idx
                        else:
                            row.label(text="Applied", icon='LOCKED')

        # Export System
        export_box = layout.box()
        export_box.label(text="Export Tools", icon='EXPORT')
        
        col = export_box.column()
        col.prop(settings, "export_format", text="Format")
        col.prop(settings, "export_folder", text="Folder")
        col.prop(settings, "export_apply_modifiers", text="Apply Modifiers")
        
        row = export_box.row()
        row.operator("export.engine_selected", text="Export Selected", icon='EXPORT')
        row.operator("export.batch_engine", text="Batch Export", icon='EXPORT')

        # Preferences
        prefs_box = layout.box()
        prefs_box.label(text="Preferences", icon='PREFERENCES')
        prefs_box.prop(settings, "lod_default_ratio", slider=True)
        prefs_box.prop(settings, "merge_distance")

def register():
    bpy.utils.register_class(VIEW3D_PT_engine_tools)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_engine_tools)