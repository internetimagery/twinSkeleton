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

# import warn
import twinSkeleton.warn as warn
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
SUPPORTEDCONSTRAINTS = [
    "orientConstraint",
    "pointConstraint",
    "parentConstraint",
]

def SetColour(obj, colour):
    """
    Set an object to a certain colour.
    """
    cmds.setAttr("%s.overrideEnabled" % obj, 1)
    cmds.setAttr("%s.overrideColor" % obj, colour)

def GetConstraints(joint):
    """
    Get Translation and Rotation constraints
    """
    # Set up channel names
    rotateChannels = ["%s.%s" % (joint, a) for a in ["rotateX", "rotateY", "rotateZ"]]
    positionChannels = ["%s.%s" % (joint, a) for a in ["translateX", "translateY", "translateZ"]]
    connections = cmds.listConnections(joint, type="constraint", c=True, d=True) or []
    rotateConnections = set(connections[i*2+1] for i in range(len(connections) / 2) if connections[i*2] in rotateChannels)
    positionConnections = set(connections[i*2+1] for i in range(len(connections) / 2) if connections[i*2] in positionChannels)

    return positionConnections, rotateConnections


class Helper(object):
    """
    Helper marker to orient Joint
    """
    def __init__(s, joint):
        s.joint = joint
        s.marker, s.wrapper = s.formMarker(joint)
        s.pos = om.MVector(0,0,0)
        s.rot = om.MVector(0,0,0)
        s.changed

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
        cmds.select(marker, r=True)
        return marker, wrapper

    @property
    def changed(s):
        """
        Has marker moved? Update position Info
        """
        if cmds.objExists(s.marker):
            pos = om.MVector(cmds.xform(s.marker, q=True, ws=True, t=True))
            rot = om.MVector(cmds.xform(s.marker, q=True, ws=True, ro=True))
            changed = False if pos == s.pos and rot == s.rot else True
            s.pos = pos
            s.rot = rot
            return changed

    def setJoint(s):
        """
        Move joint into location.
        """
        if s.changed:
            if cmds.objExists(s.joint) and cmds.objExists(s.marker):
                cmds.xform(s.joint, ws=True, t=s.pos, ro=s.rot)
                cmds.xform(s.marker, t=(0,0,0))
                cmds.xform(s.marker, ws=True, ro=s.rot)

    def removeMarker(s):
        """
        Delete marker
        """
        if cmds.objExists(s.wrapper): cmds.delete(s.wrapper)

class ReSeat(object):
    """
    Reseat orient constraint and skin
    """
    def __init__(s, joint):
        s.joint = joint

        orient = dict((a, cmds.orientConstraint(a, q=True, targetList=True)) for a in set(cmds.listConnections(joint, type="orientConstraint", d=True) or []))
        point = dict((a, cmds.pointConstraint(a, q=True, targetList=True)) for a in set(cmds.listConnections(joint, type="pointConstraint", d=True) or []))
        parent = dict((a, cmds.parentConstraint(a, q=True, targetList=True)) for a in set(cmds.listConnections(joint, type="parentConstraint", d=True) or []))

        s.pos = point or parent
        s.rot = orient or parent

        constraints = set(s.pos.keys()) | set(s.rot.keys())

        for c in constraints: cmds.delete(c)

        skin = set(cmds.listConnections(joint, type="skinCluster", s=True) or [])
        s.skin = skin if skin else []
        if s.skin:
            for sk in s.skin:
                cmds.skinCluster(sk, e=True, mjm=True) # Turn off skin
    def __enter__(s): pass
    def __exit__(s, *err):


        for c, t in zip(s.constraint, s.targets):
            cmds.orientConstraint(t, s.joint, mo=True, n=c)
        for sk in s.skin:
            cmds.skinCluster(sk, e=True, mjm=False) # Turn off skin

class Isolate(object):
    def __init__(s, joint):
        s.joint = joint
        s.parent = cmds.listRelatives(joint, p=True, type="joint")
        s.children = cmds.listRelatives(joint, c=True, type="joint")
    def __enter__(s):
        if s.parent and s.children:
            cmds.parent(s.children, s.parent, a=True) # Separate Joint
        elif s.children:
            cmds.parent(s.children, a=True, w=True)
    def __exit__(s, *err):
        if s.children:
            cmds.parent(s.children, s.joint, a=True) # Put them back

class JointTracker(object):
    """
    Track and rotate joints
    """
    def __init__(s):
        s.markers = {}

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
            raise RuntimeError, "You must select some Joints."

    def removeMarkers(s):
        """
        Remove remaining markers
        """
        for j, m in s.markers.items(): m.removeMarker()

    def orientJoints(s):
        """
        Face joints in the correct direction.
        """
        sel = cmds.ls(sl=True)
        cmds.undoInfo(openChunk=True)
        try:
            for j, m in s.markers.items():
                if cmds.objExists(m.marker) and cmds.objExists(j):
                    with Isolate(j):
                        with ReSeat(j):
                            m.setJoint()
                            # cmds.makeIdentity(
                            #     j,
                            #     apply=True,
                            #     r=True) # Freeze Rotations
                else: # User deleted marker / joint. Stop tracking.
                    m.removeMarker()
                    del s.markers[j]
            cmds.select(sel, r=True)
        finally:
            cmds.undoInfo(closeChunk=True)

class Window(object):
    """
    Main window for tool
    """
    def __init__(s):
        tracker = JointTracker()
        winName = "Orient_Joints"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Orient Joints")
        cmds.columnLayout(adj=True)
        cmds.button(
            l="Attach Marker",
            h=50,
            c=(lambda x: warn(tracker.addMarker)),
            ann="""
Attach a Marker to the selected Joint.
Rotate the marker into the desired joint rotation.
"""
        )
        cmds.button(
            l="Orient Joints",
            h=50,
            c=(lambda x: warn(tracker.orientJoints)),
            ann="""
Rotate all joints that have markers to their respective rotations.
"""
        )
        cmds.showWindow(s.win)
        cmds.scriptJob(uid=[s.win, tracker.removeMarkers])

# Window()
