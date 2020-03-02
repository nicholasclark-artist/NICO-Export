#!/usr/bin/env python3

from pathlib import Path

import bpy

import addon_utils
from nico_export.utils import objects


def addon_version() -> str:
    """
    Gets the addon version.

    Returns:
        str: A formatted version string.
    """
    for mod in addon_utils.modules():
        if mod.bl_info["name"] == "NICO Export":
            version = mod.bl_info.get("version", (0, 0))
            return f"v{version[0]}.{version[1]}"


def create_dir(directory: Path) -> None:
    """
    Creates a directory if it does not exist.

    Args:
        directory (Path): Directory path.
    """
    Path.mkdir(directory, parents=True, exist_ok=True)


def export_filepath(ob: bpy.types.Object, ext: str = "fbx") -> Path:
    """
    Generates a valid export file path.

    Args:
        ob (bpy.types.Object): The object at the stem of the path.
        ext (str, optional): The path extension. Defaults to "fbx".

    Returns:
        Path: A WindowsPath to the export file.
    """
    scene = bpy.context.scene
    obj_type = objects.get_type(ob)
    name = ob.name

    if obj_type != "COLLISION":
        name = f"{ob.export_prefix}{name}"

    name = f"{name}.{ext}"

    filepath = Path(bpy.path.abspath(scene.export_path))

    if ob.export_subpath != "":
        ob.export_subpath = ob.export_subpath.lstrip("\\/")
        filepath = filepath / ob.export_subpath

    filepath = filepath / name

    return filepath
