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


import mathutils
import math
from bpy_extras import view3d_utils
from enum import Enum
import numpy as np


vecX = mathutils.Vector((1, 0, 0))
vecY = mathutils.Vector((0, 1, 0))
vecZ = mathutils.Vector((0, 0, 1))
vecZero = mathutils.Vector((0, 0, 0))

circleSegs = 64
coordsCircle = [(math.sin(((2 * math.pi * i) / circleSegs)), math.cos((math.pi * 2 * i) / circleSegs), 0) for i in range(circleSegs + 1)]

coordsSquare = [(0, 0, 0), (1, 0, 0), 
(1, 1, 0), (0, 1, 0)
]

coordsSquare_strip = [(0, 0, 0), (1, 0, 0), 
(1, 1, 0), (0, 1, 0), 
(0, 0, 0)
]

coordsSquare2_strip = [(-1, -1, 0), (1, -1, 0), 
(1, 1, 0), (-1, 1, 0), 
(-1, -1, 0)
]


coordsCube = [(0, 0, 0), (1, 0, 0), 
(1, 0, 0), (1, 1, 0), 
(1, 1, 0), (0, 1, 0), 
(0, 1, 0), (0, 0, 0), 

(0, 0, 0), (0, 0, 1), 
(1, 0, 0), (1, 0, 1), 
(1, 1, 0), (1, 1, 1), 
(0, 1, 0), (0, 1, 1), 

(0, 0, 1), (1, 0, 1), 
(1, 0, 1), (1, 1, 1), 
(1, 1, 1), (0, 1, 1), 
(0, 1, 1), (0, 0, 1), 
]

cubeVerts = [(0, 0, 0),
(1, 0, 0),
(0, 1, 0),
(1, 1, 0),
(0, 0, 1),
(1, 0, 1),
(0, 1, 1),
(1, 1, 1),
]

cubeFaces = [(2, 3, 1, 0),
(4, 5, 7, 6),
(0, 1, 5, 4),
(6, 7, 3, 2),
(1, 3, 7, 5),
(2, 0, 4, 6),
]

cubeUvs = [
((0, 0), (1, 0), (1, 1), (0, 1)),
((0, 0), (1, 0), (1, 1), (0, 1)),
((0, 0), (1, 0), (1, 1), (0, 1)),
((0, 0), (1, 0), (1, 1), (0, 1)),
((0, 0), (1, 0), (1, 1), (0, 1)),
((0, 0), (1, 0), (1, 1), (0, 1))
]

