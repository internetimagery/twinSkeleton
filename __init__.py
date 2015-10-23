# Tool to automate attaching secondary simple rigs to complicated ones.
# Perfect for game rigging.

import maya.cmds as cmds
import template
import makeRig
import json
import os

class Main(object):
    """
    Main window
    """
    def __init__(s):
        winName = "Main_Selector"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=500, t="Simple Rig Creator")
        cmds.columnLayout(adj=True)
        cmds.button(l="Create a New Template.", h=50, c=s.makeTemplate)
        cmds.button(l="Open an existing Template.\nBuild the Rig.", h=50, c=s.runTemplate)
        cmds.showWindow(s.win)

    def makeTemplate(s, *junk):
        cmds.deleteUI(s.win)
        Opener()

    def runTemplate(s, *junk):
        cmds.deleteUI(s.win)
        makeRig.MakeRig()

class Opener(object):
    def __init__(s):
        winName = "Template_Opener"
        root = os.path.realpath(os.path.dirname(__file__)) # Location of script folder
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=500, t="Open Base Rig File")
        cmds.columnLayout(adj=True)
        cmds.text(l="Pick a Base rig layout")
        cmds.rowLayout(nc=2, adj=1)
        s.fileName = cmds.textField(h=30, tx=os.path.join(root, "default.json")) # "testingfile.json"))
        cmds.iconTextButton(style='iconOnly', image1='openScript.png', c=s.openFile)
        cmds.setParent("..")
        cmds.rowLayout(nc=2, cw2=[250, 250])
        cmds.button(l="Cancel", h=50, w=250, c=lambda x: cmds.deleteUI(s.win))
        cmds.button(l="Open",   h=50, w=250, c=s.runTemplate)
        cmds.showWindow(s.win)

    def openFile(s, *junk):
        fileFilter = "Base Rig Templates (*.json)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=1) # Open file
        if path:
            cmds.textField(s.fileName, e=True, tx=path[0])

    def runTemplate(s, *junk):
        path = cmds.textField(s.fileName, q=True, tx=True)
        try:
            with open(path, "r") as f:
                data = json.load(f)
                cmds.deleteUI(s.win)
                template.Template(data)
        except IOError, ValueError:
            cmds.confirmDialog(t="Uh oh...", m="There was a problem opening the file.")
