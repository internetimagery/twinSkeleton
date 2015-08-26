# Export rig by baking out curves first
import maya.cmds as cmds
# from makeRig import NameSpace, GetRoot

def NameSpace(name, prefix=None):
    return prefix + name if prefix else name

def GetRoot():
    return "EXPORT_RIG"

# file -force -options "v=0;" -typ "FBX export" -pr -es "/home/maczone/Desktop/test.fbx";

# bakeResults -simulation true -t "0:20" -hierarchy below -smart 1 5 -disableImplicitControl true -preserveOutsideKeys false -sparseAnimCurveBake true -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer true -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"hero_rig:all_translate"};
class ExportRig (object):
    """
    select all joints, bake keyframes onto them and export, then undo action
    """
    def __init__(s):
        s.origSelection = cmds.ls(sl=True) # Store original selection to return to
        s.locateSkeleton()


    def locateSkeleton(s, prefix=None):
        baseName = NameSpace(GetRoot(), prefix)
        baseObj = cmds.ls(baseName, r=True)
        if baseObj:
            # largeList = cmds.listRelatives(baseObj, ad=True, pa=True, ni=True)
            cmds.select(baseObj, r=True)
            cmds.select(baseObj, hi=True, tgl=True)
            joints = cmds.ls(sl=True, typ="joint")
            if joints:
                return joints
        cmds.confirmDialog(t="Bugger...", m="Couldn't find a matching rig.")
        return None

ExportRig()
