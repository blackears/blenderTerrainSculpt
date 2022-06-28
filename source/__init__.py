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
    "version": (1, 0, 3),
    "blender": (2, 80, 0),
    "location": "View3D",
#    "wiki_url": "https://github.com/blackears/uvTools",
#    "tracker_url": "https://github.com/blackears/uvTools",
    "category": "View 3D"
}

import bpy
import importlib


if "bpy" in locals():
    if "TerrainSculptMeshBrush" in locals():
#        importlib.reload(TerrainSculptMeshProperties)
        importlib.reload(TerrainSculptMeshBrush)
    else:
#        from .operators import TerrainSculptMeshProperties
        from .operators import TerrainSculptMeshBrush
        
    # if "terrainSculptMeshPanel" in locals():
        # importlib.reload(terrainSculptMeshPanel)
    # else:
        # from .operators import terrainSculptMeshPanel
        
else:
#    from .operators import TerrainSculptMeshProperties
    from .operators import TerrainSculptMeshBrush
    # from .operators import terrainSculptMeshPanel

def register():
#    TerrainSculptMeshProperties.register()
    TerrainSculptMeshBrush.register()
    # terrainSculptMeshPanel.register()


def unregister():
#    TerrainSculptMeshProperties.unregister()
    TerrainSculptMeshBrush.unregister()
    # terrainSculptMeshPanel.unregister()

