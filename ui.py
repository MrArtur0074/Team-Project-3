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

        obj = context.active_object
        if obj and hasattr(obj, 'lod_items'):
            # Add/Remove buttons
            row = lod_box.row()
            row.operator("object.add_lod", icon='ADD')
            row.operator("object.remove_lod", icon='REMOVE')

            # LOD Items list
            if obj.lod_items:
                for idx, item in enumerate(obj.lod_items):
                    if not item.lod_object:
                        continue

                    box = lod_box.box()
                    row = box.row()
                    
                    # Object name and status
                    row.label(text=f"LOD {idx + 1}: {item.lod_object.name}")
                    
                    # Modifier controls
                    if "LOD_Decimate" in item.lod_object.modifiers:
                        decimate_mod = item.lod_object.modifiers["LOD_Decimate"]
                        
                        # Ratio and Apply button
                        sub_row = box.row(align=True)
                        sub_row.prop(decimate_mod, "ratio", text="Ratio", slider=True)
                        
                        # Apply button operator
                        apply_op = sub_row.operator(
                            "object.apply_lod_modifiers",
                            text="",
                            icon='CHECKMARK'
                        )
                        apply_op.lod_index = idx
                    else:
                        # Show locked state
                        row.label(text="Applied", icon='LOCKED')

                    # Extra safety: show object selection button
                    box.operator(
                        "object.select_lod_object",
                        text="Select LOD Object"
                    ).lod_index = idx


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

        # Material Baker
        scene = context.scene

        baker_box = layout.box()
        baker_box.label(text="Material Baker", icon='TEXTURE')

        baker_box.prop(scene, "material_baker_bake_type", text="Bake Type")

        # Optional info label if 'ALL' is selected
        if scene.material_baker_bake_type == 'ALL':
            baker_box.label(text="All texture maps will be exported!", icon='INFO')

        baker_box.prop(scene, "material_baker_resolution", text="Resolution")
        baker_box.prop(scene, "material_baker_image_format", text="Image Format")
        baker_box.prop(scene, "material_baker_filepath", text="File Path")
        baker_box.operator("object.material_bake", text="Bake Material", icon='RENDER_RESULT')


def register():
    bpy.utils.register_class(VIEW3D_PT_engine_tools)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_engine_tools)