
import maya.api.OpenMaya as om
import maya.cmds as cmds

# Objects
c1 = "pCube1"
c2 = "pCube2"

# Matrix
m1 = cmds.xform(c1, q=True, m=True)
m2 = cmds.xform(c2, q=True, m=True)

# Vectors
p1 = om.MVector(m1[12:15]) # Object Positions
p2 = om.MVector(m2[12:15])
aim = (p2 - p1).normalize() # Vector Between Objects
right = (om.MVector((0,1,1)) ^ aim).normalize()
up = (aim ^ right).normalize()

print up * right

# New Matrix

m3 = (
    up[0],    up[1],   up[2],   0,
    aim[0],     aim[1],    aim[2],    0,
    right[0],  right[1], right[2], 0,
    p1[0],     p1[1],    p1[2],    1
)

# Apply matrix
cmds.xform(c1, m=m3)