def unitCube():
    coords = []
    normals = []
    uvs = []

    v000 = mathutils.Vector((-1, -1, -1))
    v100 = mathutils.Vector((1, -1, -1))
    v010 = mathutils.Vector((-1, 1, -1))
    v110 = mathutils.Vector((1, 1, -1))
    v001 = mathutils.Vector((-1, -1, 1))
    v101 = mathutils.Vector((1, -1, 1))
    v011 = mathutils.Vector((-1, 1, 1))
    v111 = mathutils.Vector((1, 1, 1))

    nx0 = mathutils.Vector((-1, 0, 0))
    nx1 = mathutils.Vector((1, 0, 0))
    ny0 = mathutils.Vector((0, -1, 0))
    ny1 = mathutils.Vector((0, 1, 0))
    nz0 = mathutils.Vector((0, 0, -1))
    nz1 = mathutils.Vector((0, 0, 1))

    uv00 = mathutils.Vector((0, 0))
    uv10 = mathutils.Vector((1, 0))
    uv01 = mathutils.Vector((0, 1))
    uv11 = mathutils.Vector((1, 1))
    
    #Face -x
    coords.append(v010)
    coords.append(v000)
    coords.append(v001)
    
    coords.append(v010)
    coords.append(v001)
    coords.append(v011)

    for i in range(6):
        normals.append(nx0)
    
    uvs.append(uv00)
    uvs.append(uv10)
    uvs.append(uv11)
    uvs.append(uv00)
    uvs.append(uv11)
    uvs.append(uv01)
    
    
    #Face +x
    coords.append(v100)
    coords.append(v110)
    coords.append(v111)
    
    coords.append(v100)
    coords.append(v111)
    coords.append(v101)

    for i in range(6):
        normals.append(nx1)
    
    uvs.append(uv00)
    uvs.append(uv10)
    uvs.append(uv11)
    uvs.append(uv00)
    uvs.append(uv11)
    uvs.append(uv01)
    
    #Face -y
    coords.append(v000)
    coords.append(v100)
    coords.append(v101)
    
    coords.append(v000)
    coords.append(v101)
    coords.append(v001)

    for i in range(6):
        normals.append(ny0)
    
    uvs.append(uv00)
    uvs.append(uv10)
    uvs.append(uv11)
    uvs.append(uv00)
    uvs.append(uv11)
    uvs.append(uv01)
    
    
    #Face +y
    coords.append(v110)
    coords.append(v010)
    coords.append(v011)
    
    coords.append(v110)
    coords.append(v011)
    coords.append(v111)

    for i in range(6):
        normals.append(ny1)
    
    uvs.append(uv00)
    uvs.append(uv10)
    uvs.append(uv11)
    uvs.append(uv00)
    uvs.append(uv11)
    uvs.append(uv01)
    

    #Face -z
    coords.append(v010)
    coords.append(v110)
    coords.append(v100)
    
    coords.append(v010)
    coords.append(v100)
    coords.append(v000)

    for i in range(6):
        normals.append(nz0)
    
    uvs.append(uv00)
    uvs.append(uv10)
    uvs.append(uv11)
    uvs.append(uv00)
    uvs.append(uv11)
    uvs.append(uv01)
    
    
    #Face +z
    coords.append(v001)
    coords.append(v101)
    coords.append(v111)
    
    coords.append(v001)
    coords.append(v111)
    coords.append(v011)

    for i in range(6):
        normals.append(nz1)
    
    uvs.append(uv00)
    uvs.append(uv10)
    uvs.append(uv11)
    uvs.append(uv00)
    uvs.append(uv11)
    uvs.append(uv01)
        
    return (coords, normals, uvs)

def unitCylinder(segs = 16, radius0 = 1, radius1 = 1, bottom_cap = False, top_cap = False):
    coords = []
    normals = []
    uvs = []
    
    vc0 = mathutils.Vector((0, 0, -1))
    vc1 = mathutils.Vector((0, 0, 1))
    uvc = mathutils.Vector((.5, .5))
    
    for s in range(segs):
        sin0 = math.sin(math.radians(360 * s / segs))
        cos0 = math.cos(math.radians(360 * s / segs))
        sin1 = math.sin(math.radians(360 * (s + 1) / segs))
        cos1 = math.cos(math.radians(360 * (s + 1) / segs))
        
        v00 = mathutils.Vector((sin0 * radius0, cos0 * radius0, -1))
        v10 = mathutils.Vector((sin1 * radius0, cos1 * radius0, -1))
        v01 = mathutils.Vector((sin0 * radius1, cos0 * radius1, 1))
        v11 = mathutils.Vector((sin1 * radius1, cos1 * radius1, 1))
        
        tan0 = mathutils.Vector((cos0, sin0, 0))
        n00 = (v01 - v00).cross(tan0)
        n00.normalize()
        n01 = n00
        tan1 = mathutils.Vector((cos1, sin1, 0))
        n10 = (v11 - v10).cross(tan1)
        n10.normalize()
        n11 = n10
        
        uv00 = mathutils.Vector((s / segs, 0))
        uv10 = mathutils.Vector(((s + 1) / segs, 0))
        uv01 = mathutils.Vector((s / segs, 1))
        uv11 = mathutils.Vector(((s + 1) / segs, 1))
        
        if radius0 != 0:
            coords.append(v00)
            coords.append(v10)
            coords.append(v11)
            
            normals.append(n00)
            normals.append(n10)
            normals.append(n11)
        
            uvs.append(uv00)
            uvs.append(uv10)
            uvs.append(uv11)

        if radius1 != 0:
            coords.append(v00)
            coords.append(v11)
            coords.append(v01)
            
            normals.append(n00)
            normals.append(n11)
            normals.append(n01)
            
            uvs.append(uv00)
            uvs.append(uv11)
            uvs.append(uv01)
        
        if top_cap and radius1 != 0:
            coords.append(v01)
            coords.append(v11)
            coords.append(vc1)
            
            normals.append(vecZ)
            normals.append(vecZ)
            normals.append(vecZ)
            
            uvs.append(mathutils.Vector((sin0, cos0)))
            uvs.append(mathutils.Vector((sin1, cos1)))
            uvs.append(uvc)
        
        if bottom_cap and radius0 != 0:
            coords.append(v00)
            coords.append(v10)
            coords.append(vc0)
            
            normals.append(-vecZ)
            normals.append(-vecZ)
            normals.append(-vecZ)
            
            uvs.append(mathutils.Vector((sin0, cos0)))
            uvs.append(mathutils.Vector((sin1, cos1)))
            uvs.append(uvc)
            
        
    return (coords, normals, uvs)

        
