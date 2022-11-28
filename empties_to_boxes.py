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
        if child.type == 'EMPTY':
            collection_replace_empty(collection, child)

    bpy.data.objects.remove(e, do_unlink=True)

    return collection

def collection_replace_empty(collection, e):
    if e.children is None or len(e.children) == 0:
        e = replace_with_box(e)
        #unlink from active collection, relink to our collection
        bpy.context.collection.objects.unlink(e)
        collection.objects.link(e)
    else:
        e = replace_with_collection(e)
        collection.children.link(e)

def find_ancestor_node(e, pool):
	while(e.parent is not None and e.parent in pool):
		e = e.parent
	return e

class EBOX_OT_create_boxes(bpy.types.Operator):
    """Convert the selected empties to boxes"""
    bl_idname = "ec.create_boxes"
    bl_label = "create_boxes"
    bl_options = {'UNDO'}

    def execute(self, context):
        empties = set([i for i in bpy.context.selected_objects if i.type == "EMPTY"])
        empties = list(set([find_ancestor_node(i, empties) for i in empties]))
        for e in empties:
            collection_replace_empty(e.users_collection[0], e)

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
