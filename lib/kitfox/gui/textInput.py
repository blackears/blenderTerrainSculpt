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
from .label import *

#----------------------------------

class InputType(Enum):
    DISPLAY = 0
    TEXT_INPUT = 1

#----------------------------------

class TextInput(Label):
    def __init__(self, text = "label"):
        super().__init__(text)

        self.set_background_color(Vector((.7, .7, .7, 1)))
        self.set_border_radius(4)
        self.set_align_x(AlignX.RIGHT)
        
        #index of character cursor is just before
        self.cursor_pos = 0
        self.input_mode = InputType.DISPLAY

    # def handle_event(self, context, event):
        # panel_pos = self.get_screen_position()
        # click_pos = event.
    
        # if event.value == "PRESS":
            # print ("TextInput press")
            
        # return False

    def draw_component(self, ctx):
        super().draw_component(ctx)
        
        if self.input_mode == InputType.TEXT_INPUT:
        
            pass

    def draw_cursor(self, ctx):
        first_part = self.text[self.cursor_pos]
        last_part = self.text[self.cursor_pos:]
    
        blf.size(self.font_id, self.font_size, self.font_dpi)
        text_first_w, text_first_h = blf.dimensions(self.font_id, first_part)
        text_last_w, text_last_h = blf.dimensions(self.font_id, last_part)
        
        
        
        bounds = self.bounds()

    def mouse_pressed(self, event):
        print ("TextINput pressed")
        print("event.pos" + str(event.pos))
        print("event.screen_pos" + str(event.screen_pos))
        return True
        
    def mouse_released(self, event):
        print ("TextINput released")
        print("event.pos" + str(event.pos))
        print("event.screen_pos" + str(event.screen_pos))
        return True
        
    def mouse_moved(self, event):
        return True


