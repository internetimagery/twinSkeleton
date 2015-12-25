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

import re
import report
import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om
from contextlib import contextmanager

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
ZERO = om.MVector(0,0,0)
RESET = {
    "aimConstraint": lambda x: cmds.aimConstraint(x, e=True, mo=True),
    "pointConstraint": lambda x: cmds.pointConstraint(x, e=True, mo=True),
    "orientConstraint": lambda x: cmds.orientConstraint(x, e=True, mo=True),
    "parentConstraint": lambda x: cmds.parentConstraint(cmds.parentConstraint(x, q=True, tl=True), x, e=True, mo=True)
}

def SetColour(obj, colour):
    """
    Set an object to a certain colour.
    """
    cmds.setAttr("%s.overrideEnabled" % obj, 1)
    cmds.setAttr("%s.overrideColor" % obj, colour)

def ListConstraints(obj):
    """
    Get a list of constraints attached to a joint
    """
    channels = r"\.(translate|rotate|scale)(X|Y|Z)$"
    incoming = cmds.listConnections(obj, c=True, d=False, type="constraint") or []
    return set(b for a, b in zip(incoming[0:-1:2], incoming[1:-1:2]) if re.search(channels, a))

@contextmanager
def ReSeat(joints):
    """ Allow movement of Joints. """
    skins = set(cmds.listConnections(joints, type="skinCluster", s=True) or [])
    for sk in skins:
        cmds.skinCluster(sk, e=True, mjm=True) # Turn off skin
    try:
        yield
    finally:
        for sk in skins:
            cmds.skinCluster(sk, e=True, mjm=False) # Turn on skin

@contextmanager
def Isolate(joint):
    """ Separate a Joint from the skeleton to move it safely. """
    children = cmds.listRelatives(joint, c=True, type="joint") or []
    childrenPos = [cmds.xform(a, q=True, ws=True, m=True) for a in children]
    if children: cmds.parent(children, w=True)
    try:
        yield
    finally: # Put it all back
        for ch, pos in zip(children, childrenPos):
            cmds.parent(ch, joint)
            cmds.xform(ch, ws=True, m=pos)

class Callback(object):
    """ Simple callback """
    def __init__(s, func, *args, **kwargs): s.__dict__.update(**locals())
    def __call__(s, *_): return s.func(*s.args, **s.kwargs)

class Helper(object):
    """
    Helper marker to orient Joint
    """
    def __init__(s, joint):
        s.joint = joint
        s.marker, s.wrapper = s.formMarker(joint)

    def formMarker(s, joint):
        """
        Create a marker to easily modify joint rotations.
        """
        win = cmds.playblast(activeEditor=True) # Viewport
        cam = cmds.modelEditor(win, q=True, camera=True) # Camera
        p1 = om.MVector(cmds.xform(cam, q=True, ws=True, t=True)) # Cam pos
        p2 = om.MVector(0,0,0) # Center of world
        scale = ((p2 - p1).length()) * 0.15
        wrapper = cmds.group(em=True) # Hold position
        marker = cmds.group(em=True)
        cmds.scale(scale, scale, scale, marker)
        cmds.parent(marker, wrapper)
        for ax in AXIS: # Build Axis
            pos = AXIS[ax]
            c = cmds.curve(p=((0,0,0), pos), d=1)
            shape = cmds.listRelatives(c, s=True)[0]
            SetColour(shape, AXISCOLOUR[ax])
            cmds.parent(shape, marker, s=True, r=True)
            cmds.delete(c)
        cmds.parentConstraint(joint, wrapper)
        ro = cmds.xform(joint, q=True, ws=True, ro=True)
        roo = cmds.xform(joint, q=True, roo=True)
        cmds.xform(marker, roo=roo)
        cmds.xform(marker, ro=ro, ws=True)
        children = cmds.listRelatives(joint, type="joint") or [] # if not a leaf joint, aim at child
        if len(children) == 1: # If we are already pointing at child, retain aim
            matrix = zip(*[iter(cmds.xform(joint, ws=True, q=True, m=True))]*4)
            child_pos = om.MVector(cmds.xform(children[0], q=True, ws=True, t=True))
            parent_pos = om.MVector(matrix[3][:3])
            aim_vec = child_pos - parent_pos
            for i, axis in enumerate(matrix[:3]):
                vec = om.MVector(axis[:3])
                if vec.isParallel(aim_vec): # We found our pointing axis
                    ax = [[1 if a == b else 0 for a in range(3)] for b in range(3)]
                    aim = ax[i]
                    up = ax[1 if i != 1 else 2] # Up Y or Z
                    cmds.aimConstraint(
                        children[0],
                        marker,
                        aim=aim,
                        u=up,
                        skip="xyz"[i],
                        wut="vector",
                        wu=up
                    )
        cmds.select(marker, r=True)
        return marker, wrapper

    def setJoint(s):
        """
        Move joint into location.
        """
        # Local
        pos = om.MVector(cmds.xform(s.marker, q=True, t=True)) # Position
        rot = om.MVector(cmds.xform(s.marker, q=True, ro=True)) # Rotation

        if not pos.isEquivalent(ZERO) or not rot.isEquivalent(ZERO): # Check for changes

            # Move Joint into position
            cmds.xform(s.joint,
                ws=True,
                t=cmds.xform(s.marker, q=True, t=True, ws=True),
                ro=cmds.xform(s.marker, q=True, ro=True, ws=True)
                )

            # Reset Marker
            cmds.xform(s.marker, t=ZERO, ro=ZERO)

            # Update Constraints
            for con in ListConstraints(s.joint):
                _type = cmds.objectType(con)
                if _type in RESET:
                    RESET[_type](con)

    def removeMarker(s):
        """
        Delete marker
        """
        if cmds.objExists(s.wrapper): cmds.delete(s.wrapper)


