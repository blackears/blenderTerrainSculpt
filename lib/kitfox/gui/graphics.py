# This file is part of the Kitfox Blender Common distribution (https://github.com/blackears/blenderCommon).
# Copyright (c) 2021 Mark McKay
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import bpy
import sys
#import mathutils
from mathutils import *
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from ..math.vecmath import *

from enum import Enum


vertices = (
    (0, 0), (1, 0),
    (1, 1), (0, 1))

# vertices = (
    # (100, 100), (300, 100),
    # (100, 200), (300, 200))

# indices = (
    # (0, 1, 2), (2, 1, 3))

shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
#batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
#batch = batch_for_shader(shader, 'TRI_FAN', {"pos": coordsSquare})

#----------------------------------

class DrawContext2D:

    def __init__(self, blender_ctx):
        self.blender_ctx = blender_ctx
        
        self.color = Vector((.5, .5, .5, 1))
        self.font_color = Vector((1, 1, 1, 1))
        self.font_dpi = 20
        self.font_size = 60
        
        self.transform_stack = []
        self.transform_stack.append(Matrix())

    # def set_color(self, color):
        # self.color = color
      
    def set_font_size(self, size):
        self.font_size = size
      
    def set_font_dpi(self, value):
        self.font_dpi = value
      
    def set_font_color(self, value):
        self.font_color = value
      
    def set_color(self, value):
        self.color = value
      
    def coords_to_screen_matrix(self):
        region = self.blender_ctx.region
        #rv3d = context.region_data

        mT = Matrix.Translation((0, region.height, 0))
        mS = Matrix.Diagonal((1, -1, 1, 1))
        return mT @ mS
        
    def push_transform(self):
        m = self.transform_stack[-1].copy()
        self.transform_stack.append(m)
        
    def pop_transform(self):
        self.transform_stack.pop()
        
    def transform_matrix(self):
        return self.transform_stack[-1]
        
    def translate(self, x, y):
        m = self.transform_stack[-1]
        self.transform_stack[-1] = Matrix.Translation(Vector((x, y, 0))) @ m
        
#        print("after translate " + str(self.transform_stack[-1]))
        
    def fill_rectangle(self, x, y, width, height):
        c2s = self.coords_to_screen_matrix()
        
        mXform = self.transform_matrix()
        mT = Matrix.Translation(Vector((x, y, 0)))
        mS = Matrix.Diagonal(Vector((width, height, 1, 1)))

        m = c2s @ mXform @ mT @ mS
        
        gpu.matrix.push()
        
        gpu.matrix.multiply_matrix(m)

        
        shader.bind()
        shader.uniform_float("color", self.color)
        batch.draw(shader)
        
        gpu.matrix.pop()
        
    def fill_round_rectangle(self, x, y, width, height, radius = 0):
        if radius <= 0:
            fill_rectangle(x, y, width, height)
            return
    
        c2s = self.coords_to_screen_matrix()

        max_radius = min(width, height) / 2
        radius = min(radius, max_radius)

        circle_segs = 8
        radian_inc = math.pi / (2 * circle_segs)
        
        verts = []
        
#        print ("+++++r rect")

        verts.append((x, y + radius))
        verts.append((x, y + height - radius))

        for i in range(1, circle_segs):
            xx = radius * math.cos(-radian_inc * i + math.pi) + x + radius 
            yy = radius * math.sin(-radian_inc * i + math.pi) + y + height - radius 
            verts.append((xx, yy))
#            print("v %f %f" % (xx, yy))
        
        verts.append((x + radius, y + height))
        verts.append((x + width - radius, y + height))

        for i in range(1, circle_segs):
            xx = radius * math.cos(-radian_inc * i + math.pi * 1 / 2) + x + width - radius 
            yy = radius * math.sin(-radian_inc * i + math.pi * 1 / 2) + y + height - radius
            verts.append((xx, yy))
        
        verts.append((x + width, y + height - radius))
        verts.append((x + width, y + radius))

        for i in range(1, circle_segs):
            xx = radius * math.cos(-radian_inc * i) + x + width - radius 
            yy = radius * math.sin(-radian_inc * i) + y + radius 
            verts.append((xx, yy))
        
        verts.append((x + width - radius, y))
        verts.append((x + radius, y))

        for i in range(1, circle_segs):
            xx = radius * math.cos(-radian_inc * i + math.pi * 3 / 2) + x + radius 
            yy = radius * math.sin(-radian_inc * i + math.pi * 3 / 2) + y + radius 
            verts.append((xx, yy))
        
        
        # print ("-----")
        # for v in verts:
            # print("v %f %f" % (v[0], v[1]))
        
        batch_rr = batch_for_shader(shader, 'TRI_FAN', {"pos": verts})
        
        
        mXform = self.transform_matrix()
        # mT = Matrix.Translation(Vector((x, y, 0)))
        # mS = Matrix.Diagonal(Vector((width, height, 1, 1)))

#        m = c2s @ mXform @ mT @ mS
        m = c2s @ mXform
        
        gpu.matrix.push()
        
        gpu.matrix.multiply_matrix(m)

        
        shader.bind()
        shader.uniform_float("color", self.color)
        batch_rr.draw(shader)
        
        gpu.matrix.pop()

    def draw_text(self, text, x, y):
        c2s = self.coords_to_screen_matrix()

        mXform = self.transform_matrix()
        
        font_id = 0  # default font
        blf.color(font_id, self.font_color.x, self.font_color.y, self.font_color.z, self.font_color.w)
        blf.size(font_id, self.font_size, self.font_dpi)
#        text_w, text_h = blf.dimensions(font_id, text)
        
        screenPos = c2s @ mXform @ Vector((x, y, 0, 1))
        
        blf.position(font_id, screenPos.x, screenPos.y, 0)
        blf.draw(font_id, text)
        
