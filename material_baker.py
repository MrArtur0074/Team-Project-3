import bpy
import os

# Operator
class MaterialBakerOperator(bpy.types.Operator):
    bl_idname = "object.material_bake"
    bl_label = "Bake Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def bake_type_settings(self, bake_type):
        scene = bpy.context.scene
        scene.render.bake.use_selected_to_active = False
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = False

        if bake_type == 'DIFFUSE':
            scene.render.bake.use_pass_color = True
        elif bake_type == 'AO':
            scene.render.bake.use_pass_direct = True
        elif bake_type == 'COMBINED':
            scene.render.bake.use_pass_direct = True
            scene.render.bake.use_pass_indirect = True
            scene.render.bake.use_pass_color = True

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object!")
            return {'CANCELLED'}
        
        scene = bpy.context.scene
        bake_type = scene.material_baker_bake_type
        res_x = res_y = scene.material_baker_resolution
        image_format = scene.material_baker_image_format
        base_path = bpy.path.abspath(scene.material_baker_filepath)

        bpy.context.scene.render.engine = 'CYCLES'

        valid_bake_types = {
            'DIFFUSE', 'NORMAL', 'ROUGHNESS', 'EMIT',
            'AO', 'COMBINED', 'TRANSMISSION', 'ENVIRONMENT',
            'SHADOW', 'POSITION', 'UV'
        }

        if bake_type not in valid_bake_types and bake_type != 'ALL':
            self.report({'ERROR'}, f"Unsupported bake type: {bake_type}")
            return {'CANCELLED'}

        bake_types = [bake_type] if bake_type != 'ALL' else list(valid_bake_types)

        wm = bpy.context.window_manager
        wm.progress_begin(0, len(bake_types) * 100)

        for i, b_type in enumerate(bake_types):
            progress = i * 100
            wm.progress_update(progress)

            self.bake_type_settings(b_type)

            # Create unique image
            image_name = f"{obj.name}_{b_type.lower()}_bake"
            image = bpy.data.images.new(name=image_name, width=res_x, height=res_y, alpha=True, float_buffer=False)
            image.generated_color = (0, 0, 0, 1)

            # Create or use material
            if not obj.data.materials:
                mat = bpy.data.materials.new(name=f"{obj.name}_Material")
                obj.data.materials.append(mat)
            else:
                mat = obj.data.materials[0]

            if not mat.use_nodes:
                mat.use_nodes = True

            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Create image texture node
            tex_node = nodes.new("ShaderNodeTexImage")
            tex_node.image = image
            mat.node_tree.nodes.active = tex_node

            # Bake
            try:
                bpy.ops.object.bake(type=b_type)
            except RuntimeError as e:
                self.report({'ERROR'}, f"Bake failed for {b_type}: {str(e)}")
                continue

            # Optional: Save image to disk
            if base_path:
                final_path = os.path.splitext(base_path)[0] + f"_{b_type.lower()}.{image_format.lower()}"
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                image.filepath_raw = final_path
                image.file_format = image_format
                try:
                    image.save()
                    self.report({'INFO'}, f"{b_type} texture saved to {final_path}")
                except RuntimeError as e:
                    self.report({'ERROR'}, f"Failed to save {b_type}: {str(e)}")

            # Optional: pack image into the blend file
            image.pack()

            # Clean up baking node
            nodes.remove(tex_node)

            wm.progress_update(progress + 50)

        wm.progress_update(100)
        wm.progress_end()
        return {'FINISHED'}


# Register/Unregister
classes = [MaterialBakerOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.material_baker_bake_type = bpy.props.EnumProperty(
        name="Bake Type",
        description="Choose the type of bake",
        items=[
            ('DIFFUSE', "Diffuse", ""),
            ('NORMAL', "Normal", ""),
            ('ROUGHNESS', "Roughness", ""),
            ('EMIT', "Emission", ""),
            ('AO', "Ambient Occlusion", ""),
            ('COMBINED', "Combined", ""),
            ('TRANSMISSION', "Transmission", ""),
            ('ENVIRONMENT', "Environment", ""),
            ('SHADOW', "Shadow", ""),
            ('POSITION', "Position", ""),
            ('UV', "UV", ""),
            ('ALL', "All Types", "Export all texture types")
        ],
        default='DIFFUSE'
    )

    bpy.types.Scene.material_baker_resolution = bpy.props.IntProperty(
        name="Resolution",
        description="Texture Resolution",
        default=1024,
        min=256,
        max=8192
    )

    bpy.types.Scene.material_baker_image_format = bpy.props.EnumProperty(
        name="Image Format",
        description="Choose the image format",
        items=[
            ('PNG', "PNG", ""),
            ('JPEG', "JPEG", ""),
            ('EXR', "EXR", ""),
            ('TIFF', "TIFF", "")
        ],
        default='PNG'
    )

    bpy.types.Scene.material_baker_filepath = bpy.props.StringProperty(
        name="File Path",
        description="Path to save baked texture",
        default="//baked_texture.png",
        subtype='FILE_PATH'
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.material_baker_bake_type
    del bpy.types.Scene.material_baker_resolution
    del bpy.types.Scene.material_baker_image_format
    del bpy.types.Scene.material_baker_filepath
