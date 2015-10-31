# Parse Rig file and build rig

import re
import json
import warn
import collections
import maya.cmds as cmds
from vector import Vector

AXIS = {
    "x" : Vector(1,0,0),
    "y" : Vector(0,1,0),
    "z" : Vector(0,0,1)
    }
WORLD_AXIS = AXIS[cmds.upAxis(q=True, ax=True)]

def NameSpace(name, prefix=None):
    return prefix + name if prefix else name

def GetRoot():
    return "EXPORT_RIG"

def stretch(jnt1, jnt2):
    axis = ["X", "Y", "Z"]
    exclude = jnt1.roo[0].upper()
    if exclude in axis: axis.remove(exclude)
    # Track Distance between joints
    dist = cmds.shadingNode(
        "distanceBetween",
        n="%s_dist" % jnt1.name,
        asUtility=True
        )
    cmds.connectAttr(
        "%s.translate" % jnt1.joint,
        "%s.point1" % dist,
        force=True
        )
    cmds.connectAttr(
        "%s.translate" % jnt2.joint,
        "%s.point2" % dist,
        force=True
        )
    mult1 = cmds.shadingNode(
        "multiplyDivide",
        n="%s_mult" % jnt1.name,
        asUtility=True
        )
    cmds.setAttr("%s.operation" % mult1, 2)
    cmds.setAttr("%s.input1X" % mult1, cmds.getAttr("%s.distance" % dist))
    cmds.connectAttr(
        "%s.distance" % dist,
        "%s.input2X" % mult1,
        force = True
        )
    # Reduce the distance value proportionately
    mult2 = cmds.shadingNode(
        "multiplyDivide",
        n="%s_reduce" % jnt1.name,
        asUtility=True
        )
    cmds.setAttr("%s.operation" % mult2, 3)
    cmds.connectAttr(
        "%s.outputX" % mult1,
        "%s.input1X" % mult2,
        force = True
        )
    cmds.setAttr("%s.input2X" % mult2, 0.5)
    # Connect the value to our joint
    for ax in axis:
        cmds.connectAttr(
            "%s.outputX" % mult2,
            "%s.scale%s" % (jnt1.joint, ax),
            force=True
            )

class Joint(object):
    axis = False
    def __init__(s, name, data, pin=False):
        s.name = name
        s.pin = pin # If we will attach by position as well as rotation/scale
        s.targets = {}
        s.targets["position"] = data.get("_position", None)
        s.targets["rotation"] = data.get("_rotation", None)
        s.targets["scale"] = data.get("_scale", None)
        s.roo = data.get("_rotationOrder", None) or "xyz"
        if s.targets["position"] and s.targets["rotation"] and s.targets["scale"]:
            if cmds.objExists(s.targets["position"]):
                if not cmds.objExists(name):
                    s.position = Vector(*cmds.xform(s.targets["position"], q=True, rp=True, ws=True))
                    cmds.select(clear=True)
                    s.joint = cmds.joint(
                        name=name,
                        p=s.position
                    )
                    cmds.xform(s.joint, p=True, roo=s.roo)
                    if s.axis: cmds.setAttr("%s.displayLocalAxis" % s.joint, 1)
                else: raise RuntimeError, "%s Joint already exists." % s.name
            else: raise RuntimeError, "%s Joint target missing: %s" % (s.name, s.targets["position"])
        else: raise RuntimeError, "%s Joint could not be created." % s.name
    def __repr__(s): return "Joint %s at %s" % (s.name, s.position)