def unitCone(segs = 16, radius = 1, cap = False):
    return unitCylinder(segs, radius, 0, cap, False)


def unitSphere(segs_lat = 8, segs_long = 16):
    coords = []
    normals = []
    uvs = []
    

    for la in range(segs_lat):
        z0 = math.cos(math.radians(180 * la / segs_lat))
        z1 = math.cos(math.radians(180 * (la + 1) / segs_lat))
        r0 = math.sin(math.radians(180 * la / segs_lat))
        r1 = math.sin(math.radians(180 * (la + 1) / segs_lat))
        
        for lo in range(segs_long):
            cx0 = math.sin(math.radians(360 * lo / segs_long))
            cx1 = math.sin(math.radians(360 * (lo + 1) / segs_long))
            cy0 = math.cos(math.radians(360 * lo / segs_long))
            cy1 = math.cos(math.radians(360 * (lo + 1) / segs_long))
            
            v00 = mathutils.Vector((cx0 * r0, cy0 * r0, z0))
            v10 = mathutils.Vector((cx1 * r0, cy1 * r0, z0))
            v01 = mathutils.Vector((cx0 * r1, cy0 * r1, z1))
            v11 = mathutils.Vector((cx1 * r1, cy1 * r1, z1))
            
            if la != 0:
                coords.append(v00)
                coords.append(v11)
                coords.append(v10)
            
                normals.append(v00)
                normals.append(v10)
                normals.append(v11)
            
                uvs.append((lo / segs_long, la / segs_lat))
                uvs.append(((lo + 1) / segs_long, la / segs_lat))
                uvs.append(((lo + 1) / segs_long, (la + 1) / segs_lat))
            
            if la != segs_lat - 1:
                coords.append(v00)
                coords.append(v01)
                coords.append(v11)
            
                normals.append(v00)
                normals.append(v11)
                normals.append(v01)
                
                uvs.append((lo / segs_long, la / segs_lat))
                uvs.append(((lo + 1) / segs_long, (la + 1) / segs_lat))
                uvs.append((lo / segs_long, (la + 1) / segs_lat))
            
    return (coords, normals, uvs)
    

def unitTorus(radius = 1, ring_radius = .2, segs_u = 16, segs_v = 8):
    coords = []
    normals = []
    uvs = []

#    print("--Build torus")

    for i in range(segs_u):
        cx0 = math.sin(math.radians(360 * i / segs_u)) * radius
        cy0 = math.cos(math.radians(360 * i / segs_u)) * radius
        cx1 = math.sin(math.radians(360 * (i + 1) / segs_u)) * radius
        cy1 = math.cos(math.radians(360 * (i + 1) / segs_u)) * radius

        c0 = mathutils.Vector((cx0, cy0, 0))
        c1 = mathutils.Vector((cx1, cy1, 0))

