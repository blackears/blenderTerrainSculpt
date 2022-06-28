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

from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
#batchLine = batch_for_shader(shader, 'LINES', {"pos": coordsNormal})
batchCircle = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsCircle})
batchSquare = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsSquare_strip})

brush_radius_increment = .9

#--------------------------------------

def draw_viewport_callback(self, context):
    pass
    
def draw_circle(mCursor):    
    #Tangent to mesh
    gpu.matrix.push()
    
    gpu.matrix.multiply_matrix(mCursor)

    shader.uniform_float("color", (1, 0, 1, 1))
    batchCircle.draw(shader)
    gpu.matrix.pop()

def draw_callback(self, context):
    ctx = bpy.context

    region = context.region
    rv3d = context.region_data

    viewport_center = (region.x + region.width / 2, region.y + region.height / 2)
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, viewport_center)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, viewport_center)

    props = context.scene.terrain_sculpt_mesh_brush_props
    brush_radius = props.radius
    inner_radius = props.inner_radius
    brush_type = props.brush_type
    ramp_width = props.ramp_width
    draw_height = props.draw_height
    world_shape_type = props.world_shape_type
    terrain_origin_obj = props.terrain_origin

    terrain_origin = vecZero.copy()
    if terrain_origin_obj != None:
        terrain_origin = terrain_origin_obj.matrix_world.translation

    shader.bind();

    bgl.glEnable(bgl.GL_DEPTH_TEST)

    #Draw cursor
    if self.show_cursor:

        if brush_type == 'RAMP':
            if self.dragging:
                ramp_start = self.start_location
                ramp_span = self.cursor_pos - ramp_start
                
                if ramp_span.length_squared > .001:

                    if world_shape_type == 'FLAT':
                        up = vecZ
                    else:
                        up = self.start_location - terrain_origin
                        up.normalize()
                                        
                    binormal = ramp_span.normalized()
                    tangent = binormal.cross(up)
                    normal = tangent.cross(binormal)
                    
                    m = create_matrix(tangent, binormal, normal, self.start_location)

                    #m = calc_vertex_transform_world(self.start_location, normal);
                    mS = mathutils.Matrix.Diagonal((ramp_width * 2, ramp_span.length, 1, 1))
                    mT = mathutils.Matrix.Translation((-.5, 0, 0))
                    
                    mCursor = m @ mS @ mT
                    
                    
                    gpu.matrix.push()
                    
                    gpu.matrix.multiply_matrix(mCursor)

                    shader.uniform_float("color", (1, 0, 1, 1))
                    batchSquare.draw(shader)
                    gpu.matrix.pop()
                    
        elif brush_type == 'DRAW':
        
            offset_from_origin = self.cursor_pos - terrain_origin
            if world_shape_type == 'FLAT':
#                            print("world_shape_type " + str(world_shape_type))
                offset_from_origin = offset_from_origin.project(vecZ)
                down = -vecZ
            else:
                down = -offset_from_origin.normalized()
                
            draw_pos = self.cursor_pos - offset_from_origin - down * draw_height
#            m = mathutils.Matrix.Translation(draw_pos)
            m = calc_vertex_transform_world(draw_pos, -down);

            draw_base_pos = self.cursor_pos - offset_from_origin
