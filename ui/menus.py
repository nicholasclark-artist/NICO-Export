#!/usr/bin/env python3

import bpy


class NC_MT_SelectProject(bpy.types.Menu):
    """Creates a project selection menu."""
    bl_label = "Select a Project"
    preset_subdir = "nico_export/global-properties-presets"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset
