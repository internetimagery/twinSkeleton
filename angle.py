# Angle calculations for joints

import math
import maya.cmds as cmds
from SimpleBaseRigGITHUB.vector import Vector

UPAXIS = cmds.upAxis(q=True, ax=True)

def chunk(items, size):
    iLen = len(items)
    if size <= iLen:
        for i in range(iLen - (size - 1)): yield [items[i + a] for a in range(size)]

class Isolate(object):
    def __init__(s, joints): s.joints = joints
    def __enter__(s): return cmds.parent(s.joints, w=True)
    def __exit__(s, *err):
        for j in chunk(s.joints, 2): cmds.parent(j[1], j[0])

def cleanup(joints):
    for j in joints:
        cmds.joint(j, e=True, zso=True)
        cmds.makeIdentity(j, apply=True)

def angle(joints):
    aimAxis = Vector(1,0,0) # X axis
    worldUp = Vector(0,1,0) if UPAXIS == "y" else Vector(0,0,1)
    limb = len(joints)
    def orient(p1, p2, vector):
        cmds.delete(cmds.aimConstraint(
            p2,
            p1,
            aim=aimAxis,
            upVector=worldUp,
            worldUpVector=vector,
            worldUpType="vector",
            weight=1.0
        ))
    if 1 < limb: # Nothing to rotate if only a single joint
        pos = [Vector(*cmds.xform(a, q=True, ws=True, rp=True)) for a in joints]
        if limb < 3: # We don't have enough joints to aim fancy
            orient(joints[0], joints[1], worldUp)
        else:
            pos = [Vector(*cmds.xform(a, q=True, ws=True, rp=True)) for a in joints]
            prev = Vector(0,0,0)
            for i in range(limb - 2):
                j1, j2, j3 = joints[i], joints[i + 1], joints[i + 2]
                p1, p2, p3 = pos[i], pos[i + 1], pos[i + 2]

                v1 = p1 - p2
                v2 = p3 - p2
                v3 = v1.cross(v2).normalized or prev or worldUp

                if not i: orient(j1, j2, v3) # Don't forget to aim the root!
                orient(j2, j3, v3)

                dot = v3.dot(prev)
                prev = v3

                if i and dot <= 0:
                    cmds.xform(j2, r=True, os=True, ro=aimAxis * (180,180,180))
                    prev *= (-1,-1,-1)

sel = cmds.ls(sl=True)
with Isolate(sel):
    angle(sel)
cleanup(sel)
cmds.select(sel, r=True)
