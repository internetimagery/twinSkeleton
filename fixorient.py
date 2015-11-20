# Fix the orientation of Joints if they're oriented incorrectly.
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

AXIS = {
    "x" : om.MVector(1,0,0),
    "y" : om.MVector(0,1,0),
    "z" : om.MVector(0,0,1),
}
AXISCOLOUR = {
    "x" : 13,
    "y" : 14,
    "z" : 15
}

def SetColour(obj, colour):
    """
    Set an object to a certain colour.
    """
    cmds.setAttr("%s.overrideEnabled" % obj, 1)
    cmds.setAttr("%s.overrideColor" % obj, colour)

class Helper(object):
    """
    Helper marker to orient Joint
    """
    def __init__(s, joint):
        s.joint = joint
        s.marker = s.formMarker(joint)

    def formMarker(s, joint):
        """
        Create a marker to easily modify joint rotations.
        """
        name = "Helper_%s" % joint
        if cmds.objExists(name): cmds.delete(name)
        marker = cmds.group(n=name, em=True)
        for ax in AXIS:
            pos = AXIS[ax] * 3
            c = cmds.curve(p=((0,0,0), pos), d=1)
            shape = cmds.listRelatives(c, s=True)[0]
            SetColour(shape, AXISCOLOUR[ax])
            cmds.parent(shape, marker, s=True, r=True)
            cmds.delete(c)
        cmds.pointConstraint(joint, marker)
        ro = cmds.xform(joint, q=True, ws=True, ro=True)
        cmds.xform(marker, ro=ro, ws=True)
        return marker

    def removeMarker(s):
        """
        Delete marker
        """
        if cmds.objExists(s.marker): cmds.delete(s.marker)


sel = cmds.ls(sl=True)
h = Helper(sel[0])
