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
from .events import *

#----------------------------------

# class Inset2D:
    # def __init__(self, left = 0, top = 0, right = 0, bottom = 0):
        # self.left = left
        # self.top = top
        # self.right = right
        # self.bottom = bottom
        
    # def __str__(self):
        # return str(self.left) + ", " + str(self.top) + ", " + str(self.right) + ", " + str(self.bottom)
    





#----------------------------------

class FoldoutPanel(Panel):
    def __init__(self):
        super().__init__()
        self.position = Vector((0, 0))



#----------------------------------

class TitleBar(Label):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.dragging = False


    def mouse_pressed(self, event):
        if event.mouse_button == MouseButton.LEFT:
            self.dragging = True
            self.drag_start = event.screen_pos
            self.window_start = self.window.position.copy()

            # print ("TextINput pressed")
            # print("event.pos" + str(event.pos))
            # print("event.screen_pos" + str(event.screen_pos))
        return True
        
    def mouse_released(self, event):
        if event.mouse_button == MouseButton.LEFT:
            self.dragging = False

        # print ("TextINput released")
        # print("event.pos" + str(event.pos))
        # print("event.screen_pos" + str(event.screen_pos))
        return True
        
    def mouse_dragged(self, event):
        if self.dragging:
            offset = event.screen_pos - self.drag_start
            self.window.position = self.window_start + offset
    
        return True


    # def mouse_click(self, context, event):
        # c2s = self.coords_to_screen_matrix(context)
        # s2c = c2s.inverted()
        # mouse_pos = s2c @ Vector((event.mouse_region_x, event.mouse_region_y, 0, 1))

        # # print ("event.mouse_region_x " + str(event.mouse_region_x))
        # # print ("event.mouse_region_y " + str(event.mouse_region_y))
        # # print ("mouse_pos " + str(mouse_pos))
        
        # bounds = self.bounds()
        
        # # print ("bounds " + str(bounds))
        
        # if bounds.contains(mouse_pos.x, mouse_pos.y):
            # if event.value == "PRESS":
                # self.layout.dispatch_mouse_event
            
                # self.dragging = True
                # self.mouse_down_pos = mouse_pos
                # self.start_position = self.position.copy()
            # else:
                # self.dragging = False
# #            return {'consumed': True}
            # return True
    
# #        return {'consumed': False}
        # return False
        
    # def mouse_move(self, context, event):
        # c2s = self.coords_to_screen_matrix(context)
        # s2c = c2s.inverted()
        # mouse_pos = s2c @ Vector((event.mouse_region_x, event.mouse_region_y, 0, 1))
        
        
        # if self.dragging:
            # offset = mouse_pos - self.mouse_down_pos
    
            # self.position = self.start_position + offset.to_2d()
# #            return {'consumed': True}
            # return True
            
# #        return {'consumed': False}
        # return False
      

#----------------------------------

class PanelStack:
    def __init__(self, stack):
        self.stack = stack
        
    # def add(self, panel):
        # self.stack.append(panel)
        
    def window_to_local(self, window_pos):
        local_pos = window_pos.copy()
        for panel in self.stack:
            local_pos -= panel.position
        return local_pos

    def __str__(self):
        strn = ""
        for panel in self.stack:
            strn += "panel bounds " + str(panel.bounds()) + "\n"
        return strn

#----------------------------------

class Window:
    def __init__(self):
        self.position = Vector((100, 40))
        self.size = Vector((200, 400))

        self.background_color = Vector((.5, .5, .5, 1))
        self.font_color = Vector((1, 1, 1, 1))
        self.font_dpi = 20
        self.font_size = 60
        
        self.dragging = False
        
        self.layout = LayoutBox(Axis.Y)
        self.layout.set_window(self)

        self.title_panel = TitleBar(self)
        self.layout.add_child(self.title_panel)
        self.title_panel.set_font_size(60)
        
        self.main_panel = Panel()
        self.layout.add_child(self.main_panel)
        self.main_panel.expansion_type_x = ExpansionType.EXPAND
        self.main_panel.expansion_type_y = ExpansionType.EXPAND
        

        self.layout.layout_components(self.bounds())
        
        #Track mouse press events
        self.captured_panel_stack = None
        self.mouse_left_down = False
        self.mouse_middle_down = False
        self.mouse_right_down = False


    def get_title(self):
        return self.__title

    def set_title(self, title):
        self.__title = title
        self.title_panel.text = title

    def get_main_panel(self):
        return self.main_panel

    def get_screen_position(self):
        return self.position.copy()
        
    def bounds(self):
        return Rectangle2D(self.position.x, self.position.y, self.size.x, self.size.y)
            
    def coords_to_screen_matrix(self, context):
        region = context.region
        #rv3d = context.region_data

        mT = Matrix.Translation((0, region.height, 0))
        mS = Matrix.Diagonal((1, -1, 1, 1))
        return mT @ mS
        
        
    def draw(self, context):
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        
        ctx = DrawContext2D(context)
        
        ctx.translate(self.position.x, self.position.y)
        ctx.color = self.background_color.copy()
        ctx.fill_round_rectangle(0, 0, self.size.x, self.size.y, 10)

        #Draw panel components
        self.layout.draw(ctx)

        
    def mouse_pos(self, context, event):
        c2s = self.coords_to_screen_matrix(context)
        s2c = c2s.inverted()
        screen_pos = s2c @ Vector((event.mouse_region_x, event.mouse_region_y, 0, 1))
        return screen_pos.to_2d()
        
    def window_to_local(self, window_pos):
        local_pos = window_pos.copy()
        for panel in stack:
            local_pos -= panel.position
        return local_pos
        
    def handle_event(self, context, event):
        bounds = self.bounds()

