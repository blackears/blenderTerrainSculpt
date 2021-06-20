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

from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

# import sys
# sys.path.insert(0, '..')
# import kitfox.gui.window
from ..kitfox.gui.window import *
from ..kitfox.gui.textInput import *

# vecZ = mathutils.Vector((0, 0, 1))
# vecX = mathutils.Vector((1, 0, 0))

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
#batchLine = batch_for_shader(shader, 'LINES', {"pos": coordsNormal})
batchCircle = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsCircle})
batchSquare = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsSquare_strip})

brush_radius_increment = .9

#my_window = window.Window()
#my_window = Window()

#--------------------------------------

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

class TerrainSculptMeshWindow(Window):
    def __init__(self):
        super().__init__()
#        self.background_color = mathutils.Vector((.9, .5, .5, 1))
        self.set_title("Terrain Sculpt Properties")
        panel = self.get_main_panel()
        
        main_layout = LayoutBox(axis = Axis.Y)
        panel.set_layout(main_layout)

        
        self.rad_panel = Panel()
        main_layout.add_child(self.rad_panel)
        rad_panel_layout = LayoutBox(Axis.X)
        self.rad_panel.set_layout(rad_panel_layout)
        self.radius_label = Label("Radius: ")
        rad_panel_layout.add_child(self.radius_label)
        self.radius_data = TextInput("0")
        rad_panel_layout.add_child(self.radius_data)
#        self.radius_data.set_background_color(Vector((.7, .7, .7, 1)))
#        self.radius_data.set_border_radius(4)
        self.radius_data.set_expansion_x(ExpansionType.EXPAND)
#        self.radius_data.set_align_x(AlignX.RIGHT)
        
        
        self.layout.layout_components(self.bounds())
        
        self.layout.dump()

    def draw(self, context):
#        props = context.scene.terrain_sculpt_mesh_brush_props
        props = context.scene.terrain_sculpt_mesh_brush_props
        brush_radius = props.radius

        text = "{:.3f}".format(brush_radius)
        self.radius_data.text = text

        super().draw(context)
        


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



def draw_viewport_callback(self, context):
#    print("drawing window")
    # if self.window != None:
        # self.window.draw(context)
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
            m = mathutils.Matrix.Translation(draw_pos)

            draw_base_pos = self.cursor_pos - offset_from_origin
            mBase = mathutils.Matrix.Translation(draw_base_pos)
            
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
        
            #Tangent to mesh
            gpu.matrix.push()
            
            gpu.matrix.multiply_matrix(mCursor)

            shader.uniform_float("color", (1, 0, 1, 1))
            batchCircle.draw(shader)
            gpu.matrix.pop()

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
        
#        self.window = TerrainSculptMeshWindow()

        
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

        hit_object, location, normal, face_index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        
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
        
        if brush_type == 'SMOOTH' or brush_type == 'SLOPE':
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
                        elif brush_type == 'SMOOTH':
                            frac = dist / brush_radius
                            atten = 1 if frac <= inner_radius else (1 - frac) / (1 - inner_radius)
                            atten *= atten
                            
                            len = offset_from_origin.magnitude
                            if offset_from_origin.dot(down) > 0:
                                len = -len
                                
                            weight_sum += atten
                            weighted_len_sum += len * atten

                if obj.mode == 'OBJECT':
                    bm.free()

            if brush_type == 'SLOPE':
                smooth_valid, smooth_plane_pos, smooth_plane_norm = fit_points_to_plane(smooth_points)
                
            elif brush_type == 'SMOOTH':
                if weight_sum == 0:
                    return
                smooth_height = weighted_len_sum / weight_sum



        
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
                            
                        if start_stroke:
                            self.start_height = len

                        # print("---")
                        # print("wpos " + str(wpos))
                        # print("offset_from_origin " + str(offset_from_origin))
                        # print("down " + str(down))
                        # print("len " + str(len))
                        # print("draw_height " + str(draw_height))
                        # print("atten " + str(atten))
                            
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
                            new_offset = (wpos - offset_from_origin) + -down * lerp(len, smooth_height, atten)
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
        result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)
        
        if not result or object.select_get() == False or object.type != 'MESH':
            return

        props = context.scene.terrain_sculpt_mesh_brush_props
        strength_ramp = props.strength_ramp
        ramp_width = props.ramp_width
        ramp_falloff = props.ramp_falloff
        world_shape_type = props.world_shape_type
        terrain_origin_obj = props.terrain_origin