#            mBase = mathutils.Matrix.Translation(draw_base_pos)
            mBase = calc_vertex_transform_world(draw_base_pos, -down);
            
            #outer
            mS = mathutils.Matrix.Scale(brush_radius, 4)
            mCursor = m @ mS
        
            draw_circle(mCursor)
            
            draw_circle(mBase @ mS)
            #Tangent to mesh
            # gpu.matrix.push()
            
            # gpu.matrix.multiply_matrix(mCursor)

            # shader.uniform_float("color", (1, 0, 1, 1))
            # batchCircle.draw(shader)
            # gpu.matrix.pop()

            #inner
            mS = mathutils.Matrix.Scale(brush_radius * inner_radius, 4)
            mCursor = m @ mS
        
            draw_circle(mCursor)
            draw_circle(mBase @ mS)
            #Tangent to mesh
            # gpu.matrix.push()
            
            # gpu.matrix.multiply_matrix(mCursor)

            # shader.uniform_float("color", (1, 0, 1, 1))
            # batchCircle.draw(shader)
            
            # gpu.matrix.pop()
        
        else:
            #Orient to mesh surface
            m = calc_vertex_transform_world(self.cursor_pos, self.cursor_normal);
            
            #outer
            mS = mathutils.Matrix.Scale(brush_radius, 4)
            mCursor = m @ mS

            draw_circle(mCursor)
        
            #Tangent to mesh
            # gpu.matrix.push()
            
            # gpu.matrix.multiply_matrix(mCursor)

            # shader.uniform_float("color", (1, 0, 1, 1))
            # batchCircle.draw(shader)
            # gpu.matrix.pop()

            #inner
            mS = mathutils.Matrix.Scale(brush_radius * inner_radius, 4)
            mCursor = m @ mS
            
            draw_circle(mCursor)
        
            #Tangent to mesh
            # gpu.matrix.push()
            
            # gpu.matrix.multiply_matrix(mCursor)

            # shader.uniform_float("color", (1, 0, 1, 1))
            # batchCircle.draw(shader)
            
            # gpu.matrix.pop()


    bgl.glDisable(bgl.GL_DEPTH_TEST)

    
#-------------------------------------

class TerrainSculptMeshOperator(bpy.types.Operator):
    """Sculpt your terrain using a brush."""
    bl_idname = "kitfox.terrain_sculpt_mesh_brush_operator"
    bl_label = "UV Brush"
    bl_options = {"REGISTER", "UNDO"}

    def __init__(self):
        self.dragging = False
        
        self.cursor_pos = None
        self.show_cursor = False
        self.edit_object = None
        self.stroke_trail = []

        self.history = []
        self.history_idx = -1
        self.history_limit = 10
        self.history_bookmarks = {}

        
    def free_snapshot(self, map):
        for obj in map:
            bm = map[obj]
            bm.free()

    #if bookmark is other than -1, snapshot added to bookmark library rather than undo stack
    def history_snapshot(self, context, bookmark = -1):
        map = {}
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bm = bmesh.new()
                
                mesh = obj.data
                bm.from_mesh(mesh)
                map[obj] = bm
                
        if bookmark != -1:
            self.history_bookmarks[bookmark] = map
                
        else:
            #Remove first element if history queue is maxed out
            if self.history_idx == self.history_limit:
                self.free_snapshot(self.history[0])
                self.history.pop(0)
            
                self.history_idx += 1

            #Remove all history past current pointer
            while self.history_idx < len(self.history) - 1:
                self.free_snapshot(self.history[-1])
                self.history.pop()
                    
            self.history.append(map)
            self.history_idx += 1
        
    def history_undo(self, context):
        if (self.history_idx == 0):
            return
            
        self.history_undo_to_snapshot(context, self.history_idx - 1)
                
    def history_redo(self, context):
        if (self.history_idx == len(self.history) - 1):
            return

        self.history_undo_to_snapshot(context, self.history_idx + 1)
            
        
    def history_restore_bookmark(self, context, bookmark):
        map = self.history[bookmark]
    
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bm = map[obj]
                
                mesh = obj.data
                bm.to_mesh(mesh)
                mesh.update()
        
    def history_undo_to_snapshot(self, context, idx):
        if idx < 0 or idx >= len(self.history):
            return
            
        self.history_idx = idx
       
        map = self.history[self.history_idx]
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bm = map[obj]
                
                mesh = obj.data
                bm.to_mesh(mesh)
                mesh.update()
        
    def history_clear(self, context):
        for key in self.history_bookmarks:
            map = self.history_bookmarks[key]
            self.free_snapshot(map)
    
        for map in self.history:
            self.free_snapshot(map)
                
        self.history = []
        self.history_idx = -1

    def stroke_falloff(self, x):
#        return 1 - x * x
        return -x * x + 2 * x
        
    def calc_offset_from_origin(self, wpos, terrain_origin, world_shape_type):
        offset_from_origin = wpos - terrain_origin
        if world_shape_type == 'FLAT':
            offset_from_origin = offset_from_origin.project(vecZ)
            down = -vecZ
        else:
            down = -offset_from_origin.normalized()
                        
        return (offset_from_origin, down)

    def dab_brush(self, context, event, start_stroke = False):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        
        region = context.region
        rv3d = context.region_data

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

