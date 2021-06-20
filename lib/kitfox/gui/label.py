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

from .graphics import DrawContext2D
from .layout import *
from .panel import *

#----------------------------------

class Label(Panel):
    def __init__(self, text = "label"):
        super().__init__()
        
        self.position = Vector((0, 0))
        self.size = Vector((100, 100))
        self.text = text
        self.margin = Vector((2, 2, 2, 2))
        self.padding = Vector((2, 2, 2, 2))
        
        self.align_x = AlignX.LEFT
        self.align_y = AlignY.TOP

    def set_text(self, value):
        self.text = value

    def set_align_x(self, value):
        self.align_x = value

    def set_align_y(self, value):
        self.align_y = value
        
    def calc_preferred_size(self):
        blf.size(self.font_id, self.font_size, self.font_dpi)
        
        #Use 'My' to estimate font height
        my_w, my_h = blf.dimensions(self.font_id, "My")
        
        text_w, text_h = blf.dimensions(self.font_id, self.text)
        text_h = my_h
        
        w = text_w
        h = text_h

        if self.margin != None:
            w += self.margin[0] + self.margin[2]
            h += self.margin[1] + self.margin[3]
        
        if self.padding != None:
            w += self.padding[0] + self.padding[2]
            h += self.padding[1] + self.padding[3]
        
        return Vector((w, h))

    def draw_component(self, ctx):
#        print("drawing panel")
        super().draw_component(ctx)
    
        blf.size(self.font_id, self.font_size, self.font_dpi)
        text_w, text_h = blf.dimensions(self.font_id, self.text)
        
        bounds = self.bounds()

#        print("bounds " + str(bounds))
        
        if self.align_x == AlignX.LEFT:
            off_x = 0
        elif self.align_x == AlignX.CENTER:
            off_x = (bounds.width - text_w) / 2
        else:
            off_x = bounds.width - text_w

        if self.align_y == AlignY.TOP:
            off_y = 0
        elif self.align_y == AlignY.CENTER:
            off_y = (bounds.height - text_h) / 2
        else:
            off_y = bounds.height - text_h
        
        x = off_x
        y = off_y + text_h
        
        if self.margin != None:
            if self.align_x == AlignX.LEFT:
                x += self.margin[0]
            elif self.align_x == AlignX.RIGHT:
                x -= self.margin[0]
                
            if self.align_y == AlignY.TOP:
                y += self.margin[1]
            elif self.align_y == AlignY.BOTTOM:
                y -= self.margin[1]
        
        if self.padding != None:
            if self.align_x == AlignX.LEFT:
                x += self.padding[0]
            elif self.align_y == AlignX.RIGHT:
                x -= self.padding[0]
                
            if self.align_y == AlignY.TOP:
                y += self.padding[1]
            elif self.align_y == AlignY.BOTTOM:
                y -= self.padding[1]
                
        ctx.set_font_size(self.font_size)
        ctx.set_font_dpi(self.font_dpi)
        ctx.set_font_color(self.font_color)
        ctx.draw_text(self.text, x, y)
