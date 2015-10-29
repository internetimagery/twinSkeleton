# Testing

from twinSkeleton.vector import Vector
import maya.cmds as cmds

def stretch(jnt1, jnt2):
    p1 = Vector(*cmds.xform(jnt1, q=True, ws=True, rp=True))
    p2 = Vector(*cmds.xform(jnt2, q=True, ws=True, rp=True))
    dist = cmds.shadingNode(
        "distanceBetween",
        n="%s_dist" % jnt1,
        asUtility=True
        )
    cmds.connectAttr(
        "%s.translate" % jnt1,
        "%s.point1" % dist,
        force=True
        )
    cmds.connectAttr(
        "%s.translate" % jnt2,
        "%s.point2" % dist,
        force=True
        )
    mult = cmds.shadingNode(
        "multiplyDivide",
        n="%s_mult" % jnt1,
        asUtility=True
        )
    cmds.setAttr("%s.operation" % mult, 2)
    cmds.setAttr("%s.input1X" % mult, cmds.getAttr("%s.distance" % dist))
    cmds.connectAttr(
        "%s.distance" % dist,
        "%s.input2X" % mult,
        force = True
        )
    cmds.connectAttr(
        "%s.outputX" % mult,
        "%s.scaleY" % jnt1,
        force=True
        )
    cmds.connectAttr(
        "%s.outputX" % mult,
        "%s.scaleZ" % jnt1,
        force=True
        )

p1 = Vector(5,5,0)
p2 = Vector(10,-4,-2)

jnt1 = cmds.joint(p=p1)
jnt2 = cmds.joint(p=p2)
cmds.joint(jnt1, e=True, zso=True, oj="xyz", sao="yup")

stretch(jnt1, jnt2)