#        print("dab_brush " + " mouse_pos " + str(mouse_pos))
#        print("ray_orig " + str(ray_origin) + "view_vec " + str(view_vector))

        viewlayer = bpy.context.view_layer
        
        hit_object = None
        location = None
        normal = None
        index = None

#        hit_object, location, normal, face_index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        hit_object, location, normal, face_index, object, matrix = pick_object(ray_origin, view_vector)
        
        if not hit_object or object.select_get() == False or object.type != 'MESH':
            return
        
        props = context.scene.terrain_sculpt_mesh_brush_props
        brush_radius = props.radius
        inner_radius = props.inner_radius
        strength = props.strength
        use_pressure = props.use_pressure
        brush_type = props.brush_type
        world_shape_type = props.world_shape_type
        draw_height = props.draw_height
        add_amount = props.add_amount
        ramp_width = props.ramp_width
        terrain_origin_obj = props.terrain_origin
        smooth_edge_snap_distance = props.smooth_edge_snap_distance
    
    
        terrain_origin = vecZero.copy()
        if terrain_origin_obj != None:
            terrain_origin = terrain_origin_obj.matrix_world.translation
    
        if event.shift:
            #Shift key overrides for smooth mode
            brush_type = 'SMOOTH'


        if world_shape_type == 'FLAT':
            hit_down = -vecZ
            hit_offset = (location - terrain_origin).project(vecZ)
        else:
            hit_down = terrain_origin - location
            hit_offset = -hit_down
    
        if start_stroke:
            self.start_height = hit_offset.dot(vecZ)

        if brush_type == 'SMOOTH':
            #Calculate relaxed location for each relevant point

            smoothing_info = SmoothingInfo()
            
            for obj in context.scene.objects:
                if not obj.select_get():
                    continue

                if obj.type != 'MESH':
                    continue
                    
                l2w = obj.matrix_world
            
                #Bounding box check
                bounds = mesh_bounds_fast(obj)
                bbox_check = bounds.intersect_with_ray(location, hit_down, brush_radius, l2w)
                if not bbox_check:
                    continue
                
                mesh = obj.data
                if obj.mode == 'EDIT':
                    bm = bmesh.from_edit_mesh(mesh)
                elif obj.mode == 'OBJECT':
                    bm = bmesh.new()
                    bm.from_mesh(mesh)
            
                for v in bm.verts:
                    wpos = l2w @ v.co
                    
                    offset_from_origin, down = self.calc_offset_from_origin(wpos, terrain_origin, world_shape_type)
                    
                    # offset_from_origin = wpos - terrain_origin
                    # if world_shape_type == 'FLAT':
    # #                            print("world_shape_type " + str(world_shape_type))
                        # offset_from_origin = offset_from_origin.project(vecZ)
                        # down = -vecZ
                    # else:
                        # down = -offset_from_origin.normalized()
                        
                    offset = wpos - location
                    offset_parallel = offset.project(down)
                    offset_perp = offset - offset_parallel
                        
                    dist = offset_perp.magnitude
                    if dist < brush_radius:
                        centroidHeight = 0
                        count = 0
#                        print("Smoothing Vertex #" + str(v.index))
                    
                        for e in v.link_edges:
                            v1 = e.other_vert(v)
#                            print("linked edge #" + str(v1.index))
                            
                            v1Wpos = l2w @ v1.co 
                            offset_from_originP, downP = self.calc_offset_from_origin(v1Wpos, terrain_origin, world_shape_type)
                            #offset_parallel = offset.project(down)

#                            print("offset_from_originP.magnitude " + str(offset_from_originP.magnitude))
                            
                            offset = offset_from_originP.magnitude
                            if offset_from_originP.dot(downP) < 0:
                                offset = -offset
                            centroidHeight += offset
                            count += 1
                            #offset = (v1Wpos - wpos).normalized()
                            
                        centroidHeight /= count
                        smoothing_info.addPoint(wpos, centroidHeight)
                    
