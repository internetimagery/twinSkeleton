# Tool to automate attaching secondary simple rigs to complicated ones.
# Perfect for game rigging.

import maya.cmds as cmds
import retarget
import makeRig
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
            image="defaultHand.png",
            style="iconAndTextHorizontal",
            l="Retarget Rig.",
            h=50,
            c=s.retarget
        )
        cmds.iconTextButton(
            image="goToBindPose.png",
            style="iconAndTextHorizontal",
            l="Attach Rig.",
            h=50,
            c=s.build
        )
        cmds.showWindow(s.win)

    def retarget(s, *junk):
        cmds.deleteUI(s.win)
        Opener()

    def build(s, *junk):
        cmds.deleteUI(s.win)
        makeRig.MakeRig()

class Opener(object):
    def __init__(s):
        winName = "Template_Opener"
        root = os.path.realpath(os.path.dirname(__file__)) # Location of script folder
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=500, t="Open Rig File")
        cmds.columnLayout(adj=True)
        cmds.text(l="Pick a Rig layout")
        cmds.rowLayout(nc=2, adj=1)
        s.fileName = cmds.textField(h=30, tx=os.path.join(root, "default.rig"))
        cmds.iconTextButton(style='iconOnly', image1='openScript.png', c=s.openFile)
        cmds.setParent("..")
        cmds.rowLayout(nc=2, cw2=[250, 250])
        cmds.button(l="Cancel", h=50, w=250, c=lambda x: cmds.deleteUI(s.win))
        cmds.button(l="Open",   h=50, w=250, c=lambda x: warn.run(s.retarget))
        cmds.showWindow(s.win)

    def openFile(s):
        fileFilter = "Rig Files (*.rig)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Open file
        if path:
            cmds.textField(s.fileName, e=True, tx=path[0])

    def retarget(s):
        path = cmds.textField(s.fileName, q=True, tx=True)
        try:
            with open(path, "r") as f:
                data = json.load(f)
                cmds.deleteUI(s.win)
                retarget.Retarget(data)
        except IOError, ValueError:
            raise RuntimeError, "There was a problem opening the file."
