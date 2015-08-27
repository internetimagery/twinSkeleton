# Export rig by baking out curves first
import maya.cmds as cmds
import maya.mel as mel
from os.path import join, exists, basename, splitext
from makeRig import NameSpace, GetRoot


class ExportRig (object):
    """
    select all joints, bake keyframes onto them and export, then undo action
    """
    def __init__(s):
        if "fbxmaya" in cmds.pluginInfo( query=True, listPlugins=True ):
            sceneName, ext = splitext(basename(cmds.file(q=True, sn=True)))
            parseName = sceneName.split("@")
            if 1 < len(parseName) and parseName[0] and parseName[1]:
                animName = parseName[1]
                charName = parseName[0]
            else:
                animName = ""
                charName = ""
            winName = "Export_Rig_Window"
            if cmds.window(winName, ex=True):
                cmds.deleteUI(winName)
            s.win = cmds.window(rtf=True, w=300, t="Export Animation")
            cmds.columnLayout(adj=True)
            s.prefix = cmds.textFieldGrp(l="(optional) Prefix: ")
            s.animOnly = cmds.checkBoxGrp(l="Export Animation Only? ")
            s.charName = cmds.textFieldGrp(l="Character Name: ", tx=charName, cc=lambda x: s.validateFilename(s.charName, x))
            s.animName = cmds.textFieldGrp(l="Animation Name: ", tx=animName, cc=lambda x: s.validateFilename(s.animName, x))
            s.fileName = cmds.textFieldButtonGrp(ed=False, l="Save Folder: ", bl="Open", bc=s.validateDirName)
            s.exportBtn = cmds.button(l="Export Animation", h=80, c=s.export, en=False)
            cmds.showWindow(s.win)
            s.valid = {
                s.charName : False,
                s.animName : False,
                s.fileName : False
            }
        else:
            cmds.confirmDialog(t="Oh no", m="Can't find the FBX plugin.\nIs it loaded?")

    """
    Validate Character / Animation filename
    """
    def validateFilename(s, control, text):
        if 120 < len(text):
            s.valid[control] = False
            cmds.textFieldGrp(control, e=True, bgc=(1,0.4,0.4))
            return s.activateExportButton()
        for invalid in ["*", "|", "\\", "/", ":", "\"", "<", ">", "?"]:
            if invalid in text:
                s.valid[control] = False
                cmds.textFieldGrp(control, e=True, bgc=(1,0.4,0.4))
                return s.activateExportButton()
        s.valid[control] = True
        cmds.textFieldGrp(control, e=True, bgc=(0.3,1,0.3))
        s.activateExportButton()

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
            s.activateExportButton()
        else:
            s.valid[s.fileName] = False
            cmds.textFieldButtonGrp(s.fileName, e=True, bgc=(1,0.4,0.4))
            s.activateExportButton()

    """
    Activate Export button
    """
    def activateExportButton(s):
        for v in s.valid:
            if not s.valid[v]:
                return cmds.button(s.exportBtn, e=True, en=False)
        cmds.button(s.exportBtn, e=True, en=True)

    """
    Export the rig animation!
    """
    def export(s, *junk):
        filePath = "%s/%s@%s.fbx" % (
                cmds.textFieldButtonGrp(s.fileName, q=True, tx=True),
                cmds.textFieldGrp(s.charName, q=True, tx=True).strip().lower().title(),
                cmds.textFieldGrp(s.animName, q=True, tx=True).strip().lower().title())
        if not exists(filePath) or "Yes" == cmds.confirmDialog(
                                            t="Just a moment...",
                                            m="The file currently exists. Override?",
                                            button=["Yes","No"],
                                            defaultButton="Yes",
                                            cancelButton="No",
                                            dismissString="No"):
            prefix = cmds.textFieldGrp(s.prefix, q=True, tx=True).strip()
            baseName = NameSpace(GetRoot(), prefix)
            baseObj = cmds.ls(baseName, r=True)

            if baseObj:
                with Undo():
                    # cmds.select(cl=True)
                    cmds.select(baseObj, r=True)
                    # cmds.select(baseObj, hi=True, tgl=True)
                    # Prepare FBX command
                    commands =  """
FBXResetExport; FBXExportInAscii -v true;
FBXExportCameras -v false; FBXExportLights -v false;
FBXExportUpAxis %s; FBXExportUseSceneName -v false;
FBXExportGenerateLog -v false; FBXExportConstraints -v false;
FBXExportAxisConversionMethod addFbxRoot;
FBXExportApplyConstantKeyReducer -v true;
""" % cmds.upAxis(q=True, ax=True)
                    if cmds.checkBoxGrp(s.animOnly, q=True, v1=True):
                        commands += """
FBXExportAnimationOnly -v true;
"""
                    else:
                        commands += """
FBXExportSkins -v true;
FBXExportShapes -v true;
FBXExportInputConnections -v false;
FBXExportEmbeddedTextures -v false;
FBXExportSmoothMesh -v false;
FBXExportSmoothingGroups -v true;
FBXExportTangents -v true;
"""
                    commands += "FBXExport -f \"%s\" -s;" % filePath
                    cmds.bakeResults( baseObj,
                        t=(
                            cmds.playbackOptions(min=True, q=True),
                            cmds.playbackOptions(max=True, q=True)),
                        attribute=[
                            "tx", "ty", "tz",
                            "rx", "ry", "rz",
                            "sx", "sy", "sz"
                        ],
                        hierarchy="below",
                        simulation=True,
                        disableImplicitControl=True,
                        sparseAnimCurveBake=True,
                        removeBakedAttributeFromLayer=True,
                        minimizeRotation=True,
                        smart=(True, 5)
                        )
                    # Clean up extra channels that are not used
                    cmds.delete(cmds.listRelatives(baseObj, ad=True, pa=True, ni=True) + baseObj, sc=True)
                    # Export the FBX file
                    mel.eval(commands)
                    cmds.deleteUI(s.win)
                    cmds.confirmDialog(t="Nice", m="Animation Exported. Woot!")
            else:
                cmds.confirmDialog(t="Bugger...", m="Couldn't find a matching rig.")

"""
Keep undos tidy
"""
class Undo(object):
    def __enter__(s):
        cmds.undoInfo(ock=True)
        s.selection = cmds.ls(sl=True) # Store original selection to return to

    def __exit__(s, err, type, trace):
        cmds.undoInfo(cck=True)
        cmds.undo()
        cmds.select(s.selection, r=True)
