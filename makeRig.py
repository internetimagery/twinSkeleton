# Parse Rig file and build rig

import maya.cmds as cmds
from json import load

def NameSpace(name, prefix=None):
    return prefix + name if prefix else name

def GetRoot():
    return "EXPORT_RIG"

class MakeRig(object):
    def __init__(s):
        winName = "Make_Rig"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Build Rig")
        cmds.columnLayout(adj=True)
        s.prefix = cmds.textFieldGrp(l="(optional) Prefix:")
        cmds.button(l="Load Template and Build Rig", h=100, c=s.checkFile)
        cmds.showWindow(s.win)

    def checkFile(s, *junk):
        prefix = cmds.textFieldGrp(s.prefix, q=True, tx=True).strip()
        fileFilter = "Rig Templates (*.rig)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Save file
        if path:
            try:
                with open(path[0], "r") as f:
                    data = load(f)
                    s.buildRig(data, prefix)
                    cmds.deleteUI(s.win)
            except IOError, ValueError:
                cmds.confirmDialog(t="Uh oh...", m="There was a problem reading the file...")

    def buildRig(s, data, prefix):
        root = NameSpace(GetRoot(), prefix)

        # check objects
        for jnt in data:
            target = data[jnt]["target"]
            joint = NameSpace(jnt, prefix)
            if cmds.objExists(joint):
                cmds.confirmDialog(t="Object exists", m="%s already exists. Cannot complete..." % joint)
                return
            if not cmds.objExists(target):
                cmds.confirmDialog(t="Missing Object", m="%s is missing. Cannot complete..." % target)
                return

        if not cmds.objExists(root):
            cmds.group(n=root, em=True)

        # Create Joints
        for jnt in data:
            target = data[jnt]["target"]
            joint = NameSpace(jnt, prefix)
            pos = cmds.xform(target, q=True, t=True, ws=True)
            cmds.select(cl=True)
            cmds.joint(name=joint, p=pos)
            cmds.parentConstraint(target, joint, mo=True)

        # Parent Joints
        for jnt in data:
            parent = NameSpace(data[jnt]["parent"], prefix)
            joint = NameSpace(jnt, prefix)
            if parent:
                cmds.parent(joint, parent)
            else:
                cmds.parent(joint, root)

        cmds.confirmDialog(t="Wohoo!", m="Rig was built successfully")