#        print("c0 %s" % (str(c0)))

        for j in range(segs_v):
            dir0 = c0 * ring_radius / c0.magnitude
            dir1 = c1 * ring_radius / c1.magnitude
            
            tan0 = dir0.cross(vecZ)
            tan1 = dir1.cross(vecZ)

#            print("dir0 %s" % (str(dir0)))
#            print("tan0 %s" % (str(tan0)))

            q00 = mathutils.Quaternion(tan0, math.radians(360 * j / segs_v))
            q01 = mathutils.Quaternion(tan0, math.radians(360 * (j + 1) / segs_v))
            q10 = mathutils.Quaternion(tan1, math.radians(360 * j / segs_v))
            q11 = mathutils.Quaternion(tan1, math.radians(360 * (j + 1) / segs_v))
            
            # m00 = q00.to_matrix()
            # m01 = q01.to_matrix()
            # m10 = q10.to_matrix()
            # m11 = q11.to_matrix()

#            print("m00 %s" % (str(m00)))
            
            # p00 = m00 @ dir0 + c0
            # p01 = m01 @ dir0 + c0
            # p10 = m10 @ dir1 + c1
            # p11 = m11 @ dir1 + c1

#            print("p00 %s" % (str(p00)))
            
            # p00 = q00 @ dir0 @ q00.conjugated() + c0
            # p01 = q01 @ dir0 @ q01.conjugated() + c0
            # p10 = q10 @ dir1 @ q10.conjugated() + c1
            # p11 = q11 @ dir1 @ q11.conjugated() + c1

            p00 = q00 @ dir0 + c0
            p01 = q01 @ dir0 + c0
            p10 = q10 @ dir1 + c1
            p11 = q11 @ dir1 + c1
            
            vu = p10 - p00
            vv = p01 - p00
            norm = vu.cross(vv)
            norm.normalize()
            
            uv00 = mathutils.Vector((i / segs_u, j / segs_v))
            uv10 = mathutils.Vector(((i + 1) / segs_u, j / segs_v))
            uv01 = mathutils.Vector((i / segs_u, (j + 1) / segs_v))
            uv11 = mathutils.Vector(((i + 1) / segs_u, (j + 1) / segs_v))
        
            coords.append(p00)
            coords.append(p10)
            coords.append(p11)

            coords.append(p00)
            coords.append(p11)
            coords.append(p01)
            
            for k in range(6):
                normals.append(norm)
            
            uvs.append(uv00)
            uvs.append(uv10)
            uvs.append(uv11)
            
            uvs.append(uv00)
            uvs.append(uv11)
            uvs.append(uv01)

    return (coords, normals, uvs)


class Axis(Enum):
    X = 1
    Y = 2
    Z = 3


class Face(Enum):
    X_POS = 0
    X_NEG = 1
    Y_POS = 2
    Y_NEG = 3
    Z_POS = 4
    Z_NEG = 5

#Multiply a vector by a 4x4 matrix.  Returns 3d vector.
def mul_vector(matrix, vector):
    v0 = vector.to_4d()
    v0.w = 0
    v1 = matrix @ v0
    return v1.to_3d()


    

#Returns the fraction of the viewport that a sphere of radius 1 will occupy
def dist_from_viewport_center3(pos, region, rv3d):
    
    w2v = rv3d.view_matrix
    v2w = w2v.inverted()
    #view_origin = v2w.translation.copy()
    j = v2w.col[1].to_3d()
    
#    print("v2w " + str(v2w))
#    print("j " + str(j))
    
    persp = rv3d.perspective_matrix
    
    pos0_win = persp @ pos.to_4d()
    pos0_win /= pos0_win.w
    p0 = pos0_win.to_2d()
    
#    print("pos0_win " + str(pos0_win))
#    print("p0 " + str(p0))
    
    pos1_win = persp @ (pos + j).to_4d()
    pos1_win /= pos1_win.w
    p1 = pos1_win.to_2d()

#    print("pos1_win " + str(pos1_win))
#    print("p1 " + str(p1))
    
    dist = (p1 - p0).magnitude
    
#    print("dist " + str(dist))
    
