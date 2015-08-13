# Some markers
import maya.cmds as cmds

class Markers(object):
    """
    Create markers for visual feedback
    """
    def __init__(s):
        s.baseName = "MarkerWrapper"
        s.__enter__()

    def __enter__(s):
        if cmds.objExists(s.baseName):
            cmds.delete(s.baseName)
        s.baseName = cmds.circle(r=20, n=s.baseName)[0]
        for at in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz"]:
            cmds.setAttr(s.baseName + at, l=True, k=False, cb=False)
        cmds.addAttr(s.baseName, ln="markerSize", dv=1)
        cmds.setAttr("%s.markerSize" % s.baseName, k=True)
        return s.createMarker

    def __exit__(s, *errs):
        if cmds.objExists(s.baseName):
            cmds.delete(s.baseName)

    def createMarker(s, target, name):
        name = "%s_marker" % name
        if cmds.objExists(name):
            cmds.delete(name)
        name = cmds.polySphere(name=name)[0]
        cmds.parent(name, s.baseName)
        for at in [".sx", ".sy", ".sz"]:
            cmds.connectAttr("%s.markerSize" % s.baseName, name + at, f=True)
        cmds.parentConstraint(target, name)
        cmds.setAttr("%s.overrideEnabled" % name, 1)
        cmds.setAttr("%s.overrideDisplayType" % name, 2)
