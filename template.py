# Build a template file from a base rig file

import os, json
import maya.cmds as cmds
from SimpleBaseRig.markers import Markers

class Template(object):
    """
    Join base rig file to objects in scene
    """
    def __init__(s, templateData):

        s.meta = {}
        def parse(data, root=""): # Parse out all keys from dict
            for d in data:
                s.meta["%s/%s" % (root, d)] = {
                    "name" : d,
                    "btn" : ""
                }
                if data[d]:
                    parse(data[d])
        parse(templateData)
        s.links = {} # Store links seperate

        winName = "TemplateWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        window = cmds.window(winName, rtf=True, t="Create Template")
        cmds.columnLayout(adj=True)
        cmds.text(hl=True, h=60, l="Select a <strong>JOINT</strong> in the Maya scene. Then click the corresponding <strong>BUTTON</strong> to forge a connection.")
        s.btnSave = cmds.button(l="press me to save thing", en=False, c=Callback(s.save))
        cmds.scrollLayout(bgc=(0,0,0), cr=True)
        for m in s.meta:
            s.meta[m]["btn"] = cmds.button(l=s.meta[m]["name"], bgc=(0.8,0.3,0.3), c=Callback(s.link, m))
        cmds.showWindow(window)
        s.marker = Markers()
        cmds.scriptJob(uid=[window, s.marker.__exit__], ro=True)

    def link(s, meta):
        sel = cmds.ls(sl=True)
        if sel:
            if len(sel) == 1:
                m = s.meta[meta]
                print "Linking %s -> %s" % (sel[0], m["name"])
                cmds.button(m["btn"], e=True, bgc=(0.3, 0.8, 0.5))
                cmds.button(m["btn"], e=True, l="%s -> %s" % (m["name"], sel[0]))
                s.links[meta] = sel[0]
                s.marker.createMarker(sel[0], m["name"])
                cmds.select(sel[0], r=True)
                if len(s.links) == len(s.meta): # All buttons clicked
                    cmds.button(s.btnSave, e=True, en=True)
            else:
                warn("You must only have one thing selected.")
        else:
            warn("You need to select something in the viewport.")

    def save(s):
        fileFilter = "Rig Templates (*.rig)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2) # Save file
        if path:
            with open(path[0], "w") as f:
                for l in s.links:
                    f.write("%s = %s\n" % (l, s.links[l]))

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
