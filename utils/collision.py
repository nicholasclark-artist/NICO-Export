#!/usr/bin/env python3

import bpy

from nico_export import constants
from nico_export.utils import objects


def create_collision_mat():
    """
    Creates a material used for collision objects.

    Returns:
        bpy.types.Material: The created collision material or the existing collision material.
    """
    mat = bpy.data.materials.get(constants.COL_MAT_NAME)
    if mat is None:
        mat = bpy.data.materials.new(name=constants.COL_MAT_NAME)

    mat.diffuse_color = constants.COL_MAT_DIFFUSE
    mat.blend_method = "BLEND"
    mat.use_nodes = True
    node_tree = mat.node_tree
    nodes = node_tree.nodes
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (0, 0)

    trans = nodes.new("ShaderNodeBsdfTransparent")
    trans.location = (-200, 0)
    trans.inputs[0].default_value = constants.COL_MAT_DIFFUSE_NODE

    node_tree.links.new(trans.outputs["BSDF"], out.inputs[0])

    return mat


def set_collision_mat(ob: bpy.types.Object) -> bpy.types.Material:
    """
    Makes the collision material the active material for the passed object.

    Args:
        ob (bpy.types.Object): The object to set.

    Returns:
        bpy.types.Material: The collision material.
    """
    ob.data.materials.clear()
    ob.active_material_index = 0

    mat = create_collision_mat()
    ob.data.materials.append(mat)

    return mat


# TODO Auto decimate hull if over certain threshold
def convex_hull() -> None:
    """
    Creates a convex hull from the selected meshes.
    """
    scene = bpy.context.scene
    main_ob = bpy.context.view_layer.objects.active
    bpy.ops.object.duplicate()

    obs = bpy.context.selected_objects
    parent_ob = objects.select_hierarchy_active()

    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")

    for ob in obs:
        bpy.context.view_layer.objects.active = ob
        for mod in [m for m in ob.modifiers]:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.context.view_layer.objects.active = parent_ob

    if len(obs) > 1:
        bpy.ops.object.join()

    hull = bpy.context.view_layer.objects.active

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.convex_hull(
        use_existing_faces=False, delete_unused=True, join_triangles=False
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    main_ob.select_set(True)
    hull.select_set(True)
    bpy.context.view_layer.objects.active = main_ob

    bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)

    set_collision_mat(hull)
    hull.show_wire = True
    hull.show_transparent = True

    # Name will iterate using UE4 custom collision convention
    if scene.export_prefix_collision == "":
        name = f"{constants.COL_PREFIX}{main_ob.name}"
    else:
        name = f"{scene.export_prefix_collision}{main_ob.name}"

    for num in range(1000):
        new_name = f"{name}_{'%02d' % num}"
        if new_name not in [ob.name for ob in bpy.context.scene.objects]:
            hull.name = new_name
            hull.data.name = new_name
            break
        print(f"Cannot set correct name for collision: {hull.name}")

    bpy.ops.object.select_all(action="DESELECT")
