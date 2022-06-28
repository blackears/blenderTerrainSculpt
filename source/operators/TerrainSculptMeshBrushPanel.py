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
from .TerrainSculptMeshBrush import *
from .TerrainHeightPickerMeshOperator import *

 
#---------------------------

class TerrainSculptMeshBrushPanel(bpy.types.Panel):

    """Properties Panel for the Terrain Sculpt Mesh Brush"""
    bl_label = "Terrain Sculpt Mesh Brush"
    bl_idname = "OBJECT_PT_terrain_sculpt_mesh_brush"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Kitfox: Terrain"

    # bl_label = "Terrain Sculpt Mesh Brush"
    # bl_idname = "SCENE_PT_terrain_sculpt_mesh_brush"
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "scene"
#    bl_context = "world"
    
        

    @classmethod
    def poll(cls, context):
        obj = context.object
#        return obj != None and (obj.mode == 'EDIT' or obj.mode == 'OBJECT')
        return obj != None and (obj.mode == 'OBJECT')
        
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.terrain_sculpt_mesh_brush_props
        
#        pcoll = preview_collections["main"]
        
        #--------------------------------
        
        col = layout.column();
        #col.operator("kitfox.terrain_sculpt_mesh_brush_operator", text="Terrain Mesh Brush", icon_value = pcoll["uvBrush"].icon_id)
        col.operator("kitfox.terrain_sculpt_mesh_brush_operator", text="Terrain Brush for Meshes")
        
        
        col.prop(props, "radius")
        col.prop(props, "inner_radius")
        if props.brush_type == 'RAMP':
            col.prop(props, "strength_ramp")
        else:
            col.prop(props, "strength")
        col.prop(props, "use_pressure")
        col.prop(props, "terrain_origin")
        col.label(text="Brush Type:")
        col.prop(props, "brush_type", expand = True, text = "Brush Type")
        col.prop(props, "world_shape_type", text = "Land Shape")
        
        if props.brush_type == 'DRAW':
            col.prop(props, "draw_height")
            col.operator("kitfox.terrain_height_picker_mesh", text="Terrain height picker", icon="EYEDROPPER")
        
        if props.brush_type == 'ADD' or props.brush_type == 'SUBTRACT':
            col.prop(props, "add_amount")
        
        if props.brush_type == 'SMOOTH':
            col.prop(props, "smooth_edge_snap_distance")            
        
        if props.brush_type == 'RAMP':
            col.prop(props, "ramp_width")
            col.prop(props, "ramp_falloff")

#---------------------------



def register():

    #Register tools
    bpy.utils.register_class(TerrainSculptMeshProperties)
    bpy.utils.register_class(TerrainSculptMeshOperator)
    bpy.utils.register_class(TerrainHeightPickerMeshOperator)
    bpy.utils.register_class(TerrainSculptMeshBrushPanel)
    
    bpy.types.Scene.terrain_sculpt_mesh_brush_props = bpy.props.PointerProperty(type=TerrainSculptMeshProperties)

def unregister():
    bpy.utils.unregister_class(TerrainSculptMeshProperties)
    bpy.utils.unregister_class(TerrainSculptMeshOperator)
    bpy.utils.unregister_class(TerrainHeightPickerMeshOperator)
    bpy.utils.unregister_class(TerrainSculptMeshBrushPanel)
    
    del bpy.types.Scene.terrain_sculpt_mesh_brush_props


if __name__ == "__main__":
    register()
