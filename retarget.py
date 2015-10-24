# Build a template file from a base rig file

import os
import json
# import warn
import SimpleBaseRig.warn as warn
# import markers
import SimpleBaseRig.markers as markers
import maya.cmds as cmds

def shorten(text, length):
    buff = length - 5 # make room for " ... "
    textlen = len(text)
    if buff < 0 or textlen < buff:
        text += " " * (length - textlen)
    else:
        segment = int(buff * 0.5)
        text = text[:segment] + " ... " + text[segment * -1:]
        text = shorten(text, length)
    return text

class Joint(dict):
    def __init__(s, name, *args, **kwargs):
        dict.__init__(s, *args, **kwargs)
        s.name = name
        s.ready = False

class Retarget(object):
    """
    Join base rig file to objects in scene
    """
    def __init__(s, templateData):

        s.template = templateData
        s.joints = []
        def parse(data, last=None): # Position 1 = root, 2 = limb, 3 = tip
            children = [a for a in data if a[:1] != "_"]
            childNum = len(children)
            if childNum:
                for c in children:
                    j = Joint(c, data[c])
                    s.joints.append(j)
                    data[c] = j
                    parse(data[c], j)
                    if childNum == 1: # Limb joint
                        j.pos = 2
                    else: # Root joint
                        j.pos = 1
            elif last: # End joint
                last.pos = 3
        parse(s.template)

        def row1(joint, parent):
            btn1 = cmds.button(h=30, l=joint.name, bgc=(0.8,0.3,0.3), c=lambda x: warn(s.link, joint, btn1), p=parent)

        def row2(joint, parent):
            btn1 = cmds.button(h=30, l=joint.name, bgc=(0.8,0.3,0.3), c=lambda x: warn(s.link, joint, btn1), p=parent)

        def row3(joint, parent):
            btn1 = cmds.button(h=30, l=joint.name, bgc=(0.8,0.3,0.3), c=lambda x: warn(s.link, joint, btn1), p=parent)

        def row4(joint, parent):
            btn1 = cmds.button(h=30, l=joint.name, bgc=(0.8,0.7,0.1), c=lambda x: warn(s.link, joint, btn1), p=parent)

        def row5(joint, parent):
            cmds.optionMenu(h=30, bgc=(0.3,0.3,0.3), cc=lambda x: warn(s.setRotationOrder, joint, x))
            axis = ["xyz", "xzy", "yxz", "yzx", "zyx", "zxy"]
            default = joint.get("_rotationOrder", None)
            default = default if default in axis else "xyz"
            axis.remove(default)
            cmds.menuItem(l=default)
            for ax in axis:
                cmds.menuItem(l=ax)

        def addBtn(joint, parent):
            row = cmds.rowLayout(nc=5, adj=1, p=parent)
            btn1 = cmds.button(h=30, l=joint.name, bgc=(0.8,0.3,0.3), c=lambda x: warn(s.link, joint, btn1), p=row)
            cmds.popupMenu(p=btn1)
            existing = joint.get("_position", None)
            if existing:
                cmds.menuItem(l="Use existing target: %s" % existing, c=lambda x: warn(s.link, joint, btn1, [existing]))

            btn1 = cmds.button(h=30, l=shorten(joint.name, rowWidth), bgc=(0.8,0.3,0.3), c=lambda x: warn(s.link, joint, btn1), p=row)
            btn1 = cmds.button(h=30, l=shorten(joint.name, rowWidth), bgc=(0.8,0.7,0.1), c=lambda x: warn(s.link, joint, btn1), p=row)
            btn1 = cmds.button(h=30, l=shorten(joint.name, rowWidth), bgc=(0.8,0.3,0.3), c=lambda x: warn(s.link, joint, btn1), p=row)

        s.total = len(s.joints) # Count changes of joints
        rowWidth = 30

        winName = "TemplateWin"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        window = cmds.window(winName, rtf=True, t="Create Template")
        outer = cmds.columnLayout(adj=True)
        cmds.text(hl=True, h=60, l="Select a <strong>JOINT</strong> in the Maya scene. Then click the corresponding <strong>BUTTON</strong> to forge a connection.")
        row = cmds.rowLayout(nc=5, adj=1)
        cmds.text(l="Base")
        cmds.text(l=shorten("Position", rowWidth))
        cmds.text(l=shorten("Rotation", rowWidth))
        cmds.text(l=shorten("Scale", rowWidth))
        cmds.text(l=shorten("R.Order", rowWidth))
        cmds.setParent("..")
        cmds.scrollLayout(h=400, bgc=(0.2,0.2,0.2), cr=True)
        wrapper = cmds.rowLayout(nc=5, adj=1)
        for j in s.joints:
            row1(j, cmds.columnLayout(adj=True, p=wrapper))
            row2(j, cmds.columnLayout(adj=True, p=wrapper))
            row3(j, cmds.columnLayout(adj=True, p=wrapper))
            row4(j, cmds.columnLayout(adj=True, p=wrapper))
            row5(j, cmds.columnLayout(adj=True, p=wrapper))
        s.btnSave = cmds.button(l="Click to Save", en=False, h=50, p=outer, c=lambda x: s.save())
        cmds.showWindow(window)
        s.marker = markers.Markers()
        cmds.scriptJob(uid=[window, s.marker.__exit__], ro=True)

    def setRotationOrder(s, joint, order):
        joint["_rotationOrder"] = order

    def setTarget(s, joint, axis, btn):
        sel = cmds.ls(sl=True)
        if sel and len(sel) == 1:
            joint[axis] = sel[0]
            cmds.button(btn, e=True, l=cmds.button(btn, q=True, l=True) + "*")
        else:
            raise RuntimeError, "You must select a single object to target."

    def link(s, joint, btn, target=None):
        sel = target or cmds.ls(sl=True)
        if sel:
            if len(sel) == 1:
                sel = sel[0]
                name = joint.name
                print "Linking %s -> %s" % (sel, name)
                if not joint.ready:
                    joint.ready = True
                    s.total -= 1
                joint["_position"] = sel
                joint["_rotation"] = sel
                joint["_scale"] = sel
                cmds.button(
                    btn,
                    e=True,
                    bgc=(0.3, 0.8, 0.5),
                    l="%s -> %s" % (name, sel)
                    )
                s.marker.createMarker(sel, name)
                cmds.select(sel, r=True)
                if s.total <= 0:
                    cmds.button(s.btnSave, e=True, en=True)
            else:
                raise RuntimeError, "You must only have one thing selected."
        else:
            raise RuntimeError, "You need to select something in the viewport."

    def save(s):
        fileFilter = "Skeleton Files (*.skeleton)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=0) # Save file
        if path:
            with open(path[0], "w") as f:
                json.dump(s.template, f, indent=4)
                print "Saved"
with open(r"C:\Users\maczone\Desktop\test.rig", "r") as f:
    data = json.load(f)
    Retarget(data)
