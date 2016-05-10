# Parse Rig file and build rig
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
import collections
import maya.cmds as cmds
import maya.api.OpenMaya as om

AXISPOS = {"x":0,"y":1,"z":2}
ROOT = "TWIN_SKELETON"

def NameSpace(name, prefix=None):
    return prefix + name if prefix else name

class Joint(object):
    axis = False
    def __init__(s, name, data):
        s.name = name
        s.targets = {}
        s.targets["position"] = data.get("_position", None)
        s.targets["rotation"] = data.get("_rotation", None)
        s.targets["scale"] = data.get("_scale", None)
        s.roo = data.get("_rotationOrder", None) or "xyz"
        if s.targets["position"] and s.targets["rotation"] and s.targets["scale"]:
            if cmds.objExists(s.targets["position"]):
                if not cmds.objExists(name):
                    s.position = om.MVector(cmds.xform(s.targets["position"], q=True, rp=True, ws=True))
                    cmds.select(clear=True)
                    s.joint = cmds.joint(
                        name=name,
                        p=s.position
                    )
                    cmds.xform(s.joint, p=True, roo=s.roo)
                    if s.axis: cmds.setAttr("%s.displayLocalAxis" % s.joint, 1)
                else: raise StopIteration, "Joint already exists: %s" % s.name
            else: raise StopIteration, "Joint target missing: %s" % s.targets["position"]
        else: raise StopIteration, "Joint could not be created: %s" % s.name
    def __repr__(s): return "Joint %s at %s" % (s.name, s.position)
    rotation = property(lambda s: cmds.xform(s.joint, q=True, ws=True, ro=True))

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

        def constrain(joint):
            cmds.joint(joint.joint, e=True, zso=True)
            cmds.makeIdentity(joint.joint, apply=True)
            cmds.orientConstraint(joint.targets["rotation"], joint.joint, mo=True)
            cmds.scaleConstraint(joint.targets["scale"], joint.joint, mo=True)

        def LookAt(aim, up, joint): # Build our matrix
            aim = aim.normalize() # Looking at target
            up = up.normalize() # Primary Rotation
            right = (aim ^ up).normalize() # Nobody likes you third Axis!
            pos = joint.position # Position
            roo = joint.roo # Rotation Order
            if roo in ["xzy", "yxz", "zyx"]: # Axis angles to the left
                right = -right
            matrix = [[],[],[],[pos[0],pos[1],pos[2],1]]
            matrix[AXISPOS[roo[0]]] = [aim[0],aim[1],aim[2],0] # First rotation order
            matrix[AXISPOS[roo[1]]] = [up[0],up[1],up[2],0] # Second rotation order
            matrix[AXISPOS[roo[2]]] = [right[0],right[1],right[2],0] # Third rotation order
            cmds.xform(joint.joint, ws=True, m=[c for r in matrix for c in r]) # Apply Matrix

        if 1 < jointNum: # Nothing to rotate if only a single joint
            if jointNum == 2: # We don't have enough joints to aim fancy
                j2, j3 = s.joints
                aim = j3.position - j2.position
                up = om.MVector(0,1,0) if cmds.upAxis(q=True, ax=True) == "y" else om.MVector(0,0,1)
                LookAt(aim, up, j2)
                cmds.parent(j3.joint, j2.joint)
                constrain(j2)
            else:
                prev = None
                for i in range(jointNum - 2):
                    j1, j2, j3 = s.joints[i], s.joints[i + 1], s.joints[i + 2]

                    tail = j1.position - j2.position
                    aim = j3.position - j2.position
                    up = tail ^ aim

                    # Flip axis if pointed the wrong way
                    if i and s.flipping and up * prev <= 0.0: up = -up
                    prev = up

                    if not i: # Don't forget to aim the root!
                        LookAt(-tail, up, j1)
                        cmds.parent(j2.joint, j1.joint)
                        constrain(j1)

                    LookAt(aim, up, j2) # Aim Joint
                    cmds.parent(j3.joint, j2.joint) # Join Limb
                    constrain(j2)

            # rotate last joint
            LookAt(aim, up, j3)
            constrain(j3)
        else:
            constrain(s.joints[0])

class Attach(object):
    def __init__(s, data):
        with report.Report():
            winName = "Make_Rig"
            if cmds.window(winName, ex=True):
                cmds.deleteUI(winName)
            s.win = cmds.window(rtf=True, w=300, t="Attach Skeleton")
            cmds.columnLayout(adj=True)
            cmds.text(l="Do you need to add a prefix? (optional)")
            prefix = cmds.textField(h=30, ann="""
Prefixes in here will be transferred onto joint names.
""")
            orient = cmds.checkBox(h=30, l="Orient Junctions", v=True, ann="""
Automatically orient joints with multiple limbs (ie hips, chest).
Turn this off if you get inconsistent rotations in these areas.
""")
            flipping = cmds.checkBox(h=30, l="Prevent Flipping", v=False, ann="""
Keep rotations consitent across limbs.
Turn this on for consistent limb rotations when animating joints.
Leave this off for reliable axis rotations when using this skeleton as a proxy.
""")
            axis = cmds.checkBox(h=30, l="Display Axis", v=False, ann="""
Display joint rotations after build.
Useful for inspection and debugging your rig.
""")
            cmds.button(
                l="ATTACH",
                h=50,
                c=lambda x: s.buildRig(
                    data,
                    cmds.textField(prefix, q=True, tx=True).strip(),
                    cmds.checkBox(orient, q=True, v=True),
                    cmds.checkBox(flipping, q=True, v=True),
                    cmds.checkBox(axis, q=True, v=True)
                    ))
            cmds.showWindow(s.win)

    @report.Report()
    def buildRig(s, data, prefix="", orientJunctions=False, flipping=True, axis=False):
        cmds.deleteUI(s.win)
        prefix = re.sub(r"[^a-zA-Z0-9]", "_", prefix)
        Limb.flipping = flipping
        Joint.axis = axis
        print "Orient Junctions %s." % ("on" if orientJunctions else "off")
        print "Prevent Flipping %s." % ("on" if flipping else "off")
        print "Display Axis %s." % ("on" if axis else "off")
        err = cmds.undoInfo(openChunk=True)
        try:
            root = NameSpace(ROOT, prefix)

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
                            joints[c] = Joint(NameSpace(c, prefix), data[c])

                        if limb and orientJunctions: # Continue junctions in limb
                            pos = last.position
                            dist = dict(( (pos - b.position).length(), a) for a, b in joints.items())
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
                root = limb[0]
                cmds.parent(root.joint, limb.parent) # Joint root of limb to parent
                cmds.pointConstraint(root.targets["position"], root.joint, mo=True)

            cmds.confirmDialog(t="Wohoo!", m="Skeleton was built successfully")
        except StopIteration as stop:
            cmds.confirmDialog(t="Oh no...", m=str(stop))
        except Exception as err:
            raise
        finally:
            cmds.select(clear=True)
            cmds.undoInfo(closeChunk=True)
            if err: cmds.undo()

if __name__ == '__main__':
    # Testing
    import json
    fileFilter = "Skeleton Files (*.skeleton)"
    path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Open file
    if path:
        with open(path[0], "r") as f:
            Attach(json.load(f))
