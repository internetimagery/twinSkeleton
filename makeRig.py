# Parse Rig file and build rig

import maya.cmds as cmds
import re

class MakeRig(object):
    def __init__(s):
        winName = "Make_Rig"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Build Rig")
        cmds.columnLayout(adj=True)
        cmds.button(l="Load Template and Build Rig", h=100, c=s.parseFile)
        cmds.showWindow(s.win)

    def parseFile(s, *junk):
        fileFilter = "Rig Templates (*.rig)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Save file
        if path:
            try:
                with open(path[0], "r") as f:
                    reg = re.compile("^([\/\w]+)[\s=]+([\w\|]+)")
                    data = {}
                    for line in f.readlines():
                        parse = reg.match(line)
                        if parse:
                            path = list(reversed(parse.group(1).split("/")))
                            data[path[0]] = {
                                "parent" : path[1],
                                "target" : parse.group(2)
                            }

                        else:
                            cmds.confirmDialog(t="Uh oh...", m="There was a problem reading the file...")
                            return
                    s.buildRig(data)
                    cmds.deleteUI(s.win)
            except IOError:
                cmds.confirmDialog(t="Uh oh...", m="There was a problem reading the file...")

    def buildRig(s, data):
        # check objects
        for joint in data:
            target = data[joint]["target"]
            if cmds.objExists(joint):
                cmds.confirmDialog(t="Object exists", m="%s already exists. Cannot complete..." % joint)
                return
            if not cmds.objExists(target):
                cmds.confirmDialog(t="Missing Object", m="%s is missing. Cannot complete..." % target)
                return
        root = "Basic_Rig"
        if cmds.objExists(root):
            cmds.delete(root)
        cmds.group(n=root)

        # Create Joints
        for joint in data:
            target = data[joint]["target"]
            pos = cmds.xform(target, q=True, t=True, ws=True)
            cmds.joint(name=joint, p=pos)
            # cmds.parentConstraint(target, joint)

        # Parent Joints
        for joint in data:
            parent = data[joint]["parent"]
            if parent:
                cmds.parent(joint, parent)
            else:
                cmds.parent(joint, root)

        print "Rig Built"



MakeRig()
