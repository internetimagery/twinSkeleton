
import maya.api.OpenMaya as om
import maya.cmds as cmds

# Objects
c1 = "pCube1"
c2 = "pCube2"
c3 = "pCube3"

# Position
p1 = om.MVector(cmds.xform(c1, q=True, t=True, ws=True))
p2 = om.MVector(cmds.xform(c2, q=True, t=True, ws=True))
p3 = om.MVector(cmds.xform(c3, q=True, t=True, ws=True))

# Get cross vector
 #  /
 # /
 # ----- cross
 # \
 #  \
tail = p1 - p2
world = om.MVector(0,0,1)
aim = (p3 - p2).normalize()
up = (aim ^ tail).normalize()
right = (aim ^ up).normalize()

v1 = om.MVector(1,2,3)
v2 = om.MVector([a for a in v1])
v2[1] = 50
print v1
print v2

if right * world < 0:
    print "flipping"
    up = -up
    right = -right

matrix = (
    aim[0], aim[1], aim[2], 0,
    up[0],  up[1],  up[2],  0,
    right[0], right[1], right[2], 0,
    p2[0], p2[1], p2[2], 1
)


# Apply matrix
cmds.xform(c2, m=matrix)
