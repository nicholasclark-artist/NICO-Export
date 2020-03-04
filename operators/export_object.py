#!/usr/bin/env python3

import time

import bpy
from bpy.props import PointerProperty, StringProperty
from bpy.types import Operator

from nico_export.utils import objects


class NC_OT_Export(Operator):
    """Gathers objects and exports with selected settings."""

    bl_label = "Export"
    bl_idname = "object.export"
    bl_description = "Export with selected settings"

    def execute(self, context):
        scene = bpy.context.scene

        if not bpy.data.is_saved:
            self.report({"WARNING"}, "Please save the file before exporting.")
            return {"CANCELLED"}

        start_time = time.process_time()
        scene.ExportedList.clear()

        export_scene = bpy.context.scene.copy()
        export_scene.name = "nc_export_temp"
        bpy.context.window.scene = export_scene

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode="OBJECT")

        # TODO Add specific error handling
        try:
            export_list = objects.get_export_list()
            objects.export_mesh(scene, export_list)
        except Exception as e:
            self.report({"ERROR"}, f"{e}")
            return {"CANCELLED"}
        else:
            self.report(
                {"INFO"},
                f"{len(scene.ExportedList)} asset(s) exported in {time.process_time() - start_time} sec.",
            )
        finally:
            bpy.context.window.scene = scene
            bpy.data.scenes.remove(export_scene)

        return {"FINISHED"}


class NC_OT_ExportedInfo(bpy.types.PropertyGroup):
    """Exported object info."""

    object_name: StringProperty(default="None")
    object_type: StringProperty(default="None")
    object_export_path: StringProperty(default="None")
    object: PointerProperty(type=bpy.types.Object)