#                        print("centroidHeight " + str(centroidHeight))
                    
                if obj.mode == 'OBJECT':
                    bm.free()

#        if brush_type == 'SMOOTH' or brush_type == 'SLOPE':
        if brush_type == 'SLOPE':
            weight_sum = 0
            weighted_len_sum = 0
                
            for obj in context.scene.objects:
                if not obj.select_get():
                    continue

                if obj.type != 'MESH':
                    continue
                    
                l2w = obj.matrix_world
            
                #Bounding box check
                bounds = mesh_bounds_fast(obj)
                bbox_check = bounds.intersect_with_ray(location, hit_down, brush_radius, l2w)
                if not bbox_check:
                    continue
                
                mesh = obj.data
                if obj.mode == 'EDIT':
                    bm = bmesh.from_edit_mesh(mesh)
                elif obj.mode == 'OBJECT':
                    bm = bmesh.new()
                    bm.from_mesh(mesh)

                smooth_points = []

                for v in bm.verts:

                    wpos = l2w @ v.co
                    
                    offset_from_origin = wpos - terrain_origin
                    if world_shape_type == 'FLAT':
    #                            print("world_shape_type " + str(world_shape_type))
                        offset_from_origin = offset_from_origin.project(vecZ)
                        down = -vecZ
                    else:
                        down = -offset_from_origin.normalized()
                        
                    offset = wpos - location
                    offset_parallel = offset.project(down)
                    offset_perp = offset - offset_parallel
                        
                    dist = offset_perp.magnitude
                    if dist < brush_radius:
                        if brush_type == 'SLOPE':
                            smooth_points.append(wpos)

                if obj.mode == 'OBJECT':
                    bm.free()

            if brush_type == 'SLOPE':
                smooth_valid, smooth_plane_pos, smooth_plane_norm = fit_points_to_plane(smooth_points)
                



        
        for obj in context.scene.objects:
            if not obj.select_get():
                continue
            
            l2w = obj.matrix_world
            w2l = l2w.inverted()

            if obj.type != 'MESH':
                continue

            #Bounding box check
            bounds = mesh_bounds_fast(obj)
            bbox_check = bounds.intersect_with_ray(location, hit_down, brush_radius, l2w)
#            print("bbox_check " + str(bbox_check))
            if not bbox_check:
                continue

#            print("=====")
#            print ("obj.name " + str(obj.name))

            if brush_type in ('DRAW', 'ADD', 'SUBTRACT', 'LEVEL', 'SLOPE', 'SMOOTH'):
            
                mesh = obj.data
                if obj.mode == 'EDIT':
                    bm = bmesh.from_edit_mesh(mesh)
                elif obj.mode == 'OBJECT':
                    bm = bmesh.new()
                    bm.from_mesh(mesh)

            
    #                print ("location " + str(location))
                for v in bm.verts:

                    wpos = l2w @ v.co
                    woffset = wpos - location
                        
                    offset_from_origin = wpos - terrain_origin
                    if world_shape_type == 'FLAT':
#                            print("world_shape_type " + str(world_shape_type))
                        offset_from_origin = offset_from_origin.project(vecZ)
                        down = -vecZ
                    else:
                        down = -offset_from_origin.normalized()
                    
                    offset_down = woffset.project(down)
                    offset_perp = woffset - offset_down
                    
                    dist_sq = offset_perp.dot(offset_perp)
                    
                    if dist_sq < brush_radius * brush_radius:
                        dist = math.sqrt(dist_sq)
                        frac = dist / brush_radius
    #                        offset_in_brush = 1 - dist / brush_radius
                        atten = 1 if frac <= inner_radius else (1 - frac) / (1 - inner_radius)
                        atten = self.stroke_falloff(atten)
                        
                        atten *= strength
                        if use_pressure:
                            atten *= event.pressure
                            
                            
                        len = offset_from_origin.magnitude
                        if offset_from_origin.dot(down) > 0:
                            len = -len
                            
                        # print("---")
                        # print("wpos " + str(wpos))
                        # print("offset_from_origin " + str(offset_from_origin))
                        # print("down " + str(down))
                        # print("len " + str(len))
                        # print("draw_height " + str(draw_height))
                        # print("atten " + str(atten))
                        # print("smooth_plane_pos " + str(smooth_plane_pos))
                        # print("smooth_plane_norm " + str(smooth_plane_norm))
                            
                        if brush_type == 'DRAW':
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, draw_height, atten)
                        elif brush_type == 'ADD':
                            adjust = add_amount * atten
                            if event.ctrl:
                                adjust = -adjust
                            new_offset = (wpos - offset_from_origin) + -down * (len + adjust)
                        elif brush_type == 'SUBTRACT':
                            adjust = add_amount * atten
                            if event.ctrl:
                                adjust = -adjust
                            new_offset = (wpos - offset_from_origin) + -down * (len - adjust)
                        elif brush_type == 'LEVEL':
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, self.start_height, atten)
                        elif brush_type == 'SMOOTH':                        
                            centroid_height = smoothing_info.getCentroidHeight(wpos, terrain_origin, world_shape_type, smooth_edge_snap_distance)
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, -centroid_height, atten)
                            # print("Applying smooth dab")
                            # print("len " + str(len))
                            # print("centroid_height " + str(centroid_height))
