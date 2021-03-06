# Build a template file from a base rig file
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

import os
import json
import report
import markers
import maya.cmds as cmds

COLOUR = {
    "red"       :[0.8,0.3,0.3],
    "yellow"    :[0.8,0.7,0.1],
    "green"     :[0.3,0.8,0.5],
    "blue"      :[0.3,0.4,0.8],
    "grey"      :[0.3,0.3,0.3]
}
POSITION = "_position"
ROTATION = "_rotation"
SCALE = "_scale"
ROTATIONORDER = "_rotationOrder"

def shorten(text, length=40):
    buff = length - 5 # make room for " ... "
    textlen = len(text)
    if length < textlen:
        segment = int(buff * 0.5)
        text = text[:segment] + " ... " + text[segment * -1:]
    return text

class Callback(object):
    """ Simple callback """
    def __init__(s, func, *args, **kwargs): s.__dict__.update(**locals())
    def __call__(s, *_): return s.func(*s.args, **s.kwargs)

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
        with report.Report():
            s.template = templateData
            s.joints = []
            def parse(data):
                for c in [a for a in data if a[:1] != "_"]:
                    j = Joint(c, data[c])
                    j.btn = {}
                    s.joints.append(j)
                    data[c] = j
                    parse(data[c])
            parse(s.template)

            s.missing = 0 # count missing entries

            winName = "TemplateWin"
            if cmds.window(winName, ex=True):
                cmds.deleteUI(winName)
            window = cmds.window(winName, rtf=True, t="Retarget Skeleton")
            outer = cmds.columnLayout(adj=True)
            cmds.text(hl=True, h=60, l="Select a <strong>JOINT</strong> in the Maya scene. Then click the corresponding <strong>BUTTON</strong> to forge a connection.")
            cmds.scrollLayout(h=400, bgc=(0.2,0.2,0.2), cr=True)
            wrapper = cmds.rowLayout(nc=5, adj=1)
            col1 = cmds.columnLayout(adj=True, p=wrapper)
            cmds.text(l="Joint")
            cmds.separator()
            col2 = cmds.columnLayout(adj=True, p=wrapper)
            cmds.text(l="Position")
            cmds.separator()
            col3 = cmds.columnLayout(adj=True, p=wrapper)
            cmds.text(l="Rotation")
            cmds.separator()
            col4 = cmds.columnLayout(adj=True, p=wrapper)
            cmds.text(l="Scale")
            cmds.separator()
            col5 = cmds.columnLayout(adj=True, p=wrapper)
            cmds.text(l="R.Order")
            cmds.separator()

            for j in s.joints:
                s.addBaseBtn(j, col1)
                s.addAttrBtn(j, POSITION, col2)
                s.addAttrBtn(j, ROTATION, col3)
                s.addAttrBtn(j, SCALE, col4)
                s.addROrderBtn(j, col5)

            s.btnSave = cmds.button(l="Click to Save", en=False, h=50, p=outer, c=lambda x: s.save())
            cmds.showWindow(window)
            s.marker = markers.Markers()
            cmds.scriptJob(uid=[window, s.marker.__exit__], ro=True)
            cmds.warning("%s to target." % s.missing)

    def addBaseBtn(s, joint, parent):

        def addNew():
            s.setAttr(joint, POSITION)
            s.setAttr(joint, ROTATION)
            s.setAttr(joint, SCALE)

        def addExisting():
            if position: s.setAttr(joint, POSITION, [position])
            if rotation: s.setAttr(joint, ROTATION, [rotation])
            if scale: s.setAttr(joint, SCALE, [scale])

        position = joint.get(POSITION, "")
        rotation = joint.get(ROTATION, "")
        scale = joint.get(SCALE, "")
        position = position if cmds.objExists(position) else None
        rotation = rotation if cmds.objExists(rotation) else None
        scale = scale if cmds.objExists(scale) else None

        btn = joint.btn["joint"] = cmds.button(
            h=30,
            bgc=COLOUR["blue"],
            l=shorten(joint.name),
            p=parent,
            c=Callback(addNew)
            )
        cmds.popupMenu(p=btn)
        if position or rotation or scale:
            cmds.menuItem(l="Use existing targets", c=Callback(addExisting))
        else:
            cmds.menuItem(l="Select a target to pick it", en=False)

    def addAttrBtn(s, joint, attr, parent):
        at = joint.get(attr, "")
        at = joint[attr] = at if cmds.objExists(at) else ""

        if not at: s.missing += 1
        btn = joint.btn[attr] = cmds.button(
            h=30,
            bgc=COLOUR["yellow"] if at else COLOUR["red"],
            l=shorten(at) if at else "[ PICK A TARGET ]",
            p=parent,
            c=Callback(s.setAttr, joint, attr)
            )
        cmds.popupMenu(p=btn)
        if at:
            cmds.menuItem(l="Use existing target: %s" % at, c=Callback(s.setAttr, joint, attr, [at]))
        else:
            cmds.menuItem(l="Select a target to pick it", en=False)

    def addROrderBtn(s, joint, parent):
        cmds.optionMenu(
            h=30,
            bgc=(0.3,0.3,0.3),
            cc=lambda x: s.setRotationOrder(joint, x)
            )
        axis = ["xyz", "xzy", "yxz", "yzx", "zyx", "zxy"]
        default = joint.get(ROTATIONORDER, None)
        default = default if default in axis else "xyz"
        axis.remove(default)
        cmds.menuItem(l=default)
        for ax in axis:
            cmds.menuItem(l=ax)

    @report.Report()
    def setRotationOrder(s, joint, order):
        joint[ROTATIONORDER] = order

    @report.Report()
    def setAttr(s, joint, attr, target=None):
        sel = target or cmds.ls(sl=True)
        if sel and len(sel) == 1:
            sel = sel[0]
            cmds.button(
                joint.btn[attr],
                e=True,
                l=shorten(sel),
                bgc=COLOUR["green"]
                )
            if not joint.get(attr, None): s.missing -= 1
            joint[attr] = sel
            s.marker.createMarker(sel, joint.name + attr)
            if s.missing <= 0:
                cmds.button(s.btnSave, e=True, en=True)
            else:
                cmds.warning("%s left to target." % s.missing)
        else:
            cmds.confirmDialog(t="Oh no", m="You must select a single object to target.")

    @report.Report()
    def save(s):
        fileFilter = "Skeleton Files (*.skeleton)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fm=0) # Save file
        if path:
            with open(path[0], "w") as f:
                json.dump(s.template, f, indent=4)
            print "Saved"
            cmds.confirmDialog(t="Nice...", m="Saved!")
