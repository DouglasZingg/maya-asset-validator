import os
import re
import maya.cmds as cmds


_UDIM_PATTERN = re.compile(r"(?:<UDIM>|1001)")


def run_texture_checks():
    """
    Checks texture and material related issues:
      - missing texture file paths (file nodes)
      - empty texture paths
      - UDIM sanity (basic)
      - meshes with no material assignment beyond default (best-effort)

    Returns:
        List[Dict]: validation results
    """
    results = []

    # 1) File node texture path checks
    file_nodes = cmds.ls(type="file") or []
    for f in file_nodes:
        if not cmds.objExists(f"{f}.fileTextureName"):
            continue

        path = cmds.getAttr(f"{f}.fileTextureName") or ""

        if not path.strip():
            results.append(_error(f, "Texture path is empty"))
            continue

        # Normalize slashes for Windows/network paths
        norm = path.replace("\\", "/")

        # UDIM handling: accept <UDIM> token OR 1001-style
        if "<UDIM>" in norm:
            # Check if at least one UDIM tile exists by testing 1001 replacement
            test_path = norm.replace("<UDIM>", "1001")
            if not os.path.exists(test_path):
                results.append(_warning(f, f"UDIM texture missing (checked 1001): {path}"))
            continue

        # If it contains 1001 but no <UDIM>, still treat as possible UDIM
        if _UDIM_PATTERN.search(norm):
            # Try exact path first
            if os.path.exists(norm):
                continue
            # If 1001 present, try a basic glob-like check (1001 -> 1002) by just checking 1001
            test_path = norm
            if "1001" in norm and not os.path.exists(test_path):
                results.append(_warning(f, f"Possible UDIM texture missing (1001 not found): {path}"))
            continue

        # Non-UDIM: must exist exactly
        if not os.path.exists(norm):
            results.append(_error(f, f"Missing texture file: {path}"))

    # 2) Mesh material assignment checks (best-effort)
    # Flag meshes using only initialShadingGroup or having no shading engine assignments
    mesh_shapes = cmds.ls(type="mesh", long=True) or []
    for shape in mesh_shapes:
        if cmds.getAttr(f"{shape}.intermediateObject"):
            continue

        transform = _parent_transform(shape)

        sgs = cmds.listConnections(shape, type="shadingEngine") or []
        if not sgs:
            results.append(_warning(transform, "Mesh has no shadingEngine connections (no material assignment)"))
            continue

        # If only initialShadingGroup, warn (common pipeline rule)
        if all(sg == "initialShadingGroup" for sg in sgs):
            results.append(_info(transform, "Mesh appears to be using default material (initialShadingGroup)"))

    return results


# ---------------------------
# Helpers
# ---------------------------
def _parent_transform(shape):
    p = cmds.listRelatives(shape, parent=True, fullPath=True)
    return p[0] if p else shape


def _error(node, message):
    return {"level": "ERROR", "node": node, "message": message}


def _warning(node, message):
    return {"level": "WARNING", "node": node, "message": message}


def _info(node, message):
    return {"level": "INFO", "node": node, "message": message}
