#!/usr/bin/env python

# This file is part of the Kitfox Normal Brush distribution (https://github.com/blackears/blenderTerrainSculpt).
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

import os
import shutil
import sys
import getopt
import platform

def copytree(src, dst):
    for item in os.listdir(src):
    
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                os.mkdir(d)
            copytree(s, d)
        else:
            filename, extn = os.path.splitext(item)
            print ("file " + filename + " extn  " + extn)
            if (extn != ".py" and extn != ".png"):
                continue
                
            shutil.copy(s, d)

def make(copyToBlenderAddons = False, createArchive = False, rebuildLibs = False):
    projectName = 'terrainSculptTools'
    
    blenderHome = None
    # platSys = platform.system()
    # if platSys == 'Windows':
        # appData = os.getenv('APPDATA')
        # blenderHome = os.path.join(appData, "Blender Foundation/Blender/2.91")
        
    # elif platSys == 'Linux':
        # home = os.getenv('HOME')
        # blenderHome = os.path.join(home, ".config/blender/2.91/")


    blenderHome = os.getenv('BLENDER_HOME')

    #Rebuild library directory
    if rebuildLibs:
        if os.path.exists('lib'):
            shutil.rmtree('lib')
        os.mkdir('lib')
        copytree("../blenderCommon/source", "lib")
        

    #Create build directory
    curPath = os.getcwd()
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.mkdir('build')
    os.mkdir('build/' + projectName)

    copytree("source", "build/" + projectName)
#    copytree("../blenderCommon/source", "build/" + projectName)
    copytree("lib", "build/" + projectName)

    
    #Build addon zip file
    if createArchive: 
        if os.path.exists('deploy'):
            shutil.rmtree('deploy')
        os.mkdir('deploy')

        shutil.make_archive("deploy/" + projectName, "zip", "build")


    if copyToBlenderAddons: 
        if blenderHome == None:
            print("Error: BLENDER_HOME not set.  Files not copied to <BLENDER_HOME>/script/addons.")
            return
        
        addonPath = os.path.join(blenderHome, "scripts/addons")
        destPath = os.path.join(addonPath, projectName)

        print("Copying to blender addons: " + addonPath)
        if os.path.exists(destPath):
            shutil.rmtree(destPath)
        copytree("build", addonPath);


if __name__ == '__main__':
    copyToBlenderAddons = False
    createArchive = False
    rebuildLibs = False

    for arg in sys.argv[1:]:
        if arg == "-a":
            createArchive = True
        if arg == "-b":
            copyToBlenderAddons = True
        if arg == "-l":
            rebuildLibs = True

    make(copyToBlenderAddons, createArchive, rebuildLibs)
            