#    return dist / region.height
#    return 1 / dist
#    return region.height / dist
    return dist
    

def calc_unit_scale3(pos, region, rv3d):

    w2win = rv3d.window_matrix @ rv3d.perspective_matrix @ rv3d.view_matrix

    p0 = pos.to_4d()
    p1 = (pos + vecZ).to_4d()

    q0 = w2win @ p0
    q1 = w2win @ p1
    
    q0 /= q0.w
    q1 /= q1.w
    
    dq = q1 - q0
    dq.z = 0
    
    print("p0 " + str(q0))
    print("p1 " + str(q1))
    print("dq " + str(dq))
    
    return dq.magnitude
    

#Returns scalar s to multiply line_dir by so that line_point + s * line_dir lies on plane
# note that plane_norm does not need to be normalized
def isect_line_plane(line_point, line_dir, plane_point, plane_norm):
    to_plane = (plane_point - line_point).project(plane_norm)
    dir_par_to_norm = line_dir.project(plane_norm)
    
    if dir_par_to_norm.magnitude == 0:
        return None
        
    scalar = to_plane.magnitude / dir_par_to_norm.magnitude
    if to_plane.dot(dir_par_to_norm) < 0:
        scalar = -scalar
    return scalar


#Returns scalar s to multiply line_dir0 by so that line_point0 + s * line_dir0 is as close as possible to the other line
def closest_point_to_line(line_point0, line_dir0, line_point1, line_dir1):
    #vector perpendicular to both line 0 and line 1
    r = line_dir0.cross(line_dir1)
    norm = r.cross(line_dir1)
    return isect_line_plane(line_point0, line_dir0, line_point1, norm)


#Returns the ray of the intersection of two planes
def isect_planes(point0, normal0, point1, normal1):
    ray_normal = normal0.cross(normal1)
    ray_normal.normalize()
    
    perp = ray_normal.cross(normal0)
    
    s = isect_line_plane(point0, perp, point1, normal1)
    ray_point = point0 + s * perp
    
    return ray_point, ray_normal


#Finds the best s such that v1 = s * v0.  Presumes vectors are parallel
def findVectorScalar(v0, v1):
    xx = abs(v1.x - v0.x)
    yy = abs(v1.y - v0.y)
    zz = abs(v1.z - v0.z)
    
    if xx > yy and xx > zz:
        return v1.x / v0.x
    elif yy > zz:
        return v1.y / v0.y
    else:
        return z1.y / v0.z
    

def lerp(a, b, t):
    return a * (1 - t) + b * t

def abs_vector(vector):
    return mathutils.Vector((abs(vector.x), abs(vector.y), abs(vector.z)))

def floor_vector(vector):
    return mathutils.Vector((math.floor(vector.x), math.floor(vector.y), math.floor(vector.z)))

def mult_vector(matrix, vector):
    v = vector.copy()
    v.resize_4d()
    v.w = 0
    v = matrix @ v
    v.resize_3d()
    return v

def mult_normal(matrix, normal):
    m = matrix.copy()
    m.invert()
    m.transpose()
    return mult_vector(m, normal)
    
def closest_axis(vector):
    xx = abs(vector.x)
    yy = abs(vector.y)
    zz = abs(vector.z)
    
    if xx > yy and xx > zz:
        return Axis.X
    elif yy > zz:
        return Axis.Y
    else:
        return Axis.Z
    
def create_matrix(i, j, k, translation):
    ii = i.to_4d()
    ii.w = 0
    jj = j.to_4d()
    jj.w = 0
    kk = k.to_4d()
    kk.w = 0
    tt = translation.to_4d()
    m = mathutils.Matrix([ii, jj, kk, tt])
    m.transpose()
    return m
    


def project_point_onto_plane(point, plane_pt, plane_norm):
    proj = (point - plane_pt).project(plane_norm)
    return point - proj

#return vector of coefficients [a, b, c] such that vec = a * v0 + b * v1 + c * v2
def express_in_basis(vec, v0, v1, v2):
    v = mathutils.Matrix((v0, v1, v2)) #row order
    if v.determinant() == 0:
        return mathutils.Vector((0, 0, 0))
        
    vI = v.copy()
    vI.transpose()
    vI.invert()
    return vI @ vec
    
