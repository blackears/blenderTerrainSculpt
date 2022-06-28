# This file is part of the Kitfox Normal Brush distribution (https://github.com/blackears/terrainSculpt).
# Copyright (c) 2021 Mark McKay
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import bpy.utils.previews
import os
import bgl
import blf
import gpu
import mathutils
import math
import bmesh
from ..kitfox.math.vecmath import *
from ..kitfox.blenderUtil import *
from .Common import *
from .SmoothingInfo import *
from .TerrainSculptMeshProperties import *
from .TerrainHeightPickerMeshOperator import *


class TerrainSculptWorkspaceTool(bpy.types.WorkSpaceTool):  
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "kitfox_terrain.terrain_brush_draw"
    bl_label = "Terrain Brush Draw"
    bl_description = ("Raise or lower terrain under cursor to the current brush height.")

    bl_icon =  "ops.gpencil.draw.poly"          
    bl_widget = None 
    bl_keymap = (
        ("kitfox.echo_tool", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("tool_mode", "DEFAULT" )]}),
        ("kitfox.echo_tool", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("tool_mode", "CONTROL")]}),
        ("kitfox.echo_tool", {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("tool_mode", "ALT")]}),
        ("kitfox.echo_tool", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("tool_mode", "SHIFT")]}),
        ("kitfox.echo_tool", {"type": 'LEFTMOUSE', "value": 'PRESS', "oskey": True},
         {"properties": [("tool_mode", "OSKEY")]}),
        ("kitfox.echo_tool", {"type": 'LEFTMOUSE', "value": 'PRESS', "oskey" : True , "alt": True},
         {"properties": [("tool_mode", "OS+ALT")]}),    
        ("kitfox.echo_tool", {"type": 'MOUSEMOVE', "value": 'ANY' }, {"properties": []}),
    )



class EchoToolOperator(bpy.types.Operator):
    """Echo tool"""
    bl_idname = "kitfox.echo_tool"
    bl_label = "Echo tool"
    bl_options = {"REGISTER", "UNDO"}
    
    is_running = False

    # tool_mode : bpy.props.EnumProperty(
    #     name="Tool Mode",
    #     description="Tool Mode",
    #     items=enum_tool_callback,
    # )

    tool_mode : bpy.props.StringProperty(
        name="Tool Mode",
        description="Tool Mode",
    )

    # @classmethod
    # def poll( cls , context ) :
    #     return not EchoToolOperator.is_running

    def __init__(self):
        self.picking = False

    def modal(self, context, event):
        print("modal evTyp:%s evVal:%s mode:%s" % (str(event.type), str(event.value), self.tool_mode))

        if context.mode != 'OBJECT':
            EchoToolOperator.is_running = False
            return {'CANCELED'}

        return {'RUNNING_MODAL'}
#        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        print("invoke evTyp:%s evVal:%s mode:%s" % (str(event.type), str(event.value), self.tool_mode))

        # if EchoToolOperator.is_running:
        #     return {'CANCELLED'}
        context.window_manager.modal_handler_add(self)

        EchoToolOperator.is_running = True

        return {'RUNNING_MODAL'}
