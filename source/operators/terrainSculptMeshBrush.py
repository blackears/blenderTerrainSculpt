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
from .math.vecmath import *
from .blenderUtil import *

from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils



#circleSegs = 64
#coordsCircle = [(math.sin(((2 * math.pi * i) / circleSegs)), math.cos((math.pi * 2 * i) / circleSegs), 0) for i in range(circleSegs + 1)]

#coordsNormal = [(0, 0, 0), (0, 0, 1)]

vecZ = mathutils.Vector((0, 0, 1))
vecX = mathutils.Vector((1, 0, 0))

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
#batchLine = batch_for_shader(shader, 'LINES', {"pos": coordsNormal})
batchCircle = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsCircle})
batchSquare = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsSquare_strip})

#--------------------------------------

class TerrainSculptMeshProperties(bpy.types.PropertyGroup):
    
    radius : bpy.props.FloatProperty(
        name = "Radius", 
        description = "Radius of brush.", 
        default = 1, 
        min = 0, 
        soft_max = 4
    )
    
    inner_radius : bpy.props.FloatProperty(
        name = "Inner Radius", 
        description = "Inner Radius of brush.  Used to calculate hardness of brush edge.", 
        default = 0, 
        min = 0, 
        max = 1
    )

    strength : bpy.props.FloatProperty(
        name = "Strength", 
        description = "Strength of brush.", 
        default = 1, 
        min = 0,
        soft_max = 4
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
            ('DRAW', "Draw", " terrain at the given height above the origin."),
            ('ADD', "Add", "Add to current height."),
            ('SUBTRACT', "Subtract", "Subtract from current height."),
            ('FLATTEN', "Flatten", "Make terrain the same height as the spot where you first place your brush."),
            ('SMOOTH', "Smooth", "Even out the terrain under the brush."),
            ('RAMP', "Ramp", "Draw a ramp between where you press and release the mouse."),
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
        description = "Distance above origin to draw terrain.", 
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

#--------------------------------------


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
                    
        else:
            m = calc_vertex_transform_world(self.cursor_pos, self.cursor_normal);
            
            #outer
            mS = mathutils.Matrix.Scale(brush_radius, 4)
            mCursor = m @ mS
        
            #Tangent to mesh
            gpu.matrix.push()
            
            gpu.matrix.multiply_matrix(mCursor)

            shader.uniform_float("color", (1, 0, 1, 1))
            batchCircle.draw(shader)
            gpu.matrix.pop()

            #inner
            mS = mathutils.Matrix.Scale(brush_radius * inner_radius, 4)
            mCursor = m @ mS
        
            #Tangent to mesh
            gpu.matrix.push()
            
            gpu.matrix.multiply_matrix(mCursor)

            shader.uniform_float("color", (1, 0, 1, 1))
            batchCircle.draw(shader)
            
            gpu.matrix.pop()


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

    def __del__(self):
#        print("destruct UvBrushToolOperator")
        pass


    def dab_brush(self, context, event, start_stroke = False):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        
        region = context.region
        rv3d = context.region_data

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

        viewlayer = bpy.context.view_layer
        
        hit_object = None
        location = None
        normal = None
        index = None

        if self.edit_object == None:
            hit_object, location, normal, face_index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
#            print("<<1>>")
        else:
            l2w = self.edit_object.matrix_world
            w2l = l2w.inverted()
            local_ray_origin = w2l @ ray_origin
#            local_ray_origin = l2w @ ray_origin
#            local_ray_origin = ray_origin.copy()
            local_view_vector = mul_vector(w2l, view_vector)

            # print("l2w " + str(l2w))
            # print("w2l " + str(w2l))
            # print("ray_origin " + str(ray_origin))
            # print("local_ray_origin " + str(local_ray_origin))
            # print("view_vector " + str(view_vector))
            # print("local_view_vector " + str(local_view_vector))
            
#            bpy.ops.object.transform_apply(location = False, rotation = True, scale = True)
        
            if self.edit_object.mode == 'OBJECT':
                hit_object, location, normal, index = self.edit_object.ray_cast(local_ray_origin, local_view_vector)
                object = self.edit_object
                
                location = l2w @ location
                
#                print("<<2>>")
            if self.edit_object.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(self.edit_object.data)
                tree = mathutils.bvhtree.BVHTree.FromBMesh(bm)
                location, normal, index, distance = tree.ray_cast(local_ray_origin, local_view_vector)
                hit_object = location != None
                object = self.edit_object
                
                location = l2w @ location
#                print("<<3>>")

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
    
        terrain_origin = vecZero.copy()
        if terrain_origin_obj != None:
            terrain_origin = terrain_origin_obj.matrix_world.translation
    
#        print("hit_object " + str(hit_object))
       
        if hit_object > 0:
            
            if self.edit_object == None:
                self.edit_object = object
#            print("--------Edit object uvs") 
            
            l2w = object.matrix_world
            # n2w = l2w.copy()
            # n2w.invert()
            # n2w.transpose()
#            print("Foo<<2>>")
            
            mesh = object.data
            if self.edit_object.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(mesh)
            elif self.edit_object.mode == 'OBJECT':
                bm = bmesh.new()
                bm.from_mesh(mesh)

            if brush_type == 'SMOOTH':
                weight_sum = 0
                weighted_len_sum = 0
                
                for v in bm.verts:

                    wpos = l2w @ v.co
                    dist = (wpos - location).magnitude
                    if dist < brush_radius:
                        frac = dist / brush_radius
#                        offset_in_brush = 1 - dist / brush_radius
                        atten = 1 if frac <= inner_radius else (1 - frac) / (1 - inner_radius)
                        
                        atten *= strength
                        if use_pressure:
                            atten *= event.pressure
                        
                        offset_from_origin = wpos - terrain_origin
                        if world_shape_type == 'FLAT':
#                            print("world_shape_type " + str(world_shape_type))
                            offset_from_origin = offset_from_origin.project(vecZ)
                            down = -vecZ
                        else:
                            down = -offset_from_origin.normalized()
                            
                        len = offset_from_origin.magnitude
                        if offset_from_origin.dot(down) > 0:
                            len = -len
                            
                        weight_sum += atten
                        weighted_len_sum += len * atten

                smooth_height = weighted_len_sum / weight_sum

            if brush_type in ('DRAW', 'ADD', 'SUBTRACT', 'FLATTEN', 'SMOOTH'):
            
#                print ("location " + str(location))
                for v in bm.verts:

                    wpos = l2w @ v.co
                    dist = (wpos - location).magnitude
                    if dist < brush_radius:
                        frac = dist / brush_radius
#                        offset_in_brush = 1 - dist / brush_radius
                        atten = 1 if frac <= inner_radius else (1 - frac) / (1 - inner_radius)
                        
                        atten *= strength
                        if use_pressure:
                            atten *= event.pressure
                        
                        offset_from_origin = wpos - terrain_origin
                        if world_shape_type == 'FLAT':
#                            print("world_shape_type " + str(world_shape_type))
                            offset_from_origin = offset_from_origin.project(vecZ)
                            down = -vecZ
                        else:
                            down = -offset_from_origin.normalized()
                            
                        len = offset_from_origin.magnitude
                        if offset_from_origin.dot(down) > 0:
                            len = -len
                            
                        if start_stroke:
                            self.start_height = len
                            
                        if brush_type == 'DRAW':
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, draw_height, atten)
                        elif brush_type == 'ADD':
                            new_offset = (wpos - offset_from_origin) + -down * (len + add_amount * atten)
                        elif brush_type == 'SUBTRACT':
                            new_offset = (wpos - offset_from_origin) + -down * (len - add_amount * atten)
                        elif brush_type == 'FLATTEN':
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, self.start_height, atten)
                        elif brush_type == 'SMOOTH':
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, smooth_height, atten)

                        v.co = w2l @ new_offset
            
                
                

            if self.edit_object.mode == 'EDIT':
                bmesh.update_edit_mesh(mesh)
            elif self.edit_object.mode == 'OBJECT':
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
        result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        
        if not result or object.select_get() == False or object.type != 'MESH':
            return

        props = context.scene.terrain_sculpt_mesh_brush_props
        strength = props.strength
        ramp_width = props.ramp_width
        ramp_falloff = props.ramp_falloff
        world_shape_type = props.world_shape_type
        terrain_origin_obj = props.terrain_origin

    
        terrain_origin = vecZero.copy()
        if terrain_origin_obj != None:
            terrain_origin = terrain_origin_obj.matrix_world.translation

            
        ramp_start = self.start_location
        ramp_span = location - self.start_location
    
        if self.edit_object == None:
            self.edit_object = object
        
        l2w = object.matrix_world
        w2l = l2w.inverted()
        
        mesh = object.data
        if self.edit_object.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(mesh)
        elif self.edit_object.mode == 'OBJECT':
            bm = bmesh.new()
            bm.from_mesh(mesh)

            
        for v in bm.verts:
            wpos = l2w @ v.co
            
            vert_offset = wpos - ramp_start
            vert_parallel = vert_offset.project(ramp_span)
            vert_perp = vert_offset - vert_parallel
            
            if vert_parallel.dot(ramp_span) > 0 and vert_parallel.length_squared < ramp_span.length_squared and vert_perp.length_squared < ramp_width * ramp_width:
                frac = vert_parallel.length / ramp_span.length
                ramp_height = ramp_start + ramp_span * frac
                attenParallel = 1
                if frac < ramp_falloff:
                    attenParallel = frac / ramp_falloff
                elif frac > 1 - ramp_falloff:
                    attenParallel = (1 - frac) / ramp_falloff
                    
                
                vert_perp_frac = vert_perp.length / ramp_width
                attenPerp = 1 if vert_perp_frac < (1 - ramp_falloff) else (1 - vert_perp_frac) / ramp_falloff
                
                if world_shape_type == 'FLAT':
                    down = -vecZ
                else:
                    down = wpos - terrain_origin
                    down.normalize()
                    
