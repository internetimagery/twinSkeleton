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
        winName = "Export_Rig"
        if cmds.window(winName, ex=True):
            cmds.deleteUI(winName)
        s.win = cmds.window(rtf=True, w=300, t="Export Animation")
        cmds.columnLayout(adj=True)
        cmds.rowLayout(nc=2, adj=2)
        cmds.text(l="(optional) Prefix:")
        s.prefix = cmds.textField()
        cmds.setParent("..")
        cmds.rowLayout(nc=2, adj=2)
        cmds.checkBoxGrp(l="Include Mesh in Export", cc=s.meshTextActive)
        s.mesh = cmds.textField(en=False, pht="Mesh Name")
        cmds.setParent("..")
        cmds.button(l="Load Template and Build Rig", h=100, c=s.export)
        cmds.showWindow(s.win)

    """
    Activate Mesh textfield
    """
    def meshTextActive(s, state):
        cmds.textField(s.mesh, e=True, en=state)

    """
    Export the rig animation!
    """
    def export(s, *junk):
        prefix = cmds.textField(s.prefix, q=True, tx=True).strip()
        origSelection = cmds.ls(sl=True) # Store original selection to return to
        skeleton = s.locateSkeleton()

    """
    Select the skeleton
    """
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