#        print("======")
    
        terrain_origin = vecZero.copy()
        if terrain_origin_obj != None:
            terrain_origin = terrain_origin_obj.matrix_world.translation

            
        ramp_start = self.start_location
        ramp_span = location - self.start_location
    
        # if self.edit_object == None:
            # self.edit_object = object
        
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
        
        # mesh = object.data
        # if object.mode == 'EDIT':
            # bm = bmesh.from_edit_mesh(mesh)
        # elif object.mode == 'OBJECT':
            # bm = bmesh.new()
            # bm.from_mesh(mesh)

            
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
                        
                    # if frac < ramp_falloff:
                        # attenParallel = frac / ramp_falloff
                    # elif frac > 1 - ramp_falloff:
                        # attenParallel = (1 - frac) / ramp_falloff
                        
                    
                    vert_perp_frac = vert_binormal.length / ramp_width
                    attenPerp = 1 if vert_perp_frac < (1 - ramp_falloff) else (1 - vert_perp_frac) / ramp_falloff
                        
                            
                    # len = offset_from_origin.magnitude
                    # if offset_from_origin.dot(down) > 0:
                        # len = -len
                    s = closest_point_to_line(wpos, down, ramp_start, ramp_span)
                    clamped_to_ramp = wpos + down * s
                    newWpos = lerp(wpos, clamped_to_ramp, strength_ramp * attenParallel * attenPerp)

                    ##############################
                    # print(" _ ")
                    # print ("wpos " + str(wpos))
                    # print ("clamped_to_ramp " + str(clamped_to_ramp))
                    # print ("down " + str(down))
                    # print ("s " + str(s))
                    # print ("newWpos " + str(newWpos))
                    
                    ##############################
                
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
        result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)

        props = context.scene.terrain_sculpt_mesh_brush_props
        brush_type = props.brush_type

        if brush_type == 'DRAW' and event.ctrl:
            context.window.cursor_set("EYEDROPPER")
            self.show_cursor = False
#            pick_height(context, event)
            return
            
        context.window.cursor_set("DEFAULT")
        
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
            result, location, normal, index, object, matrix = ray_cast_scene(context, viewlayer, ray_origin, view_vector)

            
            if result == False or object.select_get() == False or object.type != 'MESH':
                return {'RUNNING_MODAL'}
                            
            self.dragging = True
            self.stroke_trail = []
            self.start_location = location.copy()
            
#            self.edit_object = object

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
            
            
#---------------------------

class TerrainHeightPickerMeshOperator(bpy.types.Operator):
    """Pick Terrain Height"""
    bl_idname = "kitfox.terrain_height_picker_mesh"
    bl_label = "Pick Normal"
    bl_options = {"REGISTER", "UNDO"}
    
    def __init__(self):
        self.picking = False

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            if self.picking:
                context.window.cursor_set("EYEDROPPER")
            else:
                context.window.cursor_set("DEFAULT")
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            self.picking = False
#            self.mouse_down(context, event)
            pick_height(context, event)
            context.window.cursor_set("DEFAULT")
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.picking = False
#            print("pick target object cancelled")
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

    # bl_label = "Terrain Sculpt Mesh Brush"
    # bl_idname = "SCENE_PT_terrain_sculpt_mesh_brush"
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "scene"
#    bl_context = "world"
    
        

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
        if props.brush_type == 'RAMP':
            col.prop(props, "strength_ramp")
        else:
            col.prop(props, "strength")
        col.prop(props, "use_pressure")
        col.prop(props, "terrain_origin")
        col.prop(props, "brush_type", expand = True, text = "Brush Type")
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