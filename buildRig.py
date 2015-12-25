# Build Skeleton file from existing rig
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

import json
import report
import maya.cmds as cmds

class Callback(object):
    """ Simple callback """
    def __init__(s, func, *args, **kwargs): s.__dict__.update(**locals())
    def __call__(s, *_): return s.func(*s.args, **s.kwargs)

class BuildRig(object):
    def __init__(s):
        with report.Report():
            winName = "BuildRig"
            if cmds.window(winName, q=True, ex=True):
                cmds.deleteUI(winName)
            win = cmds.window(winName, rtf=True, t="Capture a new Skeleton.")
            cmds.columnLayout(adj=True)
            cmds.text(h=30, l="Select a part of your skeleton.")
            cmds.button(h=50, l="Save Skeleton", c=Callback(s.save))
            cmds.showWindow(win)

    @report.Report()
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
            cmds.confirmDialog(t="Oh no...", m="No Skeleton Found.")

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
            cmds.confirmDialog(t="Oh no...", "Select a single joint in your skeleton.")
