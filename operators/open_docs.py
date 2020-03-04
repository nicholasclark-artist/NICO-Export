#!/usr/bin/env python3

import os

import bpy

from nico_export.utils import common


class NC_OT_OpenDocs(bpy.types.Operator):
    """Opens link to documentation."""
    bl_idname = "object.open_documentation_page"
    bl_label = f"Documentation {common.addon_version()}"
    bl_description = "Open documentation"

    def execute(self, context):
        os.system("start https://github.com/nicholasclark-artist/NICO-Export/blob/master/README.md")

        return {"FINISHED"}