#                newWpos = wpos.copy()
#                newWpos.z = lerp(newWpos.z, ramp_height.z, strength * attenParallel * attenPerp)
                
                s = closest_point_to_line(wpos, down, ramp_start, ramp_span)
                clamped_to_ramp = wpos + down * s
                newWpos = lerp(wpos, clamped_to_ramp, strength * attenParallel * attenPerp)
            
                v.co = w2l @ newWpos
            

        if self.edit_object.mode == 'EDIT':
            bmesh.update_edit_mesh(mesh)
        elif self.edit_object.mode == 'OBJECT':
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
        result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        
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
            pass


    def mouse_click(self, context, event):
        if event.value == "PRESS":
            mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            region = context.region
            rv3d = context.region_data

            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

            viewlayer = bpy.context.view_layer
            result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)

            
            if result == False or object.select_get() == False or object.type != 'MESH':
                return {'PASS_THROUGH'}
                            
            self.dragging = True
            self.stroke_trail = []
            self.start_location = location.copy()
            
            self.edit_object = object
            
            self.dab_brush(context, event, start_stroke = True)

            
            
        elif event.value == "RELEASE":
            props = context.scene.terrain_sculpt_mesh_brush_props
            brush_type = props.brush_type
            
            if brush_type == 'RAMP':
                self.draw_ramp(context, event)
        
        
            self.dragging = False
            self.edit_object = None
            
