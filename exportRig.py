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
        s.prefix = cmds.textFieldGrp(l="(optional) Prefix: ")
        s.meshRow = cmds.rowLayout(nc=2, adj=2)
        cmds.checkBoxGrp(l="Include Mesh in Export", cc=s.meshTextActive)
        s.mesh = cmds.textField(en=False, pht="Mesh Name: ", cc=lambda x: s.meshTextValidate(s.mesh, x))
        cmds.setParent("..")
        s.charName = cmds.textFieldGrp(l="Character Name: ", cc=lambda x: s.validateFilename(s.charName, x))
        s.animName = cmds.textFieldGrp(l="Animation Name: ", cc=lambda x: s.validateFilename(s.animName, x))
        s.fileName = cmds.textFieldButtonGrp(ed=False, l="Save Folder: ", bl="Open", bc=s.validateDirName)
        s.animName = cmds.textFieldGrp(l="Animation Name: ", cc=lambda x: s.validateFilename(s.animName, x))
        cmds.button(l="Export Animation", h=80, c=s.export)
        cmds.showWindow(s.win)
        s.valid = {
            s.mesh : True,
            s.charName : False,
            s.animName : False,
            s.fileName : False
        }

    """
    Activate Mesh textfield
    """
    def meshTextActive(s, state):
        cmds.textField(s.mesh, e=True, en=state)
        text = cmds.textField(s.mesh, q=True, tx=True).strip()
        if state and text:
            s.meshTextValidate(text)

    """
    Validate Mesh textfield
    """
    def meshTextValidate(s, control, text):
        text = text.strip()
        if cmds.objExists(text):
            s.valid[control] = True
            cmds.rowLayout(s.meshRow, e=True, bgc=(0.3,1,0.3))
            cmds.textField(s.mesh, e=True, bgc=(0.3,1,0.3))
        else:
            s.valid[control] = False
            cmds.textField(s.mesh, e=True, bgc=(1,0.4,0.4))
            cmds.rowLayout(s.meshRow, e=True, bgc=(1,0.4,0.4))

    """
    Validate Character / Animation filename
    """
    def validateFilename(s, control, text):
        if 120 < len(text):
            s.valid[control] = False
            return cmds.textFieldGrp(control, e=True, bgc=(1,0.4,0.4))
        for invalid in ["*", "|", "\\", "/", ":", "\"", "<", ">", "?"]:
            if invalid in text:
                s.valid[control] = False
                return cmds.textFieldGrp(control, e=True, bgc=(1,0.4,0.4))
        s.valid[control] = True
        cmds.textFieldGrp(control, e=True, bgc=(0.3,1,0.3))

    """
    Load file name for saving
    """
    def validateDirName(s, *path):
        path = cmds.fileDialog2(fm=3) # Save file
        if path:
            cmds.textFieldGrp(s.fileName, e=True, tx=path[0])
        if cmds.textFieldGrp(s.fileName, q=True, tx=True):
            s.valid[s.fileName] = True
            cmds.textFieldGrp(s.fileName, e=True, bgc=(0.3,1,0.3))
        else:
            s.valid[s.fileName] = False
            cmds.textFieldButtonGrp(s.fileName, e=True, bgc=(1,0.4,0.4))

    """
    Export the rig animation!
    """
    def export(s, *junk):
        path = cmds.fileDialog2(dialogStyle=2, fm=3) # Save file

        # prefix = cmds.textField(s.prefix, q=True, tx=True).strip()
        # origSelection = cmds.ls(sl=True) # Store original selection to return to
        # skeleton = s.locateSkeleton()

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
