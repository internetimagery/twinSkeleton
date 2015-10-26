# Angle calculations for joints
import maya.cmds as cmds

UPAXIS = cmds.upAxis(q=True, ax=True)

def pair(joints):
    for i in range(len(joints) - 1): yield joints[i], joints[i + 1]

def unparent(joints):
    cmds.parent(joints, w=True)

def parent(joints):
    for j1, j2 in pair(joints): cmds.parent(j2, j1)

def angle(joints, aim):
    up = (0,1,0) if UPAXIS == "y" else (0,0,1)
    for j1, j2 in pair(joints):
        cmds.delete(cmds.aimConstraint(
            j2,
            j1,
            aim=aim,
            upVector=up,
            worldUpType="scene",
            # worldUpVector=cross,
            weight=1,
            ))

sel = cmds.ls(sl=True)
for a, b in two(sel):
    print a, b
unparent(sel)
angle(sel, (1,0,0))
parent(sel)
