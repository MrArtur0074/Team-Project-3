import bpy
import os

# Operator
class MaterialBakerOperator(bpy.types.Operator):
    bl_idname = "object.material_bake"
    bl_label = "Bake Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object!")
            return {'CANCELLED'}
        
        scene = bpy.context.scene
        bake_type = scene.material_baker_bake_type
        res_x = res_y = scene.material_baker_resolution
        image_format = scene.material_baker_image_format
        save_path = bpy.path.abspath(scene.material_baker_filepath)

        if not save_path.lower().endswith(('.png', '.jpg', '.jpeg', '.exr', '.tiff')):
            save_path = os.path.join(save_path, f"baked_texture.{image_format.lower()}")
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        bpy.context.scene.render.engine = 'CYCLES'

        image = bpy.data.images.new("BakedTexture", width=res_x, height=res_y)
        for slot in obj.material_slots:
            mat = slot.material
            if mat and mat.use_nodes:
                nodes = mat.node_tree.nodes
                tex_node = nodes.new(type='ShaderNodeTexImage')
                tex_node.image = image
                mat.node_tree.nodes.active = tex_node

        scene.render.bake.use_selected_to_active = False

        if bake_type == 'DIFFUSE':
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_pass_color = True
        elif bake_type == 'AO':
            scene.render.bake.use_pass_direct = True
        elif bake_type == 'NORMAL':
            scene.render.bake.use_pass_direct = False
        elif bake_type == 'COMBINED':
            scene.render.bake.use_pass_direct = True
            scene.render.bake.use_pass_indirect = True
            scene.render.bake.use_pass_color = True
        elif bake_type == 'SPECULAR':
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False

        wm = bpy.context.window_manager
        wm.progress_begin(0, 100)
        bpy.ops.object.bake(type=bake_type)
        wm.progress_update(50)

        image.filepath_raw = save_path
        image.file_format = image_format
        try:
            image.save()
            self.report({'INFO'}, f"Texture saved to {save_path}")
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save texture: {str(e)}")
            wm.progress_end()
            return {'CANCELLED'}

        wm.progress_update(100)
        wm.progress_end()

        return {'FINISHED'}

# UI Panel
class MaterialBakerPanel(bpy.types.Panel):
    bl_label = "Material Baker"
    bl_idname = "OBJECT_PT_material_baker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Material Baker"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "material_baker_bake_type", text="Bake Type")
        layout.prop(scene, "material_baker_resolution", text="Resolution")
        layout.prop(scene, "material_baker_image_format", text="Image Format")
        layout.prop(scene, "material_baker_filepath", text="File Path")
        layout.operator("object.material_bake")

# Register/Unregister
classes = [
    MaterialBakerOperator,
    MaterialBakerPanel,
]

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
            ('METALLIC', "Metallic", ""),
            ('AO', "Ambient Occlusion", ""),
            ('COMBINED', "Combined", ""),
            ('SPECULAR', "Specular", ""),
            ('TRANSMISSION', "Transmission", "")
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