class Limb(collections.MutableSequence):
    flipping = True # Do we prevent flipping?
    stretch = False # Do we want stretchy joints?
    def __init__(s, parent):
        s.parent = parent # Where does this limb attach?
        s.joints = []
    def __getitem__(s, k): return s.joints[k]
    def __setitem__(s, k, v): s.joints[k] = v
    def __delitem__(s, k): del s.joints[k]
    def __len__(s): return len(s.joints)
    def insert(s, k, v): s.joints.insert(k, v)
    def __repr__(s): return "Limb %s" % ", ".join(a.name for a in s.joints)
    def build(s):
        jointNum = len(s.joints)
        def orient(p1, p2, vector):
            cmds.delete(cmds.aimConstraint(
                p2.joint,
                p1.joint,
                aim=AXIS[p1.roo[0]],
                upVector=AXIS[p1.roo[1]],
                worldUpVector=vector,
                worldUpType="vector",
                weight=1.0
            ))
        def attach(j1, j2):
            cmds.parent(j2.joint, j1.joint)
            cmds.joint(j1.joint, e=True, zso=True)
            cmds.makeIdentity(j1.joint, apply=True)
            if j1.pin or s.stretch:
                cmds.pointConstraint(j1.targets["position"], j1.joint, mo=True)
            cmds.orientConstraint(j1.targets["rotation"], j1.joint, mo=True)
            if s.stretch:
                stretch(j1, j2)
            else:
                cmds.scaleConstraint(j1.targets["scale"], j1.joint, mo=True)

        if 1 < jointNum: # Nothing to rotate if only a single joint
            if jointNum == 2: # We don't have enough joints to aim fancy
                orient(s.joints[0], s.joints[1], WORLD_AXIS)
                attach(s.joints[0], s.joints[1])
            else:
                prev = Vector(0,0,0)
                for i in range(jointNum - 2):
                    j1, j2, j3 = s.joints[i], s.joints[i + 1], s.joints[i + 2]

                    v1 = j1.position - j2.position
                    v2 = j3.position - j2.position
                    v3 = v1.cross(v2).normalized or prev or WORLD_AXIS


                    if not i: orient(j1, j2, v3) # Don't forget to aim the root!
                    orient(j2, j3, v3)

                    if i and v3.dot(prev) <= 0.0 and s.flipping:
                        cmds.xform(j2.joint, r=True, os=True, ro=j2.targets["rotationOrder"] * (180,180,180))
                        prev = -v3
                    else:
                        prev = v3

                    if not i: attach(j1, j2)
                    attach(j2, j3)


def cleanup(joints):
    for j in joints:
        cmds.joint(j, e=True, zso=True)
        cmds.makeIdentity(j, apply=True)


class Safe(object):
    def __enter__(s):
        cmds.undoInfo(openChunk=True)
    def __exit__(s, *err):
        cmds.select(clear=True)
        cmds.undoInfo(closeChunk=True)
        if err[0]: cmds.undo()

class Attach(object):
    def __init__(s, data):
        winName = "Make_Rig"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Attach Skeleton")
        cmds.columnLayout(adj=True)
        cmds.text(l="Do you need to add a prefix? (optional)")
        prefix = cmds.textField(h=30)
        orient = cmds.checkBox(h=30, l="Orient Junctions", v=True)
        flipping = cmds.checkBox(h=30, l="Prevent Flipping", v=True)
        # stretch = cmds.checkBox(h=30, l="Stretchy Joints", v=False)
        axis = cmds.checkBox(h=30, l="Display Axis", v=False)
        cmds.button(
            l="ATTACH",
            h=50,
            c=lambda x: warn(
                s.buildRig,
                data,
                cmds.textField(prefix, q=True, tx=True).strip(),
                cmds.checkBox(orient, q=True, v=True),
                cmds.checkBox(flipping, q=True, v=True),
                False,#cmds.checkBox(stretch, q=True, v=True),
                cmds.checkBox(axis, q=True, v=True)
                ))
        cmds.showWindow(s.win)

    def buildRig(s, data, prefix="", orientJunctions=False, flipping=True, stretch=False, axis=False):
        cmds.deleteUI(s.win)
        prefix = re.sub(r"[^a-zA-Z0-9]", "_", prefix)
        Limb.flipping = flipping
        Limb.stretch = stretch
        Joint.axis = axis
        print "Orient Junctions %s." % "on" if orientJunctions else "off"
        with Safe():
            root = NameSpace(GetRoot(), prefix)

            # Check if root is there. IF so, use it, else create
            if not cmds.objExists(root):
                cmds.group(n=root, em=True)

            skeleton = []
            def parse(data, last, limb=None):
                children = [a for a in data if a[:1] != "_"]
                childNum = len(children) # How many children have we?
                if childNum:
                    if childNum == 1 and limb:
                        c = children[0]
                        j = Joint(NameSpace(c, prefix), data[c])
                        limb.append(j)
                        parse(data[c], j, limb)
                    else:
                        joints = {}
                        for c in children:
                            joints[c] = Joint(NameSpace(c, prefix), data[c], True)

                        if limb and orientJunctions: # Continue junctions in limb
                            pos = last.position
                            dist = dict((b.position.distance(pos), a) for a, b in joints.items())
                            furthest = dist[max([a for a in dist])]
                            j = joints.pop(furthest)
                            limb.append(j)
                            parse(data[furthest], j, limb)

                        root = not isinstance(last, Joint) # Special treatment for root
                        prev = last if root else last.joint # We first pipe in a name, not a joint
                        for c, j in joints.items():
                            l = Limb(prev)
                            l.append(j)
                            skeleton.append(l)
                            parse(data[c], j, None if root else l)
            parse(data, root)

            for limb in skeleton:
                limb.build()
                print limb
                for i, j in enumerate(limb):
                    if not i:
                        cmds.parent(j.joint, limb.parent) # Joint root of limb to parent

            cmds.confirmDialog(t="Wohoo!", m="Skeleton was built successfully")
