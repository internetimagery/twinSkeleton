# Build a template file from a base rig file

import os, json
import maya.cmds as cmds

root = os.path.realpath(os.path.dirname(__file__))

class Template(object):
    """
    Join base rig file to objects in scene
    """
    def __init__(s):
        winName = "TemplateWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        window = cmds.window(winName)
        cmds.columnLayout(adj=True)
        cmds.text(hl=True, h=40, l="Select a <strong>JOINT</strong> in the Maya scene. Then click the corresponding <strong>BUTTON</strong> to forge a connection.")
        s.buttonLayout = cmds.scrollLayout(bgc=(0,0,0), h=300, cr=True)
        cmds.showWindow(window)

        s.buttons = ["one", "two", "three"]
        s._refreshButtons()

    def _refreshButtons(s):
        remove = cmds.scrollLayout(s.buttonLayout, q=True, ca=True)
        print remove
        for b in s.buttons:
            cmds.button(l=b, p=s.buttonLayout, bgc=(0.9, 0.9, 0.9))

    def _attach(s):
        print "attaching!!"

class Callback(object):
    """
    Holds arguments for button commands
    """
    def __init__(self, func, *args, **kwargs):
            self.func = func
            self.args = args
            self.kwargs = kwargs

    def __call__(self, *args):
            return self.func(*self.args, **self.kwargs)

# Template()


# def rigWalk(root, current):
#     result = []
#     for curr in current:
#         currPath = join(root, curr)
#         result.append(currPath)
#         result += rigWalk(currPath, current[curr])
#     return result
# rigSetup = rigWalk("", rig)