#                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, smooth_height, atten)
                        elif brush_type == 'SLOPE':
                            if smooth_valid:
                                s = isect_line_plane(wpos, down, smooth_plane_pos, smooth_plane_norm)
                                target = wpos + s * down
                                new_offset = Vector(lerp(wpos, target, atten))
                            else:
                                new_offset = wpos

                        v.co = w2l @ new_offset
            
                
                
                if obj.mode == 'EDIT':
                    bmesh.update_edit_mesh(mesh)
                elif obj.mode == 'OBJECT':
                    bm.to_mesh(mesh)
                    bm.free()
                
                mesh.calc_normals()


    def draw_ramp(self, context, event):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        region = context.region
        rv3d = context.region_data

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

        viewlayer = bpy.context.view_layer
        result, location, normal, face_index, object, matrix = pick_object(ray_origin, view_vector)
        
        if not result or object.select_get() == False or object.type != 'MESH':
            return

        props = context.scene.terrain_sculpt_mesh_brush_props
        strength_ramp = props.strength_ramp
        ramp_width = props.ramp_width
        ramp_falloff = props.ramp_falloff
        world_shape_type = props.world_shape_type
        terrain_origin_obj = props.terrain_origin

        terrain_origin = vecZero.copy()
        if terrain_origin_obj != None:
            terrain_origin = terrain_origin_obj.matrix_world.translation

            
        ramp_start = self.start_location
        ramp_span = location - self.start_location
    
        l2w = object.matrix_world
        w2l = l2w.inverted()

        
        for obj in context.scene.objects:
            if not obj.select_get():
                continue

            if obj.type != 'MESH':
                continue
            
            l2w = obj.matrix_world
            w2l = l2w.inverted()
            
            mesh = obj.data
            if obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(mesh)
            elif obj.mode == 'OBJECT':
                bm = bmesh.new()
                bm.from_mesh(mesh)
        
            
            for v in bm.verts:
                wpos = l2w @ v.co
                
                vert_offset = wpos - ramp_start
                vert_parallel = vert_offset.project(ramp_span)
                vert_perp = vert_offset - vert_parallel
                
                offset_from_origin = wpos - terrain_origin
                if world_shape_type == 'FLAT':
                    offset_from_origin = offset_from_origin.project(vecZ)
                    down = -vecZ
                else:
                    down = -offset_from_origin.normalized()
                    
                binormal = down.cross(ramp_span)
                binormal.normalize()
                vert_binormal = vert_offset.project(binormal)
                
                # if vert_parallel.dot(ramp_span) > 0 and vert_parallel.length_squared < ramp_span.length_squared and vert_perp.length_squared < ramp_width * ramp_width:
                if vert_parallel.dot(ramp_span) > 0 and vert_parallel.length_squared < ramp_span.length_squared and vert_binormal.length_squared < ramp_width * ramp_width:
                    frac = vert_parallel.length / ramp_span.length
                    ramp_height = ramp_start + ramp_span * frac
                    falloff_span = ramp_width * ramp_falloff
                    
                    vert_parallel_len = vert_parallel.length
                    vert_parallel_len = min(vert_parallel_len, ramp_span.length - vert_parallel_len)
                    
                    attenParallel = 1
                    if vert_parallel_len < falloff_span:
                        attenParallel = vert_parallel_len / falloff_span
                    
                    vert_perp_frac = vert_binormal.length / ramp_width
                    attenPerp = 1 if vert_perp_frac < (1 - ramp_falloff) else (1 - vert_perp_frac) / ramp_falloff
                        
                            
                    s = closest_point_to_line(wpos, down, ramp_start, ramp_span)
                    clamped_to_ramp = wpos + down * s
                    newWpos = lerp(wpos, clamped_to_ramp, strength_ramp * attenParallel * attenPerp)
                
                    v.co = w2l @ newWpos
                

            if obj.mode == 'EDIT':
                bmesh.update_edit_mesh(mesh)
            elif obj.mode == 'OBJECT':
                bm.to_mesh(mesh)
                bm.free()
                
            mesh.calc_normals()


                    
    def mouse_move(self, context, event):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        ctx = bpy.context

        region = context.region
        rv3d = context.region_data

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

        viewlayer = bpy.context.view_layer