def snap_to_grid(pos, unit):
    p = mathutils.Vector(pos)
    p /= unit
    p += mathutils.Vector((.5, .5, .5))
    
    p.x = math.floor(p.x)
    p.y = math.floor(p.y)
    p.z = math.floor(p.z)
    
    p *= unit
    
    return p
    
def snap_to_grid_plane(pos, unit, plane_point, plane_normal):
    sp = snap_to_grid(pos, unit)

    axis = closest_axis(plane_normal)
    
    if axis == Axis.X:
        s = isect_line_plane(sp, vecX, plane_point, plane_normal)
        return sp + s * vecX
    elif axis == Axis.Y:
        s = isect_line_plane(sp, vecY, plane_point, plane_normal)
        return sp + s * vecY
    else:
        s = isect_line_plane(sp, vecZ, plane_point, plane_normal)
        return sp + s * vecZ

def intersect_triangle(p0, p1, p2, pickOrigin, pickRay):
    v10 = p1 - p0
    v20 = p2 - p0
    v21 = p2 - p1
    norm = v10.cross(v20)
    norm.normalize()
    
    scalar = isect_line_plane(pickOrigin, pickRay, p0, norm)
    if scalar == None:
        return None
        
    hitPoint = pickOrigin + scalar * pickRay
    
    vh0 = hitPoint - p0
    vh1 = hitPoint - p1
    v01 = -v10
    
    if vh0.cross(v20).dot(v10.cross(v20)) < 0:
        return None
    if vh0.cross(v10).dot(v20.cross(v10)) < 0:
        return None
    if vh1.cross(v21).dot(v01.cross(v21)) < 0:
        return None
    
    return hitPoint
    
#Finds the vector x such the function f(x) = A @ x - b is minimized.
#  A and b must be numpy matricies and have the same number of rows.
#  return value is a numpy vector
def least_squares_fit(A, b):
    aa = A.T @ A
    
    if np.isfinite(np.linalg.cond(aa)):
        aa = np.linalg.inv(aa)
    else:
        return (False, [])
    
    x = aa @ A.T @ b
    
    return (True, x)

# #points is an array of 3D points.
# #  @returns [point, normal] of plane that best fits points
# def fit_points_to_plane(points):
    # P = np.array(points)
    # rows = P.shape[0]
    
    # ones = np.ones(rows).reshape((rows, 1))
    
    # aa = P[:, 0:-1]
    # A = np.hstack((aa, ones))
    
    # b = P[:, -1]
    
    # valid, C = least_squares_fit(A, b)
    # if valid == False:
        # return (False, vecZero, vecZero)
    # pos = mathutils.Vector((0, 0, C[2]))
    
    # norm = mathutils.Vector((C[0], C[1], -1))
    # norm.normalize()
    
    # return (True, pos, norm)

#points is an array of 3D points.
#  @returns [point, normal] of plane that best fits points
def fit_points_to_plane(points):
    P = np.array(points)
    rows = P.shape[0]
    
    centroid = P.sum(axis=0) / rows

    #Centered points
    Pc = P - centroid
    
    ones = np.ones(rows).reshape((rows, 1))
    
    # aa = P[:, 0:-1]
    # A = np.hstack((aa, ones))
    A = Pc[:, 0:-1]
    
    b = P[:, -1]
    
    valid, C = least_squares_fit(A, b)
    if valid == False:
        return (False, vecZero, vecZero)
    pos = mathutils.Vector(centroid)
    
    norm = mathutils.Vector((C[0], C[1], -1))
    norm.normalize()
    
    return (True, pos, norm)

# #points is an array of 3D points.
# #  @returns [point, normal] of plane that best fits points
# def fit_points_to_plane2(points):
    # #Equation of plane we're trying to fit is ax + by + cz + d = 0
    # # <a, b, c> is the normal of the plane

    # P = np.array(points)
    # rows = P.shape[0]
    
    # centroid = P.sum(axis=0) / rows

    # #Centered points
    # Pc = P - centroid
    
