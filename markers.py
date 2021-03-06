# Some visual feedback
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import maya.cmds as cmds
import maya.api.OpenMaya as om

class Markers(object):
    """
    Create markers for visual feedback
    """
    def __init__(s):
        s.baseName = "MarkerWrapper"
        s.__enter__()

    def __enter__(s):
        if cmds.objExists(s.baseName):
            cmds.delete(s.baseName)
        sel = cmds.ls(sl=True)
        win = cmds.playblast(activeEditor=True)
        cam = cmds.modelEditor(win, q=True, camera=True)
        p1 = om.MVector(cmds.xform(cam, q=True, ws=True, t=True))
        p2 = om.MVector(0,0,0) # Center of world
        scale = (p1 - p2).length()

        s.baseName = cmds.circle(
            r=scale * 0.4,
            n=s.baseName,
            nr= (0,1,0) if cmds.upAxis(q=True, ax=True) == "y" else (0,0,1)
            )[0]
        for at in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz"]:
            cmds.setAttr(s.baseName + at, l=True, k=False, cb=False)
        cmds.addAttr(s.baseName, ln="markerSize", dv=1, k=True)
        cmds.setAttr("%s.markerSize" % s.baseName, scale * 0.005)
        cmds.select(sel, r=True)
        return s.createMarker

    def __exit__(s, *errs):
        if cmds.objExists(s.baseName):
            cmds.delete(s.baseName)

    def createMarker(s, target, name, shape=None, colour=None):
        sel = cmds.ls(sl=True)
        name = "%s_marker" % name
        if cmds.objExists(name):
            cmds.delete(name)
        if shape == "square":
            name = cmds.polyCube(name=name)[0]
        elif shape == "cone" :
            name = cmds.polyCone(name=name)[0]
        elif shape == "cylinder":
            name = cmds.polyCylinder(name=name)[0]
        else:
            name = cmds.polySphere(name=name)[0]
        cmds.parent(name, s.baseName)
        for at in [".sx", ".sy", ".sz"]:
            cmds.connectAttr("%s.markerSize" % s.baseName, name + at, f=True)
        cmds.parentConstraint(target, name)
        cmds.setAttr("%s.overrideEnabled" % name, 1)
        cmds.setAttr("%s.overrideDisplayType" % name, 2)
        cmds.polyColorPerVertex(name, rgb=colour or [1,1,0], cdo=True)
        cmds.select(sel, r=True)
