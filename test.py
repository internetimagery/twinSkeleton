import json




import maya.cmds as cmds

loc1 = cmds.spaceLocator()
cmds.move(1,2,3,loc1)
loc2 = cmds.spaceLocator()
cmds.move(3,2,1,loc2)

pos1 = cmds.xform(loc1, q=True, t=True, ws=True)
pos2 = cmds.xform(loc2, q=True, t=True, ws=True)

cmds.select(cl=True)
jnt1 = cmds.joint(p=pos1)
cmds.select(cl=True)
jnt2 = cmds.joint(p=pos2)
cmds.parent(jnt2, jnt1)
cmds.joint(
    jnt1,
    e=True,
    zeroScaleOrient=True,
    orientJoint="xyz",
    secondaryAxisOrient="yup"
    )

# print cmds.upAxis(q=True, ax=True)
#
#  # 	The argument can be one of the following strings: xup, xdown, yup, ydown, zup, zdown, none.
#
# # # This flag is used in conjunction with the -oj/orientJoint flag.
# # It specifies the scene axis that the second axis should align with. For example, a flag combination of "-oj yzx -sao yup" would result
# # in the y-axis pointing down the bone, the z-axis oriented with the scene's positive y-axis, and the x-axis oriented according to the right hand rule.
