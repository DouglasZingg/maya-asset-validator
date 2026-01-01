import maya.cmds as cmds
import maya.mel as mel


def run_auto_fix(
    freeze_transforms=True,
    center_pivots=True,
    delete_unused=True
):
    """
    Runs a set of safe, production-style fixes.

    Returns:
        List[Dict]: actions performed (level/node/message) for UI reporting.
    """
    actions = []

    mesh_transforms = _list_mesh_transforms_long()

    cmds.undoInfo(openChunk=True)
    try:
        if freeze_transforms:
            count = 0
            for node in mesh_transforms:
                if not cmds.objExists(node):
                    continue
                # Make sure it's transformable
                try:
                    cmds.makeIdentity(node, apply=True, t=True, r=True, s=True, n=False, pn=True)
                    count += 1
                except Exception:
                    actions.append(_warning(node, "Failed to freeze transforms"))
            actions.append(_info("Scene", f"Freeze transforms attempted on {count} mesh transforms"))

        if center_pivots:
            count = 0
            for node in mesh_transforms:
                if not cmds.objExists(node):
                    continue
                try:
                    cmds.xform(node, centerPivots=True)
                    count += 1
                except Exception:
                    actions.append(_warning(node, "Failed to center pivot"))
            actions.append(_info("Scene", f"Center pivots attempted on {count} mesh transforms"))

        if delete_unused:
            # MEL is the normal pipeline way to do this
            try:
                mel.eval("hyperShadePanelMenuCommand(\"hyperShadePanel1\", \"deleteUnusedNodes\");")
                actions.append(_info("Scene", "Delete unused nodes executed"))
            except Exception:
                # Fallback command (sometimes works depending on UI state)
                try:
                    mel.eval("MLdeleteUnused;")
                    actions.append(_info("Scene", "Delete unused nodes executed (fallback)"))
                except Exception:
                    actions.append(_warning("Scene", "Failed to delete unused nodes (HyperShade may not be available)"))

    finally:
        cmds.undoInfo(closeChunk=True)

    return actions


# ---------------------------
# Helpers
# ---------------------------
def _list_mesh_transforms_long():
    meshes = cmds.ls(type="mesh", long=True) or []
    xforms = set()
    for shape in meshes:
        try:
            if cmds.getAttr(f"{shape}.intermediateObject"):
                continue
        except Exception:
            pass

        parent = cmds.listRelatives(shape, parent=True, fullPath=True)
        if parent:
            xforms.add(parent[0])
    return sorted(xforms)


def _info(node, message):
    return {"level": "INFO", "node": node, "message": message}


def _warning(node, message):
    return {"level": "WARNING", "node": node, "message": message}
