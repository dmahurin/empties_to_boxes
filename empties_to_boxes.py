bl_info = {
    "name": "Empties to Boxes",
    "author": "Don Mahurin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Tool> Empties to Boxes",
    "description": "Convert empties into boxes",
    "category": "3D View"
}

import bpy

def replace_with_box(e):
    bpy.ops.mesh.primitive_cube_add(size=1, location = e.matrix_world.to_translation(), rotation = e.matrix_world.to_euler(), scale = e.matrix_world.to_scale())
    box = bpy.context.selected_objects[0]
    name = e.name
    bpy.data.objects.remove(e, do_unlink=True)
    box.name = name

    return box

def replace_with_collection(e):
    collection = bpy.data.collections.new(e.name)

    for child in e.children:
        if child.children is None or len(child.children) == 0:
            child = replace_with_box(child)
            #unlink from active collection, relink to our collection
            bpy.context.collection.objects.unlink(child)
            collection.objects.link(child)
        else:
            child = replace_with_collection(child)
            collection.children.link(child)

    bpy.data.objects.remove(e, do_unlink=True)

    return collection

def get_root_node(e):
	while(e.parent is not None):
		e = e.parent
	return e

class EBOX_OT_create_boxes(bpy.types.Operator):
    """Convert the selected empties to boxes"""
    bl_idname = "ec.create_boxes"
    bl_label = "create_boxes"
    bl_options = {'UNDO'}

    def execute(self, context):
        selected_empties_roots = list(set([get_root_node(i) for i in bpy.context.selected_objects if i.type == "EMPTY" and len(i.children) == 0]))
        for e in selected_empties_roots:
            e.users_collection[0].children.link(replace_with_collection(e))

        return {'FINISHED'}

class EBOX_PT_menu(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_label = "Empties to Boxes"
    bl_idname = "EBOX_PT_menu"

    def draw(self, context):
        layout = self.layout
        object = context.object
        scene = context.scene

        col = layout.column(align=True)
        col.operator("ec.create_boxes", text="Create Boxes")

classes = (EBOX_OT_create_boxes, EBOX_PT_menu)

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

def unregister():
    from bpy.utils import unregister_class
    for c in reversed(classes):
        unregister_class(c)

if __name__ == "__main__":
    register()