#        print("event typ:" + event.type + " val: " + event.value)

        mouse_button = None
        
        if event.type == 'LEFTMOUSE':
            mouse_button = MouseButton.LEFT
            
            if event.value == "PRESS":
                self.mouse_left_down = True
            elif event.value == "RELEASE":
                self.mouse_left_down = False

        if event.type == 'RIGHTMOUSE':
            mouse_button = MouseButton.RIGHT
            
            if event.value == "PRESS":
                self.mouse_right_down = True
            elif event.value == "RELEASE":
                self.mouse_right_down = False

        if event.type == 'MIDDLEMOUSE':
            mouse_button = MouseButton.MIDDLE
            
            if event.value == "PRESS":
                self.mouse_middle_down = True
            elif event.value == "RELEASE":
                self.mouse_middle_down = False


        if mouse_button != None:
            mouse_pos = self.mouse_pos(context, event)
            mouse_window_pos = mouse_pos - self.position
            
            if self.captured_panel_stack != None:
            
 #               print("panel stack is captured")
                
                if event.value == "RELEASE":
#                    print("RELEASE stack \n" + str(self.captured_panel_stack))
                
                    local_pos = self.captured_panel_stack.window_to_local(mouse_window_pos)
                    evt = MouseButtonEvent(
                        mouse_button = mouse_button, 
                        pos = local_pos, 
                        screen_pos = mouse_pos,
                        left_down = self.mouse_left_down,
                        middle_down = self.mouse_middle_down,
                        right_down = self.mouse_right_down,
                        shift_down = event.shift,
                        ctrl_down = event.ctrl,
                        alt_down = event.alt
                    )
                    
                    self.captured_panel_stack.stack[-1].mouse_released(evt)
                    
#                    print("self.mouse_left_down" + str(self.mouse_left_down))
#                    print("self.mouse_right_down" + str(self.mouse_right_down))
                    
                    #If all buttons are released, end mouse capture
                    if self.mouse_left_down == False and self.mouse_middle_down == False and self.mouse_right_down == False:
#                        print("END capture")
                        self.captured_panel_stack = None
                        
                    return True
                
            elif bounds.contains(mouse_pos[0], mouse_pos[1]):
                #evt = MouseButtonEvent(mouse_button = MouseButton.LEFT, pos = mouse_pos - self.position, screen_pos = mouse_pos)

                if event.value == "PRESS":
                    stack = self.layout.pick_panel_stack(mouse_window_pos)
                    self.captured_panel_stack = PanelStack(stack)
                    
                    
#                    print("self.captured_panel_stack \n" + str(self.captured_panel_stack))
                    
                    local_pos = self.captured_panel_stack.window_to_local(mouse_window_pos)
                    evt = MouseButtonEvent(
                        mouse_button = mouse_button, 
                        pos = local_pos, 
                        screen_pos = mouse_pos,
                        left_down = self.mouse_left_down,
                        middle_down = self.mouse_middle_down,
                        right_down = self.mouse_right_down,
                        shift_down = event.shift,
                        ctrl_down = event.ctrl,
                        alt_down = event.alt
                    )
                    self.captured_panel_stack.stack[-1].mouse_pressed(evt)
                      
                    return True
    
        
        elif event.type == 'MOUSEMOVE':
            mouse_pos = self.mouse_pos(context, event)
            mouse_window_pos = mouse_pos - self.position
            
            if self.captured_panel_stack != None:
#                print("mouse DRAG")
                local_pos = self.captured_panel_stack.window_to_local(mouse_window_pos)
                evt = MouseButtonEvent(
                    pos = local_pos, 
                    screen_pos = mouse_pos,
                    left_down = self.mouse_left_down,
                    middle_down = self.mouse_middle_down,
                    right_down = self.mouse_right_down,
                    shift_down = event.shift,
                    ctrl_down = event.ctrl,
                    alt_down = event.alt
                )
                
                self.captured_panel_stack.stack[-1].mouse_dragged(evt)
                
                return True
            
            elif bounds.contains(mouse_pos[0], mouse_pos[1]):
#                print("mouse MOVE")
                stack = self.layout.pick_panel_stack(mouse_window_pos)
                stack = PanelStack(stack)
                
                local_pos = stack.window_to_local(mouse_window_pos)
                evt = MouseButtonEvent(
                    pos = local_pos, 
                    screen_pos = mouse_pos,
                    left_down = self.mouse_left_down,
                    middle_down = self.mouse_middle_down,
                    right_down = self.mouse_right_down,
                    shift_down = event.shift,
                    ctrl_down = event.ctrl,
                    alt_down = event.alt
                )
                stack.stack[-1].mouse_moved(evt)
                
                return True
        
        return False
        
        