
import maya.cmds as cmds
from SimpleBaseRigGITHUB.vector import Vector

win = cmds.playblast(activeEditor=True)
cam = cmds.modelEditor(win, q=True, camera=True)
p1 = Vector(*cmds.xform(cam, q=True, ws=True, t=True))
p2 = Vector(0,0,0) # Center of world
distance = p2.distance(p1)
print distance
cmds.polySphere(radius=distance * 0.1)
