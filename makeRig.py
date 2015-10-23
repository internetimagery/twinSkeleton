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

class MakeRig(object):
    def __init__(s):
        winName = "Make_Rig"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Build Rig")
        cmds.columnLayout(adj=True)
        row = cmds.rowLayout(nc=2, adj=2)
        cmds.columnLayout(adj=True, p=row)
        cmds.text(h=30, l="(optional) Prefix: ")
        cmds.columnLayout(h=100)
        cmds.columnLayout(adj=True, p=row)
        s.prefix = cmds.textField(h=30)
        cmds.button(l="Load and attach Rig", h=100, c= lambda x: warn.run(s.checkFile))
        cmds.showWindow(s.win)

    def checkFile(s):
        prefix = cmds.textField(s.prefix, q=True, tx=True).strip()
        fileFilter = "Rig Files (*.rig)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Save file
        if path:
            try:
                with open(path[0], "r") as f:
                    data = json.load(f)
                    s.buildRig(data, prefix)
                    cmds.deleteUI(s.win)
            except IOError, ValueError:
                raise RuntimeError, "There was a problem reading the file..."

    def buildRig(s, data, prefix):
        root = NameSpace(GetRoot(), prefix)

        # Parse and Validate
        joints = []
        def parse(data):
            for k in data:
                if k[:1] != "_":
                    j = Joint(k, data[k])
                    target = j.get("_target", "")
                    if cmds.objExists(k): raise RuntimeError, "%s already exists. Cannot complete..." % k
                    if not target or not cmds.objExists(target): raise RuntimeError, "%s is missing. Cannot complete..." % target or "An Unspecified Joint"
                    joints.append(j)
                    data[k] = j
                    parse(data[k])
        parse(data)

        # Check if root is there. IF so, use it, else create
        if not cmds.objExists(root):
            cmds.group(n=root, em=True)

        # Lay out our joints
        for j in joints:
            target = j["_target"]
            name = NameSpace(j.name, prefix)
            pos = cmds.xform(target, q=True, t=True, ws=True)
            cmds.select(cl=True)
            j.joint = cmds.joint(name=name, p=pos)

        # Form heirarchy
        upAxis = "%sup" % cmds.upAxis(q=True, ax=True)
        def layout(j, parent=None):
            if parent:
                cmds.parent(j.joint, parent)
            else:
                cmds.parent(j.joint, root)
            children = [a for a in j if a[:1] != "_"]
            childNum = len(children) # How many children have we?
            if childNum:
                if childNum == 1: # Are we part of a limb?
                    cmds.joint(
                        j.joint,
                        e=True,
                        zeroScaleOrient=True,
                        orientJoint=j.get("_rotationOrder", "xyz"),
                        secondaryAxisOrient=upAxis
                        )
                for k in j:
                    layout(j[k], k)
            cmds.parentConstraint(j["_target"], j.joint, mo=True)
        for j in data.values():
            layout(j)

        cmds.confirmDialog(t="Wohoo!", m="Rig was built successfully")
