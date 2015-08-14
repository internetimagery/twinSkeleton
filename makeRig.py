# Parse Rig file and build rig

import maya.cmds as cmds
from json import load

class MakeRig(object):
    def __init__(s):
        winName = "Make_Rig"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Build Rig")
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=2)
        cmds.text(l="(optional) Prefix:")
        s.prefix = cmds.textField()
        cmds.setParent("..")
        cmds.button(l="Load Template and Build Rig", h=100, c=s.checkFile)
        cmds.showWindow(s.win)

    def checkFile(s, *junk):
        prefix = cmds.textField(s.prefix, q=True, tx=True).strip()
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
        def name(n):
            return "%s_%s" % (prefix, n) if prefix else n
        root = name("Basic_Rig")

        # check objects
        for jnt in data:
            target = data[jnt]["target"]
            joint = name(jnt)
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
            joint = name(jnt)
            pos = cmds.xform(target, q=True, t=True, ws=True)
            cmds.select(cl=True)
            cmds.joint(name=joint, p=pos)
            cmds.parentConstraint(target, joint, mo=True)

        # Parent Joints
        for jnt in data:
            parent = data[jnt]["parent"]
            joint = name(jnt)
            if parent:
                cmds.parent(joint, parent)
            else:
                cmds.parent(joint, root)

        cmds.confirmDialog(t="Wohoo!", m="Rig was built successfully")
