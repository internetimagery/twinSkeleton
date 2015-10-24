# Parse Rig file and build rig

import json
import warn
import maya.cmds as cmds

def NameSpace(name, prefix=None):
    return prefix + name if prefix else name

def GetRoot():
    return "EXPORT_RIG"

class Joint(dict):
    def __init__(s, name, *args, **kwargs):
        dict.__init__(s, *args, **kwargs)
        s.name = name

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
        s.win = cmds.window(rtf=True, w=300, t="Build Rig")
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

    def buildRig(s, data, prefix):
        with Safe():
            root = NameSpace(GetRoot(), prefix)

            # Parse and Validate
            joints = []
            def parse(data):
                for k in data:
                    if k[:1] != "_":
                        if cmds.objExists(k): raise RuntimeError, "%s already exists. Cannot complete..." % k
                        position = data[k].get("_position", "")
                        rotation = data[k].get("_rotation", "")
                        scale = data[k].get("_scale", "")
                        if not position or not cmds.objExists(position): raise RuntimeError, "%s is missing. Cannot complete..." % position or "An Unspecified Joint"
                        if not rotation or not cmds.objExists(rotation): raise RuntimeError, "%s is missing. Cannot complete..." % rotation or "An Unspecified Joint"
                        if not scale or not cmds.objExists(scale): raise RuntimeError, "%s is missing. Cannot complete..." % scale or "An Unspecified Joint"
                        j = Joint(k, data[k])
                        joints.append(j)
                        data[k] = j
                        parse(data[k])
            parse(data)

            # Check if root is there. IF so, use it, else create
            if not cmds.objExists(root):
                cmds.group(n=root, em=True)

            # Lay out our joints
            for j in joints:
                position = j["_position"]
                name = NameSpace(j.name, prefix)
                pos = cmds.xform(position, q=True, t=True, ws=True)
                cmds.select(cl=True)
                j.joint = cmds.joint(name=name, p=pos)
                j.pos = pos

            # Form heirarchy
            upAxis = "%sup" % cmds.upAxis(q=True, ax=True)
            def layout(j, parent=None):
                if parent:
                    cmds.parent(j.joint, parent)
                else:
                    cmds.parent(j.joint, root)
                children = [b for a, b in j.items() if a[:1] != "_"]
                childNum = len(children) # How many children have we?
                if childNum:
                    for c in children:
                        layout(c, j.joint)
                    if childNum == 1: # Part of a limb
                        cmds.joint(
                            j.joint,
                            e=True,
                            zeroScaleOrient=True,
                            orientJoint="xyz",
                            secondaryAxisOrient=upAxis
                            )
                    else: # Base of a limb
                        cmds.xform(
                            j.joint,
                            p=True,
                            roo=j.get("_rotationOrder", "xyz")
                            )
                        cmds.pointConstraint(j["_position"], j.joint, mo=True)
                else: # End of a limb
                    pass
                cmds.orientConstraint(j["_rotation"], j.joint, mo=True)
                cmds.scaleConstraint(j["_scale"], j.joint, mo=True)
            for k in data:
                layout(data[k])

            cmds.confirmDialog(t="Wohoo!", m="Rig was built successfully")