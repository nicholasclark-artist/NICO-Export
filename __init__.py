#!/usr/bin/env python3

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from nico_export.operators import create_collision, export_object, open_docs
from nico_export.ui import menus, panels

bl_info = {
    "name": "NICO Export",
    "description": "NICO Export is a Blender 2.8 addon designed to improve the fbx export process.",
    "author": "Nicholas Clark",
    "version": (0, 4),
    "blender": (2, 80, 0),
    "location": "View3D > UI > NICO Export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

CLASSES = (
    panels.NC_PT_MainPanel,
    menus.NC_MT_SelectProject,
    panels.NC_PT_ObjectProperties,
    panels.NC_PT_Collisions,
    panels.NC_PT_ExportSettings,
    export_object.NC_OT_Export,
    create_collision.NC_OT_ConvexHull,
    open_docs.NC_OT_OpenDocs,
)

register, unregister = bpy.utils.register_classes_factory(CLASSES)

bpy.utils.register_class(export_object.NC_OT_ExportedInfo)
bpy.types.Scene.ExportedList = CollectionProperty(type=export_object.NC_OT_ExportedInfo)
