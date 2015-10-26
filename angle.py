# Angle calculations for joints

import math
import maya.cmds as cmds
from SimpleBaseRigGITHUB.vector import Vector

UPAXIS = cmds.upAxis(q=True, ax=True)



def chunk(items, size):
    iLen = len(items)
    if size < iLen:
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


def angle(joints, aim):
    up = (0,1,0) if UPAXIS == "y" else (0,0,1)
    for j in chunk(joints, 2):
        cmds.delete(cmds.aimConstraint(
            j[1],
            j[0],
            aim=aim,
            upVector=up,
            worldUpType="scene",
            # worldUpVector=cross,
            weight=1,
            ))

def cleanup(joints):
    for j in joints:
        cmds.joint(j, e=True, zso=True)
        cmds.makeIdentity(j, apply=True)

def angle(joints):
    aimAxis = Vector(1,0,0) # X axis
    limb = len(joints)

    prev = Vector(0,0,0)
    for i in range(limb):
        # Set up our targets
        parent = joints[i - 1] if i else ""
        joint = joints[i]
        aim = joints[i + 1] if i < limb else ""

        if aim:
            up = Vector(0,0,0)
            if not up:
                up = Vector(0,1,0) if UPAXIS == "y" else Vector(0,0,1)


# sel = cmds.ls(sl=True)
# with Isolate(sel) as sel:
#     angle(sel, (1,0,0))
# cleanup(sel)


def cJO_orient(joints, aimAxis, upAxis, upDir, doAuto):
    nJnt = len(joints)
    prevUp = (0,0,0)
    for i in range(nJnt):



        if aimTgt != "":
            upVec = (0,0,0)
            # if doAuto
            if not upVec:
                pass

#   	    // First off...if $doAuto is on, we need to guess the cross axis dir.
            if doAuto:
#   	    	// Now since the first joint we want to match the second orientation
#   	    	// we kind of hack the things passed in if it is the first joint
#   	    	// ie: If the joint doesn't have a parent...OR if the parent it has
#   	    	// has the "same" position as itself...then we use the "next" joints
#   	    	// as the up cross calculations
                posJ = cmds.xform(joints[i], q=True, ws=True, rp=True)
                posP = posJ
                if parent != "":
                    posP = cmds.xform(parent, q=True, rp=True, ws=True)

                tol = 0.0001 # How close to we consider "same"?

                if parent == "" or abs(posJ[0] - posP[0]) <= tol and abs(posJ[1] - posP[1]) <= tol and abs(posJ[2] - posP[2]):
                    aimChilds = cmds.listRelatives(aimTgt, children=True)
                    aimChild = ""
                    for child in aimChilds:
                        if cmds.nodeType(child) == "joint":
                            aimChild = child
                            break
                        upVec = getCrossDir(joints[i], aimTgt, aimChild)
                else:
                    upVec = getCrossDir(parent, joints[i], aimTgt)

            if not doAuto or (upVec[0] == 0.0 and upVec[1] == 0.0 and upVec[2] == 0.0):
                upVec = upDir #  or else use user set up Dir. if needed

            aim = cmds.aimConstraint(
                aimTgt,
                joints[i],
                aim = aimAxis,
                upVector = upAxis,
                worldUpVector = upVec,
                worldUpType = "vector",
                weight = 1.0,
            )
            cmds.delete(aim)

            # Now compare the up we used to the previous one
            curUp = upVec
            curUp = unit(curUp)
            dot = curUp * prevUp # dot product for angle betwen...
            prevUp = upVec # store for later

            if i > 0 and dot <= 0.0:
#   	        // Adjust the rotation axis 180 if it looks like we've flopped the wrong way!
                cmds.xform(
                    joints[i],
                    r=True,
                    os=True,
                    ra= [(aimAxis[0] * 180), (aimAxis[1] * 180), (aimAxis[2] * 180)]
                )
                prevUp *= -1

            # And now finish clearing out joint axis...
            cmds.joint(joints[i], e=True, zso=True)
            cmds.makeIdentity(joints[i], apply=True)

        elif parent != "":
#   	    // Otherwise if there is no target, just dup orienation of parent...
            oCons = cmds.orientConstraint(parent, joints[i], weight=1.0)
            cmds.delete(oCons)

            # And now finish clearing out joint axis...
            cmds.joint(joints[i], e=True, zso=True)
            cmds.makeIdentity(joints[i], apply=True)

        # Now we're doen reparent
        if len(childs) > 0:
            cmds.parent(childs, joints[i])
