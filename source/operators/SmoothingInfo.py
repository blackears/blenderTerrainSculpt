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


class SmoothingPointInfo:
    def __init__(self, coord, height):
        self.coord = coord
        self.centroidHeight = height

class SmoothingInfo:
    def __init__(self):
        self.points = []
        
    def addPoint(self, wpos, height):
        self.points.append(SmoothingPointInfo(wpos, height))
        
    def getCentroidHeight(self, wpos, terrain_origin, world_shape_type, smooth_edge_snap_distance):
    #########
#        print("getCentroidHeight( wpos " + str(wpos))
        if world_shape_type == 'FLAT':
            down = -vecZ
            wpos_parallel = wpos.project(down)
            wpos_perp = wpos_parallel - wpos
            
            centroidHeight = 0
            count = 0
            
                        
            for p in self.points:
                coord_parallel = p.coord.project(down)
                coord_perp = coord_parallel - p.coord
                
#                print ("coord_perp " + str(coord_perp))
#                print ("coord_perp - wpos_perp " + str(coord_perp - wpos_perp))
                
                if (coord_perp - wpos_perp).magnitude < smooth_edge_snap_distance:
 #                   print ("p.centroidHeight " + str(p.centroidHeight))
                    centroidHeight += p.centroidHeight
                    count += 1
                    #return p.centroidHeight
                    
            if count >= 1:
#                print ("centroidHeight / count " + str(centroidHeight / count))
                return centroidHeight / count
            return 0
        else:        
            #This currently does not take into account meshes that meet at seams
            for p in self.points:
                if (p.coord - wpos).magnitude < .001:
                    return p.centroidHeight
            return 0
    
        