class JointTracker(object):
    """
    Track and rotate joints
    """
    def __init__(s):
        s.markers = {}

    @report.Report()
    def addMarker(s):
        """
        Add a new marker to the joint
        """
        sel = cmds.ls(sl=True, type="joint")
        if sel:
            for joint in sel:
                if joint not in s.markers:
                    s.markers[joint] = Helper(joint)
        else:
            cmds.confirmDialog(t="Oh no...", m="You must select some Joints.")

    def removeMarkers(s):
        """
        Remove remaining markers
        """
        for j, m in s.markers.items(): m.removeMarker()

    @report.Report()
    def orientJoints(s):
        """
        Face joints in the correct direction.
        """
        sel = cmds.ls(sl=True)
        err = cmds.undoInfo(openChunk=True)
        try:
            markers = s.markers
            joints = markers.keys()
            with ReSeat(joints):
                for j in joints:
                    m = markers[j]
                    if cmds.objExists(m.marker) and cmds.objExists(j):
                        with Isolate(j):
                            m.setJoint()
                            try:
                                cmds.makeIdentity(
                                    j,
                                    apply=True,
                                    r=True) # Freeze Rotations
                            except RuntimeError:
                                pass
                    else: # User deleted marker / joint. Stop tracking.
                        m.removeMarker()
                        del markers[j]
                cmds.select(sel, r=True)
        except Exception as err:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
            if err: cmds.undo()

class Window(object):
    """
    Main window for tool
    """
    def __init__(s):
        with report.Report():
            tracker = JointTracker()
            winName = "Orient_Joints"
            if cmds.window(winName, ex=True):
                cmds.deleteUI(winName)
            s.win = cmds.window(rtf=True, w=300, t="Orient Joints")
            cmds.columnLayout(adj=True)
            cmds.button(
                l="Attach Marker",
                h=50,
                c=Callback(tracker.addMarker),
                ann="""
Attach a Marker to the selected Joint.
Rotate the marker into the desired joint rotation.
"""
            )
            cmds.button(
                l="Update Joints",
                h=50,
                c=Callback(tracker.orientJoints),
                ann="""
Rotate all joints that have markers to their respective rotations.
"""
            )
            cmds.showWindow(s.win)
            cmds.scriptJob(uid=[s.win, tracker.removeMarkers])

if __name__ == '__main__':
    Window()