# #    ones = np.ones(rows).reshape((rows, 1))
    
# #    A = np.hstack((P, ones))
    # A = Pc
    
# #    b = P[:, -1]
    # b = np.zeros(rows).reshape((rows, 1))
    
    # #Coefficients of ax + by + cz + d = 0
    # valid, C = least_squares_fit(A, b)
    # if valid == False:
        # return (False, vecZero, vecZero)
    
    # #Point on plane where x = 0, y = 0
    # pos = mathutils.Vector(centroid)
    
    # norm = mathutils.Vector((C[0], C[1], C[2]))
    # norm.normalize()
    
    # return (True, pos, norm)


class Bounds:
    def __init__(self, point):
        self.minBound = point.copy()
        self.maxBound = point.copy()
        
    def include_point(self, point):
        self.minBound.x = min(self.minBound.x, point.x)
        self.maxBound.x = max(self.maxBound.x, point.x)
        self.minBound.y = min(self.minBound.y, point.y)
        self.maxBound.y = max(self.maxBound.y, point.y)
        self.minBound.z = min(self.minBound.z, point.z)
        self.maxBound.z = max(self.maxBound.z, point.z)
    
    def include_bounds(self, bounds):
        include_point(bounds.minBound)
        include_point(bounds.maxBound)

    def __intersect_edge(self, p0, p1, ray_origin, ray_dir, ray_radius):
        dir = p1 - p0
        s = closest_point_to_line(p0, dir, ray_origin, ray_dir)
        if math.isnan(s):
            return False
        # print("ray_origin " + str(ray_origin))
        # print("ray_dir " + str(ray_dir))
        # print("ray_radius " + str(ray_radius))
            
        # print("p0 " + str(p0))
        # print("p1 " + str(p1))
        # print("s " + str(s))
        
        s = max(min(s, 1), 0)
        p = p0 + s * dir

        # print("p " + str(p))
        
        offset_from_ray_origin = p - ray_origin
        offset_parallel = offset_from_ray_origin.project(ray_dir)
        offset_perp = offset_from_ray_origin - offset_parallel

        # print("offset_perp " + str(offset_perp))
        # print("offset_perp.length " + str(offset_perp.length))
        
        if offset_perp.dot(offset_perp) < ray_radius * ray_radius:
            #We intersect with cube edge
            return True
        return False

    def __intersect_face(self, p0, p1, p2, ray_origin, ray_dir):
        # print ("__intersect_face ")
        # print("p0 " + str(p0))
        # print("p1 " + str(p1))
        # print("p2 " + str(p2))
        # print("ray_origin " + str(ray_origin))
        # print("ray_dir " + str(ray_dir))
    
        v1 = p1 - p0
        v2 = p2 - p0
        normal = v1.cross(v2)
        s = isect_line_plane(ray_origin, ray_dir, p0, normal)
        if s == None:
            #Parallel to face
            return False
        hit = ray_origin + s * ray_dir
        v_hit = hit - p0

#        print("hit " + str(hit))
        
        #Express v_hit as a linear combination of v1 and v2
