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


bl_info = {
    "name": "Terrain Sculpting Tools",
    "description": "Tools for creating and editing terrains.",
    "author": "Mark McKay",
    "version": (1, 0, 9),
    "blender": (4, 4, 1),
    "location": "View3D",
#    "wiki_url": "https://github.com/blackears/uvTools",
#    "tracker_url": "https://github.com/blackears/uvTools",
    "category": "View 3D"
}

import importlib


if "bpy" in locals():
    if "TerrainSculptMeshBrushPanel" in locals():
        importlib.reload(TerrainSculptMeshBrushPanel)
    else:
        from .operators import TerrainSculptMeshBrushPanel
        
        
else:
    from .operators import TerrainSculptMeshBrushPanel

def register():
    TerrainSculptMeshBrushPanel.register()


def unregister():
    TerrainSculptMeshBrushPanel.unregister()

