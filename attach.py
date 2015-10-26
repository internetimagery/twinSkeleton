# Parse Rig file and build rig

import json
# import warn
import SimpleBaseRigGITHUB.warn as warn
# import vector
import SimpleBaseRigGITHUB.vector as vector
import collections
import maya.cmds as cmds

AIM_AXIS = Vector(1,0,0) # X axis
WORLD_AXIS = Vector(0,1,0) if cmds.upAxis(q=True, ax=True) == "y" else Vector(0,0,1)

def NameSpace(name, prefix=None):
    return prefix + name if prefix else name

def GetRoot():
    return "EXPORT_RIG"

class Joint(object):
    def __init__(s, name, data):
        s.name = name
        s.targets = dict((a[1:], b) for a, b in data.items() if a[:1] == "_")
        if s.targets.get("position", None):
            if cmds.objExists(s.targets["position"]):
                if not cmds.objExists(name):
                    s.position = vector.Vector(*cmds.xform(data["_position"], q=True, rp=True, ws=True))
                    cmds.select(clear=True)
                    s.joint = cmds.joint(
                        name=name,
                        p=s.position
                    )
                else: raise RuntimeError, "%s Joint already exists." % s.name
            else: raise RuntimeError, "%s Joint target missing: %s" % (s.name, data["_position"])
        else: raise RuntimeError, "%s Joint could not be created." % s.name
    def attach(s, position=None, rotation=None, scale=None):
            if position:
                cmds.pointConstraint(s.targets["position"], s.joint, mo=True)
            if rotation:
                cmds.orientConstraint(s.targets["rotation"], s.joint, mo=True)
            if scale:
                cmds.scaleConstraint(s.targets["scale"], s.joint, mo=True)
    def __repr__(s): return "Joint %s at %s" % (s.name, s.position)

class Limb(collections.MutableSequence):
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
                p2,
                p1,
                aim=AIM_AXIS,
                upVector=WORLD_AXIS,
                worldUpVector=vector,
                worldUpType="vector",
                weight=1.0
            ))
        def attach(j1, j2):
            cmds.parent(j2, j1)
            cmds.joint(j1, e=True, zso=True)
            cmds.makeIdentity(j1, apply=True)

        if 1 < jointNum: # Nothing to rotate if only a single joint
            if jointNum == 2: # We don't have enough joints to aim fancy
                orient(s.joints[0].joint, s.joints[1].joint, WORLD_AXIS)
                attach(s.joints[1].joint, s.joints[1].joint)
            else:
                prev = vector.Vector(0,0,0)
                for i in range(jointNum - 2):
                    j1, j2, j3 = s.joints[i], s.joints[i + 1], s.joints[i + 2]

                    v1 = j1.position - j2.position
                    v2 = j3.position - j2.position
                    v3 = v1.cross(v2).normalized or prev or WORLD_AXIS

                    if not i: orient(j1.joint, j2.joint, v3) # Don't forget to aim the root!
                    orient(j2.joint, j3.joint, v3)

                    dot = v3.dot(prev)
                    prev = v3

                    if i and dot <= 0:
                        cmds.xform(j2.joint, r=True, os=True, ro=AIM_AXIS * (180,180,180))
                        prev = -prev

                    if not i: attach(j1.joint, j2.joint)
                    attach(j2.joint, j3.joint)


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
        row = cmds.rowLayout(nc=3, adj=1)
        cmds.separator()
        cmds.button(
            l="Add Prefix",
            c=lambda x: warn(s.buildRig, data, cmds.textField(prefix, q=True, tx=True).strip()))
        cmds.button(
            l="No Prefix",
            c=lambda x: warn(s.buildRig, data, ""))
        cmds.showWindow(s.win)


        cmds.deleteUI(s.win)
        s.buildRig(data, "")

    def buildRig(s, data, prefix):
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
                        limb.append(
                            Joint(
                                NameSpace(c, prefix),
                                data[c]
                                )
                            )
                        parse(data[c], c, limb)
                    else:
                        joints = {}
                        for c in children:
                            joints[c] = Joint(NameSpace(c, prefix), data[c])
                        # TODO Add checks for extending limbs
                        for c, j in joints.items():
                            l = Limb(last)
                            l.append(j)
                            skeleton.append(l)
                            parse(data[c], c, l)

                        #
                        # if limb:
                        #     pos = {
                        #         "X" :[a.position[0] for a in joints],
                        #         "Y" :[a.position[1] for a in joints],
                        #         "Z" :[a.position[2] for a in joints]
                        #         }
                        #     print min(pos["X"]), max(pos["X"])

            parse(data, root)

            for limb in skeleton:
                limb.build()
                for i, j in enumerate(limb):
                    if i:
                        j.attach(False, True, True) # Attach rotation / scale
                    else:
                        cmds.parent(j.joint, limb.parent) # Joint root of limb to parent
                        j.attach(True, True, True) # Attach everything

            print "-"*20
            raise Exception, "cleanup for testing"

            cmds.confirmDialog(t="Wohoo!", m="Skeleton was built successfully")

import os.path
path = r"D:\Dropbox\Dying Ember\Dying Ember\assets\Rig Structure Files\Human\Advanced Skeleton.skeleton"
# path = "/home/maczone/Dropbox/Dying Ember/Dying Ember/assets/Rig Structure Files/Human/Advanced Skeleton.skeleton"
with open(path, "r") as f:
    data = json.load(f)
    Attach(data)
