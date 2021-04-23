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



circleSegs = 64
coordsCircle = [(math.sin(((2 * math.pi * i) / circleSegs)), math.cos((math.pi * 2 * i) / circleSegs), 0) for i in range(circleSegs + 1)]

coordsNormal = [(0, 0, 0), (0, 0, 1)]

vecZ = mathutils.Vector((0, 0, 1))
vecX = mathutils.Vector((1, 0, 0))

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
batchLine = batch_for_shader(shader, 'LINES', {"pos": coordsNormal})
batchCircle = batch_for_shader(shader, 'LINE_STRIP', {"pos": coordsCircle})

#--------------------------------------

class TerrainSculptMeshProperties(bpy.types.PropertyGroup):
    
    radius : bpy.props.FloatProperty(
        name="Radius", description="Radius of brush", default = 1, min=0, soft_max = 4
    )

    strength : bpy.props.FloatProperty(
        name="Strength", description="Strength of brush", default = 1, min=0, soft_max = 4
    )

    use_pressure : bpy.props.BoolProperty(
        name="Pen Pressure", description="If true, pen pressure is used to adjust strength", default = False
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
#    if True:
#        return

    ctx = bpy.context

    region = context.region
    rv3d = context.region_data

    viewport_center = (region.x + region.width / 2, region.y + region.height / 2)
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, viewport_center)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, viewport_center)


    shader.bind();

    bgl.glEnable(bgl.GL_DEPTH_TEST)

    #Draw cursor
    if self.show_cursor:
        brush_radius = context.scene.uv_brush_props.radius
    
        m = calc_vertex_transform_world(self.cursor_pos, self.cursor_normal);
        mS = mathutils.Matrix.Scale(brush_radius, 4)
        m = m @ mS
    
        #Tangent to mesh
        gpu.matrix.push()
        
        gpu.matrix.multiply_matrix(m)

        shader.uniform_float("color", (1, 0, 1, 1))
        batchCircle.draw(shader)
        
        gpu.matrix.pop()


    bgl.glDisable(bgl.GL_DEPTH_TEST)

    
#-------------------------------------

class TerrainSculptMeshOperator(bpy.types.Operator):
    """Move uvs on your mesh by stroking a brush."""
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


    def dab_brush(self, context, event):
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
            
            self.edit_object = object
            
            self.dab_brush(context, event)
            
            
        elif event.value == "RELEASE":
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
                brush_radius = context.scene.terrain_sculpt_mesh_brush_props.radius
                brush_radius = brush_radius + .1
                context.scene.terrain_sculpt_mesh_brush_props.radius = brush_radius
            return {'RUNNING_MODAL'}

        elif event.type in {'PAGE_DOWN', 'LEFT_BRACKET'}:
            if event.value == "PRESS":
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
        settings = scene.terrain_sculpt_mesh_brush_props
        
#        pcoll = preview_collections["main"]
        
        #--------------------------------
        
        col = layout.column();
        #col.operator("kitfox.terrain_sculpt_mesh_brush_operator", text="Terrain Mesh Brush", icon_value = pcoll["uvBrush"].icon_id)
        col.operator("kitfox.terrain_sculpt_mesh_brush_operator", text="Terrain Brush for Mesh")
        
        col.prop(settings, "radius")
        col.prop(settings, "strength")
        col.prop(settings, "use_pressure")


#---------------------------



def register():

    #Register tools
    bpy.utils.register_class(TerrainSculptMeshProperties)
    bpy.utils.register_class(TerrainSculptMeshOperator)
    bpy.utils.register_class(TerrainSculptMeshBrushPanel)

    bpy.types.Scene.terrain_sculpt_mesh_brush_props = bpy.props.PointerProperty(type=TerrainSculptMeshProperties)

def unregister():
    bpy.utils.unregister_class(TerrainSculptMeshProperties)
    bpy.utils.unregister_class(TerrainSculptMeshOperator)
    bpy.utils.unregister_class(TerrainSculptMeshBrushPanel)

    del bpy.types.Scene.terrain_sculpt_mesh_brush_props


if __name__ == "__main__":
    register()