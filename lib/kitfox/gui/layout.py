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



#----------------------------------
class Size2D:
    def __init__(width = 0, height = 0):
        self.width = width
        self.height = height

#----------------------------------

class Rectangle2D:
    def __init__(self, x = 0, y = 0, width = 0, height = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def contains(self, x, y):
        return x >= self.x and x < self.x + self.width and y >= self.y and y < self.y + self.height
        
    def __str__(self):
        return str(self.x) + ", " + str(self.y) + ", " + str(self.width) + ", " + str(self.height)

        

#----------------------------------

class Layout:

    def __init__(self):
        self.parent = None
        self.window = None

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def get_window(self):
        return self.window

    def set_window(self, window):
        self.window = window
        
    def layout_components(self, bounds):
        pass

    def draw(self, ctx):
        pass
        
    def handle_event(self, context, event):
        return False

    def get_screen_position(self):
        if self.parent != None:
            return self.parent.get_screen_position()
        elif self.window != None:
            return self.window.get_screen_position()
        return Vector((0, 0))

    def mouse_pressed(self, event):
        return False

    def mouse_released(self, event):
        return False

    def mouse_moved(self, event):
        return False
        
#----------------------------------

class LayoutAxis(Enum):
    X = 1
    Y = 2
#----------------------------------

class ExpansionType(Enum):
    EXPAND = 1
    PREFERRED = 2
#    MIN = 3
#    MAX = 4


#----------------------------------


class LayoutBox(Layout):
    class Info:
        def __init__(self):
            self.span = 0
        

    def __init__(self, axis = Axis.X):
        super().__init__()
        
        self.axis = axis
        self.children = []

    def dump(self, indent = ""):
        print(indent + "LayoutBox " + str(self.axis))

        for child in self.children:
            child.dump(indent + " ")

        
    def add_child(self, child):
        self.children.append(child)
        child.set_parent_layout(self)
        
    def handle_event(self, context, event):
        for child in self.children:
            result = child.handle_event_dispatch(context, event)
            if result:
                return True
    
        return False

    def calc_minimum_size(self):
        span_x = 0
        span_y = 0
        
        for child in self.children:
            size = child.calc_minimum_size()
            
            if self.axis == Axis.X:
                span_x += size.x
                span_y = max(span_y, size.y)
            else:
                span_x = max(span_x, size.x)
                span_y += size.y
                
        return Vector((span_x, span_y))

    def calc_preferred_size(self):
        span_x = 0
        span_y = 0
        
        for child in self.children:
            size = child.calc_preferred_size()
            
            if self.axis == Axis.X:
                span_x += size.x
                span_y = max(span_y, size.y)
            else:
                span_x = max(span_x, size.x)
                span_y += size.y
                
        return Vector((span_x, span_y))


    def calc_maximum_size(self):
        span_x = 0
        span_y = 0
        
        for child in self.children:
            size = child.calc_maximum_size()
            
            if self.axis == Axis.X:
                span_x += size.x
                span_y = max(span_y, size.y)
            else:
                span_x = max(span_x, size.x)
                span_y += size.y
                
        return Vector((span_x, span_y))

    
    def layout_components(self, bounds):
        local_span = bounds.width if self.axis == Axis.X else bounds.height
    
        infoList = []
        total_span = 0
        
        
        #Allocate min sizes first
#        print("calc min")
        for i in range(len(self.children)):
            child = self.children[i]
            size = child.calc_minimum_size()
            
            info = self.Info()
            infoList.append(info)
            info.span = size.x if self.axis == Axis.X else size.y
            total_span += info.span

#            print("child %d: span %d" % (i, info.span))

        #Expand to preferred sizes if there is room
#        print("calc pref")
        for i in range(len(self.children)):
            if total_span < local_span:
                child = self.children[i]
                size = child.calc_preferred_size()
                pref_span = size.x if self.axis == Axis.X else size.y
                span_remaining = local_span - total_span
                
#                print("span_remaining " + str(span_remaining))
#                print("pref_span " + str(pref_span))
                
                info = infoList[i]
#                print("info.span " + str(info.span))
                span_to_add = min(span_remaining, pref_span - info.span)
                info.span += span_to_add
                total_span += span_to_add

#                print("child %d: span %d" % (i, info.span))
                    
        #If there is space left, expand children with expand set
        # print("calc max")
        # print("local_span " + str(local_span))
        # print("total_span " + str(total_span))
        for i in range(len(self.children)):
            if total_span < local_span:
                child = self.children[i]
                info = infoList[i]
#                print("info.span " + str(info.span))
                
                if (self.axis == Axis.X and child.expansion_type_x == ExpansionType.EXPAND) or (self.axis == Axis.Y and child.expansion_type_y == ExpansionType.EXPAND):
                    size = child.calc_maximum_size()
                    max_span = size.x if self.axis == Axis.X else size.y
                    
                    expand_to = min(max_span, local_span - total_span + info.span)

                    # print("max_span " + str(max_span))
                    # print("expand_to " + str(expand_to))
                    
                    # info = infoList[i]
                    # print("info.span " + str(info.span))
                    
                    span_to_add = expand_to - info.span
                    info.span += span_to_add
                    total_span += span_to_add

#                print("child %d: span %d" % (i, info.span))
                    
        #Apply sizes
        cursor_offset = 0
        for i in range(len(self.children)):
            child = self.children[i]
            info = infoList[i]
            
            if self.axis == Axis.X:
                child.position.x = cursor_offset
                child.position.y = 0
                child.size.x = info.span
                child.size.y = bounds.height
            else:
                child.position.x = 0
                child.position.y = cursor_offset
                child.size.x = bounds.width
                child.size.y = info.span
                
            child.layout_components()
                
            cursor_offset += info.span

    def draw(self, ctx):
        for child in self.children:
            child.draw(ctx)

    def pick_panel_stack(self, pos):
        for child in self.children:
            child_pos = child.position
            
            #Bounds relative to parent
            bounds = child.bounds()
            
#            print ("testing bounds " + str(bounds))
            if bounds.contains(pos[0], pos[1]):
#                print ("bounds test passed")
            
                rel_pos = pos - child_pos
                result = child.pick_panel_stack(rel_pos)
                
                # if result:
                    # return True
                result.insert(0, child)
                return result
            
        return []

    def mouse_pressed(self, event):
        # print ("layout mouse_pressed")
        # print ("in event " + str(event))
    
        for child in self.children:
            pos = child.position
            
            #Bounds relative to parent
            bounds = child.bounds()
            
#            print ("testing bounds " + str(bounds))
            if bounds.contains(event.pos[0], event.pos[1]):
#                print ("bounds test passed")
            
                evt = event.copy()
                evt.pos -= pos
                result = child.mouse_pressed(evt)
                
                if result:
                    return True
            
        return False

    def mouse_released(self, event):
        for child in self.children:
            pos = child.position
            
            #Bounds relative to parent
            bounds = child.bounds()
            if bounds.contains(event.pos[0], event.pos[1]):
            
                evt = event.copy()
                evt.pos -= pos
                result = child.mouse_released(evt)
                if result:
                    return True

        return False
        
    def mouse_moved(self, event):
        for child in self.children:
            pos = child.position
            
            #Bounds relative to parent
            bounds = child.bounds()
            if bounds.contains(event.pos[0], event.pos[1]):
            
                evt = event.copy()
                evt.pos -= pos
                result = child.mouse_moved(evt)
                if result:
                    return True

        return False