#            self.history_snapshot(context)


        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
        
    def modal(self, context, event):
#        print("modal evTyp:%s evVal:%s" % (str(event.type), str(event.value)))
        context.area.tag_redraw()

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}
        
        elif event.type == 'MOUSEMOVE':
            self.mouse_move(context, event)
            
            if self.dragging:
                return {'RUNNING_MODAL'}
            else:
                return {'PASS_THROUGH'}
            
        elif event.type == 'LEFTMOUSE':
            return self.mouse_click(context, event)

        # elif event.type in {'Z'}:
            # if event.ctrl:
                # if event.shift:
                    # if event.value == "RELEASE":
                        # self.history_redo(context)
                    # return {'RUNNING_MODAL'}
                # else:
                    # if event.value == "RELEASE":
                        # self.history_undo(context)

                    # return {'RUNNING_MODAL'}
                
            # return {'RUNNING_MODAL'}
            
        elif event.type in {'RET'}:
            if event.value == 'RELEASE':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
#                self.history_clear(context)
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
                    brush_radius = brush_radius + .1
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
                    brush_radius = max(brush_radius - .1, .1)
                    context.scene.terrain_sculpt_mesh_brush_props.radius = brush_radius
            return {'RUNNING_MODAL'}
            
        elif event.type == 'ESC':
            if event.value == 'RELEASE':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                self.history_restore_bookmark(context, 0)
                self.history_clear(context)            
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

            redraw_all_viewports(context)
            # self.history_clear(context)
            # self.history_snapshot(context)
            # self.history_snapshot(context, 0)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
#---------------------------

class TerrainHeightPickerMeshOperator(bpy.types.Operator):
    """Pick Terrain Height"""
    bl_idname = "kitfox.terrain_height_picker_mesh"
    bl_label = "Pick Normal"
    bl_options = {"REGISTER", "UNDO"}
    
    def __init__(self):
        self.picking = False

    def mouse_down(self, context, event):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        ctx = bpy.context

        region = context.region
        rv3d = context.region_data

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)


        viewlayer = bpy.context.view_layer
        #result, location, normal, index, object, matrix = ray_cast(context, viewlayer, ray_origin, view_vector)

        hit_object, location, normal, face_index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        
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
        
        
            context.scene.normal_brush_props.normal = normal
            redraw_all_viewports(context)


    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            if self.picking:
                context.window.cursor_set("EYEDROPPER")
            else:
                context.window.cursor_set("DEFAULT")
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            self.picking = False
            self.mouse_down(context, event)
#            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.window.cursor_set("DEFAULT")
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.picking = False
#            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            print("pick target object cancelled")
            context.window.cursor_set("DEFAULT")
            return {'CANCELLED'}
        else:
            return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':

            args = (self, context)
            self._context = context

            context.window_manager.modal_handler_add(self)
            
            context.window.cursor_set("EYEDROPPER")
            self.picking = True
            
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

#---------------------------

class TerrainSculptMeshBrushPanel(bpy.types.Panel):

    """Properties Panel for the Terrain Sculpt Mesh Brush"""
    bl_label = "Terrain Sculpt Mesh Brush"
    bl_idname = "OBJECT_PT_terrain_sculpt_mesh_brush"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Kitfox - Terrain"

        

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj != None and (obj.mode == 'EDIT' or obj.mode == 'OBJECT')
        
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
        col.prop(props, "strength")
        col.prop(props, "use_pressure")
        col.prop(props, "terrain_origin")
        col.prop(props, "brush_type", expand = True)
        col.prop(props, "world_shape_type", text = "Land Shape")
        
        if props.brush_type == 'DRAW':
            col.prop(props, "draw_height")
            col.operator("kitfox.terrain_height_picker_mesh", text="Terrain height picker", icon="EYEDROPPER")
        
        if props.brush_type == 'ADD' or props.brush_type == 'SUBTRACT':
            col.prop(props, "add_amount")
        
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