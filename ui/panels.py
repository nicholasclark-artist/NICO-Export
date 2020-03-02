#!/usr/bin/env python3

import os

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty

from nico_export import constants
from nico_export.utils import objects


class NC_PT_MainPanel(bpy.types.Panel):
    """Creates main panel that houses export properties."""

    bl_idname = "NC_PT_MainPanel"
    bl_label = "NICO Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NICO Export"

    def draw(self, context):
        ob = context.object
        layout = self.layout

        layout.operator("object.open_documentation_page", icon="HELP")


class NC_PT_ObjectProperties(bpy.types.Panel):
    """Creates a panel for basic object properties."""

    bl_idname = "NC_PT_ObjectProperties"
    bl_label = "Object Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NICO Export"
    bl_parent_id = "NC_PT_MainPanel"

    bpy.types.Object.export_origin = BoolProperty(
        name="Export at Origin",
        description="Move object to scene origin on export",
        default=True,
    )

    bpy.types.Object.export_ignore = BoolProperty(
        name="Ignore Object", description="Ignore object on export", default=False,
    )

    bpy.types.Object.export_prefix = StringProperty(
        name="Object Prefix",
        description="Export object with given prefix",
        maxlen=64,
        default="",
        subtype="FILE_NAME",
    )

    bpy.types.Object.export_subpath = StringProperty(
        name="Object Subpath",
        description="Export object to given subpath. This path is relative to the export path",
        maxlen=64,
        default="",
        subtype="FILE_NAME",
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = context.object

        if ob is not None:
            col = layout.column()

            # Show object's real type as well as its derived type
            inherit = ob.type.capitalize()
            ob_type = objects.get_type(ob).capitalize()

            if ob_type not in (inherit, ""):
                inherit = f"{inherit} . {ob_type}"

            col.label(
                text=f"{ob.parent_type.capitalize()} . {inherit}", icon="OBJECT_DATA",
            )

            col = layout.column()

            col_prefix = col.column()
            col_prefix.prop(ob, "export_prefix")

            col_subpath = col.column()
            col_subpath.prop(ob, "export_subpath")

            layout.separator()

            col_props = layout.column()

            col_origin = col_props.column()
            col_origin.prop(ob, "export_origin")

            col_ignore = col_props.column()
            col_ignore.prop(ob, "export_ignore")

            if scene.export_mode == "export_mode_root" and ob.parent is not None:
                col_prefix.enabled = False
                col_subpath.enabled = False
                col_origin.enabled = False

            if objects.get_type(ob) == "":
                layout.enabled = False
        else:
            layout.label(text="")


class NC_PT_Collisions(bpy.types.Panel):
    """Creates a panel for collision properties."""

    bl_idname = "NC_PT_Collisions"
    bl_label = "Collision"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NICO Export"
    bl_parent_id = "NC_PT_MainPanel"

    bpy.types.Scene.export_prefix_collision = StringProperty(
        name="Collision Prefix",
        description="Create collision objects with given prefix",
        maxlen=64,
        default=constants.COL_PREFIX,
        subtype="FILE_NAME",
    )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = context.object

        if ob is not None:
            col = layout.column()
            col.prop(scene, "export_prefix_collision")

            layout.separator()

            col = layout.column()
            col.enabled = ob.mode == "OBJECT" and objects.check_type_selected("MESH")
            col.operator("object.convex_hull", icon="MOD_WIREFRAME")

            if objects.get_type(ob) == "":
                layout.enabled = False
        else:
            layout.label(text="")


class NC_PT_ExportSettings(bpy.types.Panel):
    """Creates a panel for export settings."""

    bl_idname = "NC_PT_ExportSettings"
    bl_label = "Scene Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NICO Export"
    bl_parent_id = "NC_PT_MainPanel"

    bpy.types.Scene.export_mode = EnumProperty(
        name="Export Mode",
        description="Export procedure for objects",
        items=[
            ("export_mode_root", "Root", "Export hierarchy from the root object",),
            ("export_mode_selection", "Selection", "Export selected object(s)",),
            (
                "export_mode_recursive",
                "Recursive Selection",
                "Export selected object(s) with children",
            ),
        ],
        default="export_mode_root",
    )

    bpy.types.Scene.export_path = bpy.props.StringProperty(
        name="Export Path",
        description="Select an export directory. All meshes will export to this directory",
        maxlen=512,
        default=os.path.join("//", "export"),
        subtype="DIR_PATH",
    )

    bpy.types.Scene.export_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Apply object modifiers on export",
        default=True,
    )

    bpy.types.Scene.export_tspace = BoolProperty(
        name="Tangent Space",
        description="Add binormal and tangent vectors",
        default=False,
    )

    bpy.types.Scene.export_forward_axis = EnumProperty(
        name="Forward Axis",
        description="Export objects with selected forward axis",
        items=[
            ("X", "X", "",),
            ("Y", "Y", "",),
            ("Z", "Z", "",),
            ("-X", "-X", "",),
            ("-Y", "-Y", "",),
            ("-Z", "-Z", "",),
        ],
        default="-Y",
    )

    bpy.types.Scene.export_up_axis = EnumProperty(
        name="Up Axis",
        description="Export objects with selected up axis",
        items=[
            ("X", "X", "",),
            ("Y", "Y", "",),
            ("Z", "Z", "",),
            ("-X", "-X", "",),
            ("-Y", "-Y", "",),
            ("-Z", "-Z", "",),
        ],
        default="Z",
    )


    def draw(self, context):
        scene = context.scene
        ob = context.object
        layout = self.layout

        if ob is not None:
            col = layout.column()
            col.prop(scene, "export_mode")
            col.prop(scene, "export_path")

            layout.separator()

            col = layout.column()
            col.prop(scene, "export_forward_axis")
            col.prop(scene, "export_up_axis")

            layout.separator()

            col = layout.column()
            col.prop(scene, "export_modifiers")
            col.prop(scene, "export_tspace")

            layout.separator()

            row = layout.row()
            row.scale_y = 2.0
            row.operator("object.export", icon="EXPORT")

            if objects.get_type(ob) == "":
                row.enabled = False
        else:
            layout.label(text="")
