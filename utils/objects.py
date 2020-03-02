#!/usr/bin/env python3

import io
from contextlib import redirect_stdout

import bpy

from nico_export import constants
from nico_export.utils import common

STDOUT = io.StringIO()


def get_export_list() -> list:
    """
    Gets a list of objects to be exported based on passed type.

    Returns:
        list: A nested list of objects.
    """
    scene = bpy.context.scene
    selected = bpy.context.selected_objects
    parents = []
    children = []

    for ob in selected:
        if scene.export_mode == "export_mode_root":
            ob = trace_parent(ob)

        if get_type(ob) != "" and not ob.export_ignore and not ob in parents:
            parents.append(ob)

            ob_children = []
            if scene.export_mode != "export_mode_selection":
                for child in get_children(ob):
                    if get_type(child) != "" and not child.export_ignore:
                        ob_children.append(child)

            children.append(ob_children)

    return [parents, children]


def export_mesh(main_scene: bpy.types.Scene, export_list: list) -> list:
    """
    Export mesh types.

    Args:
        main_scene (bpy.types.Scene): The scene the user exported from.
        export_list (object): The object to be exported.

    Returns:
        list: A list of successfully exported objects.
    """
    # TODO Check for non existent and orphaned objects before exporting
    # TODO Add specific exception handling

    scene = bpy.context.scene
    parents = export_list[0]
    children = export_list[1]

    for i, ob in enumerate(parents):
        filepath = common.export_filepath(ob)
        common.create_dir(filepath.parent)
        # client_root = p4.get_client_root()
        # opened_by = p4.opened_by(filepath.as_posix())
        # proj_asset_path = project.SETTINGS[scene.selected_project].asset_path
        # proj_name = project.SETTINGS[scene.selected_project].name

        # if scene.selected_project != "none" and client_root not in filepath.parents:
        #     raise Exception(f"'{filepath}' is not in the perforce client root.")

        # if scene.selected_project != "none" and proj_asset_path not in filepath.parents:
        #     raise Exception(f"'{filepath}' is not in the {proj_name} asset directory.")

        # if opened_by != "":
        #     raise Exception(f"'{filepath}' is checked out by {opened_by}")

        bpy.ops.object.select_all(action="DESELECT")

        for child in children[i]:
            child.select_set(True)

        ob.select_set(True)

        matrix = ob.matrix_world.copy()

        if ob.export_origin:
            ob.matrix_world.translation = (0, 0, 0)

        try:
            # if scene.selected_project != "none" and filepath.is_file():
            #     p4.edit(filepath.as_posix())

            with redirect_stdout(STDOUT):
                bpy.ops.export_scene.fbx(
                    filepath=str(filepath),
                    check_existing=False,
                    use_mesh_modifiers=scene.export_modifiers,
                    use_selection=True,
                    use_tspace=False,
                    global_scale=1.0,
                    apply_scale_options="FBX_SCALE_NONE",
                    apply_unit_scale=True,
                    object_types={"EMPTY", "MESH", "OTHER"},
                    mesh_smooth_type="FACE",
                    axis_forward=scene.export_forward_axis,
                    axis_up=scene.export_up_axis,
                )
            # if scene.selected_project != "none" and not p4.opened(filepath.as_posix()):
            #     p4.add(filepath.as_posix())
        except PermissionError:
            raise
        except Exception:
            raise
        else:
            # Add to property group to relay info back to user after export
            ob_exported = main_scene.ExportedList.add()
            ob_exported.object_name = filepath.stem
            ob_exported.object_type = get_type(ob)
            ob_exported.object_export_path = str(filepath)
            ob_exported.object = ob
        finally:
            ob.matrix_world = matrix

    return export_list


def check_type_selected(target_type: str) -> bool:
    """
    Checks type of all selected objects.

    Args:
        target_type (str): Type to test selected objects against.

    Returns:
        bool: True if all objects are of same type, False if not.
    """
    for ob in bpy.context.selected_objects:
        if ob.type != target_type.upper():
            return False
    return True


def get_type(ob: bpy.types.Object) -> str:
    """
    Gets object type derived from selected properties.

    Args:
        ob (bpy.types.Object): The object to evaluate.

    Returns:
        str: The object type or an empty string if type is unsupported.
    """
    scene = bpy.context.scene
    if ob.type in constants.EXPORT_TYPES:
        if ob.type == "MESH":
            if (
                ob.name.startswith(scene.export_prefix_collision)
                and constants.COL_MAT_NAME in ob.data.materials
            ):
                return "COLLISION"
        return ob.type
    return ""


def get_children(ob: bpy.types.Object) -> list:
    """
    Gets all child objects of passed object.

    Args:
        ob (bpy.types.Object): The parent object.

    Returns:
        list: A list of child objects.
    """
    children = []
    for child in ob.children:
        children.append(child)
        for c in get_children(child):
            children.append(c)
    return children


def select_hierarchy_active() -> bpy.types.Object:
    """
    Sets topmost object in the selected hierarchy as active object.

    Returns:
        bpy.types.Object: The topmost object.
    """
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

    return bpy.context.selected_objects[0]


def trace_parent(ob: bpy.types.Object) -> bpy.types.Object:
    """
    Moves up object hierarchy until the top-most parent is found.

    Args:
        ob (bpy.types.Object): The object where the trace starts.

    Returns:
        bpy.types.Object: The top-most parent object.
    """
    if ob.parent is None:
        return ob
    else:
        return trace_parent(ob.parent)
