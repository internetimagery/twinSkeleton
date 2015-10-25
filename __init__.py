# Tool to automate attaching secondary simple rigs to complicated ones.
# Perfect for game rigging.

import maya.cmds as cmds
import buildRig
import retarget
import os.path
import attach
import json
import warn
import os

class Main(object):
    """
    Main window
    """
    def __init__(s):
        winName = "Main_Selector"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, t="Simple Rig Creator")
        cmds.columnLayout(adj=True)
        cmds.iconTextButton(
            image="kinJoint.png",
            style="iconAndTextHorizontal",
            l="Capture Skeleton.",
            h=50,
            c=lambda: warn(s.run, buildRig.BuildRig)
        )
        cmds.iconTextButton(
            image="defaultHand.png",
            style="iconAndTextHorizontal",
            l="(Re)Target Skeleton.",
            h=50,
            c=lambda: warn(s.run, retarget.Retarget, True)
        )
        cmds.iconTextButton(
            image="goToBindPose.png",
            style="iconAndTextHorizontal",
            l="Attach Skeleton.",
            h=50,
            c=lambda: warn(s.run, attach.Attach, True)
        )
        cmds.showWindow(s.win)

    def run(s, func, load=None):
        if load:
            fileFilter = "Skeleton Files (*.skeleton)"
            path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Open file
            if path:
                with open(os.path.realpath(path[0]), "r") as f:
                    data = json.load(f)
                func(data)
        else:
            func()
        cmds.deleteUI(s.win)
