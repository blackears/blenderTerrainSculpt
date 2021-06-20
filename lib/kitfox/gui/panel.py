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



#----------------------------------

class AlignX(Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

#----------------------------------

class AlignY(Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3

            
#----------------------------------

class Panel:
    def __init__(self):
        self.parent_layout = None
        self.background_color = None
        self.border_radius = 0
        self.border_color = None
        self.border_width = 1
#        self.background_color = Vector((.5, .5, .5, 1))
        
        self.font_color = Vector((1, 1, 1, 1))
        self.font_dpi = 20
        self.font_size = 50
        self.font_id = 0
        
        self.margin = None
        self.padding = None
        self.layout = None
        self.size = Vector((0, 0))
        self.maximum_size = Vector((sys.maxsize, sys.maxsize))
        self.minimum_size = Vector((0, 0))
        self.preferred_size = Vector((0, 0))
        self.expansion_type_x = ExpansionType.PREFERRED
        self.expansion_type_y = ExpansionType.PREFERRED
        
        self.position = Vector((0, 0))

    def dump(self, indent = ""):
        print(indent + "Panel " + str(self.bounds()))
        if self.layout != None:
            self.layout.dump(indent + " ")
      
    def get_parent_layout(self):
        return self.parent_layout
      
    def set_parent_layout(self, value):
        self.parent_layout = value
      
    def set_expansion_x(self, value):
        self.expansion_type_x = value
      
    def set_expansion_y(self, value):
        self.expansion_type_y = value
      
    def set_background_color(self, value):
        self.background_color = value
      
    def set_border_color(self, value):
        self.border_color = value
      
    def set_border_radius(self, value):
        self.border_radius = value
      
    def set_border_width(self, value):
        self.border_width = value
      
    def set_font_size(self, size):
        self.font_size = size
      
    def set_font_dpi(self, value):
        self.font_dpi = value
      
    def set_font_color(self, value):
        self.font_color = value

    def layout_components(self):
        if self.layout != None:
            self.layout.layout_components(self.bounds())
        
    def set_layout(self, layout):
        self.layout = layout
        layout.set_parent(self)
        
    def bounds(self):
        return Rectangle2D(self.position.x, self.position.y, self.size.x, self.size.y)
        
    def bounds_world(self):
        if parent_layout != None:
            window = parent_layout.get_window()
            if window != None:
                pass
            
            parent = parent_layout.get_parent()
            if parent != None:
                parent.position
        return Rectangle2D(self.position.x, self.position.y, self.size.x, self.size.y)
        
    def calc_minimum_size(self):
#        print("calc_minimum_size")
    
        if self.layout != None:
            layout_size = self.layout.calc_minimum_size()
#            print("layout_size " + str(layout_size))
            return Vector((max(layout_size.x, self.minimum_size.x), max(layout_size.y, self.minimum_size.y)))
#            print("layout_size " + str(layout_size))
            
        else:    
            return self.minimum_size
    
    def calc_preferred_size(self):
        if self.layout != None:
            layout_size = self.layout.calc_preferred_size()
            return Vector((max(layout_size.x, self.preferred_size.x), max(layout_size.y, self.preferred_size.y)))
            
        else:    
            return self.preferred_size
    
    def calc_maximum_size(self):
        if self.layout != None:
            layout_size = self.layout.calc_maximum_size()
            return Vector((max(layout_size.x, self.maximum_size.x), max(layout_size.y, self.maximum_size.y)))
            
        else:    
            return self.maximum_size

    def draw(self, ctx):
        ctx.push_transform()
        ctx.translate(self.position.x, self.position.y)
        
        self.draw_component(ctx)
        
        if self.layout != None:
            self.layout.draw(ctx)
        
        ctx.pop_transform()

    def draw_component(self, ctx):
        if self.background_color != None:
            x = 0
            y = 0
            w = self.size[0]
            h = self.size[1]
            
            if self.margin != None:
                x += self.margin[0]
                y += self.margin[1]
                w -= self.margin[0] + self.margin[2]
                h -= self.margin[1] + self.margin[3]
                
            # if self.padding != None:
                # x -= self.padding[0] + self.padding[2]
                # y -= self.padding[1] + self.padding[3]
                
            ctx.set_color(self.background_color)
            ctx.fill_round_rectangle(x, y, w, h, self.border_radius)

    def handle_event_dispatch(self, context, event):
        if self.layout != None:
            result = self.layout.handle_event(context_event)
            if result:
                return True
                
        return handle_event(context, event)

    # def handle_event(self, context, event):
        # return False

    def get_screen_position(self):
        pos = self.position.copy()
    
        if self.parent_layout != None:
            pos += self.parent_layout.get_screen_position()

        return pos
        
    def get_parent_panel():
        if self.parent_layout != None:
            return self.parnt_layout.get_parent()
        return None

    #Get the child panel that exists at the given position
    def pick_panel_stack(self, pos):
        if self.layout != None:
            return self.layout.pick_panel_stack(pos)
            
        return []
    

    def mouse_pressed(self, event):
        # if self.layout != None:
            # result = self.layout.mouse_pressed(event)
            # if result:
                # return True
            
        return False
        
    def mouse_released(self, event):
        # if self.layout != None:
            # result = self.layout.mouse_released(event)
            # if result:
                # return True
                
        return False
        
    def mouse_moved(self, event):
        # if self.layout != None:
            # result = self.layout.mouse_moved(event)
            # if result:
                # return True
                
        return False
        
    def mouse_dragged(self, event):
        # if self.layout != None:
            # result = self.layout.mouse_dragged(event)
            # if result:
                # return True
                
        return False
        
        
        