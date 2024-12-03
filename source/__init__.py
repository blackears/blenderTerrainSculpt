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
    "version": (1, 0, 8),
    "blender": (4, 0, 0),
    "location": "View3D",
#    "wiki_url": "https://github.com/blackears/uvTools",
#    "tracker_url": "https://github.com/blackears/uvTools",
    "category": "View 3D"
}

import bpy
import importlib


if "bpy" in locals():
    if "TerrainSculptMeshBrushPanel" in locals():
#        importlib.reload(TerrainSculptMeshProperties)
        importlib.reload(TerrainSculptMeshBrushPanel)
    else:
#        from .operators import TerrainSculptMeshProperties
        from .operators import TerrainSculptMeshBrushPanel
        
    # if "terrainSculptMeshPanel" in locals():
        # importlib.reload(terrainSculptMeshPanel)
    # else:
        # from .operators import terrainSculptMeshPanel
        
else:
#    from .operators import TerrainSculptMeshProperties
    from .operators import TerrainSculptMeshBrushPanel
    # from .operators import terrainSculptMeshPanel

def register():
#    TerrainSculptMeshProperties.register()
    TerrainSculptMeshBrushPanel.register()
    # terrainSculptMeshPanel.register()


def unregister():
#    TerrainSculptMeshProperties.unregister()
    TerrainSculptMeshBrushPanel.unregister()
    # terrainSculptMeshPanel.unregister()