#        result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        result, location, normal, index, object, matrix = pick_object(ray_origin, view_vector)

        props = context.scene.terrain_sculpt_mesh_brush_props
        brush_type = props.brush_type

        if brush_type == 'DRAW' and event.ctrl:
            context.window.cursor_set("EYEDROPPER")
            self.show_cursor = False
            return
            
        context.window.cursor_set("PAINT_BRUSH")
        
        #Brush cursor display
        if result:
            self.show_cursor = True
            self.cursor_pos = location
            self.cursor_normal = normal
            self.cursor_object = object
            self.cursor_matrix = matrix
        else:
            self.show_cursor = False

        if self.dragging:
            self.dab_brush(context, event)


    def mouse_click(self, context, event):
        if event.value == "PRESS":
            mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            region = context.region
            rv3d = context.region_data

            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

            viewlayer = bpy.context.view_layer
#            result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
            result, location, normal, index, object, matrix = pick_object(ray_origin, view_vector)

            
            if result == False or object.select_get() == False or object.type != 'MESH':
                return {'RUNNING_MODAL'}
                            
            self.dragging = True
            self.stroke_trail = []
            self.start_location = location.copy()

            props = context.scene.terrain_sculpt_mesh_brush_props
            brush_type = props.brush_type
    
            if brush_type == 'DRAW' and event.ctrl:
                context.window.cursor_set("EYEDROPPER")
                pick_height(context, event)
                return {'RUNNING_MODAL'}

            context.window.cursor_set("DEFAULT")
        
            self.dab_brush(context, event, start_stroke = True)

            
            
        elif event.value == "RELEASE":
            props = context.scene.terrain_sculpt_mesh_brush_props
            brush_type = props.brush_type
            
            if brush_type == 'RAMP':
                self.draw_ramp(context, event)
        
        
            self.dragging = False
#            self.edit_object = None
            
            self.history_snapshot(context)
            context.window.cursor_set("DEFAULT")


        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
        
    def modal(self, context, event):
#        print("modal evTyp:%s evVal:%s" % (str(event.type), str(event.value)))
        context.area.tag_redraw()
        
        
        # window_result = self.window.handle_event(context, event)
# #        print ("window_result " + str(window_result))
        
        # if window_result:
            # return {'RUNNING_MODAL'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}
        
        elif event.type == 'MOUSEMOVE':
            #context.window.cursor_set("PAINT_BRUSH")
            self.mouse_move(context, event)
            
            if self.dragging:
                return {'RUNNING_MODAL'}
            else:
                return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFTMOUSE':
            return self.mouse_click(context, event)

        elif event.type in {'Z'}:
            if event.ctrl:
                if event.shift:
                    if event.value == "RELEASE":
                        self.history_redo(context)
                    return {'RUNNING_MODAL'}
                else:
                    if event.value == "RELEASE":
                        self.history_undo(context)

                    return {'RUNNING_MODAL'}
                
            return {'RUNNING_MODAL'}
            
        elif event.type in {'RET'}:
            if event.value == 'RELEASE':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_viewport, 'WINDOW')
                self.history_clear(context)
                bpy.context.window.cursor_set("DEFAULT")
                return {'FINISHED'}
            return {'RUNNING_MODAL'}

        elif event.type in {'PAGE_UP', 'RIGHT_BRACKET'}:
            if event.value == "PRESS":
                if event.shift:
                    brush_radius = context.scene.terrain_sculpt_mesh_brush_props.inner_radius
                    brush_radius = brush_radius + .1
                    context.scene.terrain_sculpt_mesh_brush_props.inner_radius = brush_radius
                else:
                    brush_radius = context.scene.terrain_sculpt_mesh_brush_props.radius
