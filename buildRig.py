# Build rig file from existing rig

import json
# import warn
import SimpleBaseRigGITHUB.warn as warn
import maya.cmds as cmds

class BuildRig(object):
    def __init__(s):
        winName = "BuildRig"
        if cmds.window(winName, q=True, ex=True):
            cmds.deleteUI(winName)
        win = cmds.window(winName, rtf=True, t="Capture a new Skeleton.")
        cmds.columnLayout(adj=True)
        cmds.text(h=30, l="Select a part of your skeleton.")
        cmds.button(h=50, l="Save Skeleton", c= lambda x: warn(s.save))
        cmds.showWindow(win)

    def save(s):
        data = s.formStructure()
        if data:
            fileFilter = "Skeleton Files (*.skeleton)"
            path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=0) # Save file
            if path:
                with open(path[0], "w") as f:
                    json.dump(data, f, indent=4)
                cmds.confirmDialog(t="Nice...", m="Saved!")
        else:
            raise RuntimeError, "No Skeleton Found."

    def formStructure(s):
        sel = cmds.ls(sl=True, type="transform")
        if sel and len(sel) == 1:
            def ascend(pos):
                parent = cmds.listRelatives(pos, p=True, type="joint")
                if parent:
                    pos = ascend(parent)
                return pos
            def descend(pos):
                data = {}
                children = cmds.listRelatives(pos, c=True, type="joint")
                if children:
                    for c in children:
                        data[c] = descend(c)
                return data
            root = ascend(sel)
            return {root[0]: descend(root)} if cmds.objectType(root, isType="joint") else descend(root)
        else:
            raise RuntimeError, "Select a single joint in your skeleton."

BuildRig()
