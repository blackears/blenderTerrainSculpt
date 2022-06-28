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

        
def pick_object(ray_origin, ray_direction):
    hit_object = False
    best_loc = None
    best_normal = None
    best_face_idx = None
    best_obj = None
    best_matrix = None
    best_dist_sq = 0
    
    for obj in bpy.context.selected_objects:
        if obj.hide_select:
            continue
            
        l2w = obj.matrix_world
        w2l = l2w.inverted()
        n2w = w2l.transposed() #normal transform
        l_origin = w2l @ ray_origin
        l_offPt = w2l @ (ray_origin + ray_direction)
        l_direction = l_offPt - l_origin

        #print("testing " + obj.name + " orig " + str(ray_origin) + " dir " + str(ray_direction))
            
        success, location, normal, poly_index = obj.ray_cast(l_origin, l_direction)
        if not success:
            continue

        #print("hit " + obj.name)
                
        dist_sq = (location - l_origin).length_squared
        
        if not hit_object or dist_sq < best_dist_sq:
            hit_object = True
            best_loc = l2w @ location
            best_normal = (n2w @ normal).normalized()
            best_face_idx = poly_index
            best_obj = obj
            best_matrix = l2w
            best_dist_sq = dist_sq
        
    return (hit_object, best_loc, best_normal, best_face_idx, best_obj, best_matrix)

#--------------------------------------

def pick_height(context, event):
    mouse_pos = (event.mouse_region_x, event.mouse_region_y)

    ctx = bpy.context

    region = context.region
    rv3d = context.region_data

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)


    viewlayer = bpy.context.view_layer
    #result, location, normal, index, object, matrix = ray_cast(context, viewlayer, ray_origin, view_vector)

#    hit_object, location, normal, face_index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
    hit_object, location, normal, face_index, object, matrix = pick_object(ray_origin, view_vector)
    
    if hit_object:
        #object.matrix_world @ 
        props = context.scene.terrain_sculpt_mesh_brush_props
        terrain_origin_obj = props.terrain_origin
        world_shape_type = props.world_shape_type
    
        terrain_origin = vecZero.copy()
        if terrain_origin_obj != None:
            terrain_origin = terrain_origin_obj.matrix_world.translation
        
        
        offset = location - terrain_origin
        down = -offset
        
        if world_shape_type == 'FLAT':
            offset = offset.project(vecZ)
            down = -vecZ
            
        len = offset.magnitude
        if offset.dot(down) > 0:
            len = -len
    
        context.scene.terrain_sculpt_mesh_brush_props.draw_height = len
    
    
        context.scene.terrain_sculpt_mesh_brush_props.normal = normal
        redraw_all_viewports(context)


#Find matrix that will rotate Z axis to point along normal
#coord - point in world space
#normal - normal in world space
def calc_vertex_transform_world(pos, norm):
    axis = norm.cross(vecZ)
    if axis.length_squared < .0001:
        axis = mathutils.Vector(vecX)
    else:
        axis.normalize()
    angle = -math.acos(norm.dot(vecZ))
    
    quat = mathutils.Quaternion(axis, angle)
    mR = quat.to_matrix()
    mR.resize_4x4()
    
    mT = mathutils.Matrix.Translation(pos)

    m = mT @ mR
    return m