#        V = mathutils.Matrix(((v1.x, v2.x, normal.x), (v1.y, v2.y, normal.y), (v1.z, v2.z, normal.z)))
        V = mathutils.Matrix((v1, v2, normal))
        if V.determinant() == 0:
            return False
        
        V.transpose()
        V_i = V.inverted()
        co = V_i @ v_hit
        
        if co.x >= 0 and co.x <= 1 and co.y >= 0 and co.y <= 1:
            return True
        
        return False

    def intersect_with_ray(self, ray_origin, ray_dir, ray_radius = 0, boundsXform = None):
        p000 = mathutils.Vector((self.minBound.x, self.minBound.y, self.minBound.z))
        p001 = mathutils.Vector((self.minBound.x, self.minBound.y, self.maxBound.z))
        p010 = mathutils.Vector((self.minBound.x, self.maxBound.y, self.minBound.z))
        p011 = mathutils.Vector((self.minBound.x, self.maxBound.y, self.maxBound.z))
        p100 = mathutils.Vector((self.maxBound.x, self.minBound.y, self.minBound.z))
        p101 = mathutils.Vector((self.maxBound.x, self.minBound.y, self.maxBound.z))
        p110 = mathutils.Vector((self.maxBound.x, self.maxBound.y, self.minBound.z))
        p111 = mathutils.Vector((self.maxBound.x, self.maxBound.y, self.maxBound.z))
        
        # print("p000 " + str(p000))
        # print("p001 " + str(p001))
        # print("p010 " + str(p010))
        # print("p011 " + str(p011))
        # print("p100 " + str(p100))
        # print("p101 " + str(p101))
        # print("p110 " + str(p110))
        # print("p111 " + str(p111))
        
        if boundsXform != None:
            p000 = boundsXform @ p000
            p001 = boundsXform @ p001
            p010 = boundsXform @ p010
            p011 = boundsXform @ p011
            p100 = boundsXform @ p100
            p101 = boundsXform @ p101
            p110 = boundsXform @ p110
            p111 = boundsXform @ p111

        # print("after xform")
        # print("p000 " + str(p000))
        # print("p001 " + str(p001))
        # print("p010 " + str(p010))
        # print("p011 " + str(p011))
        # print("p100 " + str(p100))
        # print("p101 " + str(p101))
        # print("p110 " + str(p110))
        # print("p111 " + str(p111))
        
        #Check for edge intersections
        if ray_radius > 0:
            if self.__intersect_edge(p000, p100, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p000, p010, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p010, p110, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p100, p110, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p000, p001, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p100, p101, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p010, p011, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p110, p111, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p001, p101, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p001, p011, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p011, p111, ray_origin, ray_dir, ray_radius):
                return True
            if self.__intersect_edge(p101, p111, ray_origin, ray_dir, ray_radius):
                return True
        
        if self.__intersect_face(p000, p010, p100, ray_origin, ray_dir):
            return True
        if self.__intersect_face(p000, p001, p100, ray_origin, ray_dir):
            return True
        if self.__intersect_face(p100, p101, p110, ray_origin, ray_dir):
            return True
        if self.__intersect_face(p010, p110, p011, ray_origin, ray_dir):
            return True
        if self.__intersect_face(p000, p001, p010, ray_origin, ray_dir):
            return True
        if self.__intersect_face(p001, p101, p011, ray_origin, ray_dir):
            return True
        
        return False
        
    def __str__(self):
        return "bounds [" + str(self.minBound) + " " + str(self.maxBound) + "]"

def mesh_bounds_fast(obj, world = False):
    bounds = None
    
#    print("mesh_bounds_fast()")
    for co in obj.bound_box:
        pos = mathutils.Vector(co)

#        print("pos " + str(pos))

        if world:
            pos = obj.matrix_world @ pos
            
        if bounds == None:
            bounds = Bounds(pos)
        else:
            bounds.include_point(pos)
    
    return bounds
    
def mesh_bounds(obj, world = True, selected_faces_only = False):

    bounds = None

    mesh = obj.data

    for p in mesh.polygons:
        if selected_faces_only and not p.select:
            continue
            
        for vIdx in p.vertices:
            v = mesh.vertices[vIdx]
            pos = mathutils.Vector(v.co)
            
            if world:
                pos = obj.matrix_world @ pos
                
            if bounds == None:
                bounds = Bounds(pos)
            else:
                bounds.include_point(pos)
            
    return bounds

    
    
def bmesh_bounds(obj, bmesh, world = True, selected_faces_only = False):

    bounds = None
    
    for f in bmesh.faces:
        if selected_faces_only and not p.select:
            continue

        for v in f.verts:
            pos = mathutils.Vector(v.co)
            if world:
                pos = obj.matrix_world @ pos
        
            if bounds == None:
                bounds = Bounds(pos)
            else:
                bounds.include_point(pos)
     
    return bounds


    
    
    
