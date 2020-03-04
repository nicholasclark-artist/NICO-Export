#!/usr/bin/env python3

import bpy
from nico_export.utils import collision


class NC_OT_ConvexHull(bpy.types.Operator):
    """Creates a convex hull mesh."""

    bl_label = "Create Convex Hull"
    bl_idname = "object.convex_hull"
    bl_description = "Creates a convex hull from the selected meshes"

    def execute(self, context):
        collision.convex_hull()
        return {"FINISHED"}