#                    brush_radius = brush_radius + .1
                    brush_radius /= brush_radius_increment
                    context.scene.terrain_sculpt_mesh_brush_props.radius = brush_radius
            return {'RUNNING_MODAL'}

        elif event.type in {'PAGE_DOWN', 'LEFT_BRACKET'}:
            if event.value == "PRESS":
                if event.shift:
                    brush_radius = context.scene.terrain_sculpt_mesh_brush_props.inner_radius
                    brush_radius = max(brush_radius - .1, .1)
                    context.scene.terrain_sculpt_mesh_brush_props.inner_radius = brush_radius
                else:
                    brush_radius = context.scene.terrain_sculpt_mesh_brush_props.radius
#                    brush_radius = max(brush_radius - .1, .1)
                    brush_radius *= brush_radius_increment
                    context.scene.terrain_sculpt_mesh_brush_props.radius = brush_radius
            return {'RUNNING_MODAL'}

        elif event.type in {'UP_ARROW'}:
            if event.value == "PRESS":
                brush_radius = context.scene.terrain_sculpt_mesh_brush_props.radius
                draw_height = context.scene.terrain_sculpt_mesh_brush_props.draw_height
                draw_height += brush_radius / 4
                context.scene.terrain_sculpt_mesh_brush_props.draw_height = draw_height
            return {'RUNNING_MODAL'}

        elif event.type in {'DOWN_ARROW'}:
            if event.value == "PRESS":
                brush_radius = context.scene.terrain_sculpt_mesh_brush_props.radius
                draw_height = context.scene.terrain_sculpt_mesh_brush_props.draw_height
                draw_height -= brush_radius / 4
                context.scene.terrain_sculpt_mesh_brush_props.draw_height = draw_height
            return {'RUNNING_MODAL'}

        elif event.type in {'D'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'DRAW'
            return {'RUNNING_MODAL'}

        elif event.type in {'L'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'LEVEL'
            return {'RUNNING_MODAL'}

        elif event.type in {'A'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'ADD'
            return {'RUNNING_MODAL'}

        elif event.type in {'S'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'SUBTRACT'
            return {'RUNNING_MODAL'}

        elif event.type in {'P'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'SLOPE'
            return {'RUNNING_MODAL'}

        elif event.type in {'M'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'SMOOTH'
            return {'RUNNING_MODAL'}

        elif event.type in {'R'}:
            if event.value == "PRESS":
                context.scene.terrain_sculpt_mesh_brush_props.brush_type = 'RAMP'
            return {'RUNNING_MODAL'}
            
        elif event.type == 'ESC':
            if event.value == 'RELEASE':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_viewport, 'WINDOW')
                self.history_restore_bookmark(context, 0)
                self.history_clear(context)            
                bpy.context.window.cursor_set("DEFAULT")
                return {'CANCELLED'}
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

#    def execute(self, context):
#        print("execute SimpleOperator")
#        return {'FINISHED'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
    #        print("invoke evTyp:%s evVal:%s" % (str(event.type), str(event.value)))

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_VIEW')
            self._handle_viewport = bpy.types.SpaceView3D.draw_handler_add(draw_viewport_callback, args, 'WINDOW', 'POST_PIXEL')

            bpy.context.window.cursor_set("PAINT_BRUSH")

            redraw_all_viewports(context)
            self.history_clear(context)
            self.history_snapshot(context)
            self.history_snapshot(context, 0)

            context.window_manager.modal_handler_add(self)
            context.area.tag_redraw()
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
            

        

