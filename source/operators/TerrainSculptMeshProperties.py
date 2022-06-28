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
#from smoothingInfo import *

class TerrainSculptMeshProperties(bpy.types.PropertyGroup):
    
    radius : bpy.props.FloatProperty(
        name = "Radius", 
        description = "Radius of brush.  Use [, ] keys to adjust.", 
        default = 1, 
        min = 0, 
        soft_max = 4
    )
    
    inner_radius : bpy.props.FloatProperty(
        name = "Inner Radius", 
        description = "Inner Radius of brush.  Used for hardness of brush edge.  Use Shift plus [, ] keys to adjust.", 
        default = 0, 
        min = 0, 
        max = 1
    )

    strength : bpy.props.FloatProperty(
        name = "Strength", 
        description = "Strength of brush.", 
        default = 1, 
        min = 0,
        max = 1
    )

    strength_ramp : bpy.props.FloatProperty(
        name = "Ramp Strength", 
        description = "Strength for ramp tool.", 
        default = 1, 
        min = 0,
        soft_max = 1
    )

    use_pressure : bpy.props.BoolProperty(
        name = "Pen Pressure", 
        description = "If true, pen pressure is used to adjust strength.", 
        default = False
    )

    terrain_origin : bpy.props.PointerProperty(
        name = "Terrain Origin", 
        description = "Defines the origin point for modes that depend on a distance from the origin.  World origin used if not set.", 
        type = bpy.types.Object
    )

    brush_type : bpy.props.EnumProperty(
        items=(
            ('DRAW', "Draw (D)", "Draw terrain at the given height above the origin."),
            ('LEVEL', "Level (L)", "Make terrain the same height as the spot where you first place your brush."),
            ('ADD', "Add (A)", "Add to terrain height."),
            ('SUBTRACT', "Subtract (S)", "Subtract from terrain height."),
            ('SLOPE', "Slope (P)", "Use the slope of the surface under the brush to set height."),
            ('SMOOTH', "Smooth (M)", "Average out the terrain under the brush."),
            ('RAMP', "Ramp (R)", "Draw a ramp between where you press and release the mouse."),
        ),
        default='DRAW'
    )

    world_shape_type : bpy.props.EnumProperty(
        items=(
            ('FLAT', "Flat", "Terrain is flat and gravity points along -Z."),
            ('SPHERE', "Sphere", "Terrain is sphere shaped (like a planet) and gravity points toward the origin."),
        ),
        default='FLAT'
    )

    draw_height : bpy.props.FloatProperty(
        name = "Draw Height", 
        description = "Distance above origin to draw terrain.  Use Up, Down arrow to adjust.", 
        default = 1, 
        soft_min = 0,
        soft_max = 100
    )

    add_amount : bpy.props.FloatProperty(
        name = "Add Amount", 
        description = "Amount to add or subtract when those modes are used.", 
        default = 1, 
        soft_min = 0,
        soft_max = 100
    )

    smooth_edge_snap_distance : bpy.props.FloatProperty(
        name = "Smooth Snap Distance", 
        description = "When using the smooth tool with more than one mesh selected, this determines whether vertices in the different meshes are treated as if they're the same vertex.  That is, if the two vertices are less than this distance apart when looking in the 'down' direction, they are treated as if they are connected.", 
        default = .001, 
        min = 0,
        soft_max = .1
    )

    ramp_width : bpy.props.FloatProperty(
        name = "Ramp Width", 
        description = "The width of the ramp.", 
        default = 1, 
        min = 0,
        soft_max = 10
    )
    
    ramp_falloff : bpy.props.FloatProperty(
        name = "Ramp Falloff", 
        description = "Softness of the edge of the ramp.", 
        default = .2, 
        min = 0, 
        max = 1
    )
