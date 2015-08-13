# Tool to automate attaching secondary simple rigs to complicated ones. Perfect for game rigging.

import maya.cmds as cmds


class Main(object):
    def __init__(s):
        winName = "Main_Selector"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        win = cmds.window(rtf=True)
        cmds.columnLayout(adj=True)
        cmds.button(l="Create a NEW Template.", h=50, c=s.makeTemplate)
        cmds.button(l="OPEN an existing Template.\nBUID the Rig.", h=50, c=s.runTemplate)
        cmds.showWindow(win)

    def makeTemplate(s, *junk):
        print "tempalte"

    def runTemplate(s, *junk):
        print "running"


Main()
