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

def getVector(pos1, pos2):
    return Vector(*pos1) - Vector(*pos2)

# Cross angle:
# pt1, pt2, pt3
# v1 = getVector(pt1, pt2)
# v2 = getVector(pt3, pt2)
# v3 = v1.cross(v2)
# print v3.normalized


# def angle(joints, aim):
#     up = (0,1,0) if UPAXIS == "y" else (0,0,1)
#     for j in chunk(joints, 2):
#         cmds.delete(cmds.aimConstraint(
#             j[1],
#             j[0],
#             aim=aim,
#             upVector=up,
#             worldUpType="scene",
#             # worldUpVector=cross,
#             weight=1,
#             ))

def cleanup(joints):
    for j in joints:
        cmds.joint(j, e=True, zso=True)
        cmds.makeIdentity(j, apply=True)

def angle(joints):
    aimAxis = Vector(1,0,0) # X axis
    upAxis = Vector(0,1,0) # Y Axis
    worldUp = Vector(0,1,0) if UPAXIS == "y" else Vector(0,0,1)
    upVector = worldUp # Default to world up
    limb = len(joints)
    if 1 < limb: # Nothing to rotate if only a single joint
        pos = [Vector(*cmds.xform(a, q=True, ws=True, rp=True)) for a in joints]
        for i in range(limb):
            j1 = joints[i - 1] if i else None
            p1 = pos[i - 1] if j1 else None
            j2 = joints[i]
            p2 = pos[i]
            j3 = joints[i + 1] if i < limb else None
            p3 = pos[i + 1] if j3 else None
            j4 = joints[i + 2] if i < (limb - 1) else None

            if j1:
                pass
            else: # We are at the start of the chain
                if j3: # We have a match




    if 2 < limb:
        for j in chunk(joints, 3):
            p1 = Vector(*cmds.xform(j[0], q=True, ws=True, rp=True))
            p2 = Vector(*cmds.xform(j[1], q=True, ws=True, rp=True))
            p3 = Vector(*cmds.xform(j[2], q=True, ws=True, rp=True))

            v1 = p1 - p2
            v2 = p3 - p2
            v3 = v1.cross(v2)
        # cmds.delete(cmds.aimConstraint(
        #     j[2],
        #     j[1],
        #     aim=aimAxis,
        #     upVector=upAxis,
        #     worldUpVector=v3.normalized,
        #     worldUpType="vector",
        #     weight=1.0
        # ))


sel = cmds.ls(sl=True)
with Isolate(sel):
    angle(sel)
cleanup(sel)
cmds.select(sel, r=True)
