# Build a template file from a base rig file

import os, json
import maya.cmds as cmds

root = os.path.realpath(os.path.dirname(__file__)) # Location of script folder

class Template(object):
    """
    Join base rig file to objects in scene
    """
    def __init__(s, templateFile):
        winName = "TemplateWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        window = cmds.window(winName)
        cmds.columnLayout(adj=True)
        cmds.text(hl=True, h=40, l="Select a <strong>JOINT</strong> in the Maya scene. Then click the corresponding <strong>BUTTON</strong> to forge a connection.")
        s.buttonLayout = cmds.scrollLayout(bgc=(0,0,0), h=300, cr=True)
        cmds.showWindow(window)

        rigFile = json.load(templateFile)
        print s.rigParse(rigFile)
        # rigSetup = s.rigParse(json.load(templateFile))
        # print rigSetup

        s.buttons = s._buildScruture()
        s._refreshButtons()


    def rigParse(s, current, root=""):
        result = []
        if type(current) == "dict":
            for curr in current:
                print curr
                currPath = os.path.join(root, curr)
                result.append(currPath)
                result += s.rigParse(currPath, current[curr])
        return result


    def _buildScruture(s):
        return ["one", "two", "three"]

    def _refreshButtons(s):
        remove = cmds.scrollLayout(s.buttonLayout, q=True, ca=True)
        if remove:
            cmds.deleteUI(remove)
        for b in s.buttons:
            cmds.button(l=b, p=s.buttonLayout, bgc=(0.9, 0.9, 0.9), c=Callback(s.join, b))

    def join(s, b):
        sel = cmds.ls(sl=True)
        if sel:
            if len(sel) == 1:
                print "Linking %s -> %s" % (sel[0], b)
                s.buttons.remove(b)
                s._refreshButtons()
            else:
                warn("You must only have one thing selected.")
        else:
            warn("You need to select something in the viewport.")

def warn(message):
    cmds.confirmDialog(t="Whoops...", m=message)


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

testFile = os.path.join(root, "default.rig")
with open(testFile, "r") as f:
    Template(f)


# def rigWalk(root, current):
#     result = []
#     for curr in current:
#         currPath = join(root, curr)
#         result.append(currPath)
#         result += rigWalk(currPath, current[curr])
#     return result
# rigSetup = rigWalk("", rig)