class TerrainSculptMeshProperties(bpy.types.PropertyGroup):
    
    radius : bpy.props.FloatProperty(
        name = "Radius", 
        description = "Radius of brush.  Use [, ] keys to adjust.", 
        default = 1, 
        min = 0, 
        soft_max = 4
    )
    
    inner_radius : bpy.props.FloatProperty(
        name = "Inner Radius", 
        description = "Inner Radius of brush.  Used for hardness of brush edge.  Use Shift plus [, ] keys to adjust.", 
        default = 0, 
        min = 0, 
        max = 1
    )

    strength : bpy.props.FloatProperty(
        name = "Strength", 
        description = "Strength of brush.", 
        default = 1, 
        min = 0,
        max = 1
    )

    strength_ramp : bpy.props.FloatProperty(
        name = "Ramp Strength", 
        description = "Strength for ramp tool.", 
        default = 1, 
        min = 0,
        soft_max = 1
    )

    use_pressure : bpy.props.BoolProperty(
        name = "Pen Pressure", 
        description = "If true, pen pressure is used to adjust strength.", 
        default = False
    )

    terrain_origin : bpy.props.PointerProperty(
        name = "Terrain Origin", 
        description = "Defines the origin point for modes that depend on a distance from the origin.  World origin used if not set.", 
        type = bpy.types.Object
    )

    brush_type : bpy.props.EnumProperty(
        items=(
            ('DRAW', "Draw (D)", "Draw terrain at the given height above the origin."),
            ('LEVEL', "Level (L)", "Make terrain the same height as the spot where you first place your brush."),
            ('ADD', "Add (A)", "Add to terrain height."),
            ('SUBTRACT', "Subtract (S)", "Subtract from terrain height."),
            ('SLOPE', "Slope (P)", "Use the slope of the surface under the brush to set height."),
            ('SMOOTH', "Smooth (M)", "Average out the terrain under the brush."),
            ('RAMP', "Ramp (R)", "Draw a ramp between where you press and release the mouse."),
        ),
        default='DRAW'
    )

    world_shape_type : bpy.props.EnumProperty(
        items=(
            ('FLAT', "Flat", "Terrain is flat and gravity points along -Z."),
            ('SPHERE', "Sphere", "Terrain is sphere shaped (like a planet) and gravity points toward the origin."),
        ),
        default='FLAT'
    )

    draw_height : bpy.props.FloatProperty(
        name = "Draw Height", 
        description = "Distance above origin to draw terrain.  Use Up, Down arrow to adjust.", 
        default = 1, 
        soft_min = 0,
        soft_max = 100
    )

    add_amount : bpy.props.FloatProperty(
        name = "Add Amount", 
        description = "Amount to add or subtract when those modes are used.", 
        default = 1, 
        soft_min = 0,
        soft_max = 100
    )

    smooth_edge_snap_distance : bpy.props.FloatProperty(
        name = "Smooth Snap Distance", 
        description = "When using the smooth tool with more than one mesh selected, this determines whether vertices in the different meshes are treated as if they're the same vertex.  That is, if the two vertices are less than this distance apart when looking in the 'down' direction, they are treated as if they are connected.", 
        default = .001, 
        min = 0,
        soft_max = .1
    )

    ramp_width : bpy.props.FloatProperty(
        name = "Ramp Width", 
        description = "The width of the ramp.", 
        default = 1, 
        min = 0,
        soft_max = 10
    )
    
    ramp_falloff : bpy.props.FloatProperty(
        name = "Ramp Falloff", 
        description = "Softness of the edge of the ramp.", 
        default = .2, 
        min = 0, 
        max = 1
    )



# def register():

    # #Register tools
    # bpy.utils.register_class(TerrainSculptMeshProperties)
    
    # bpy.types.Scene.terrain_sculpt_mesh_brush_props = bpy.props.PointerProperty(type=TerrainSculptMeshProperties)

# def unregister():
    # bpy.utils.unregister_class(TerrainSculptMeshProperties)
    
    # del bpy.types.Scene.terrain_sculpt_mesh_brush_props
