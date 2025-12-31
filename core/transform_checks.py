import maya.cmds as cmds


def run_transform_checks(
    translate_tolerance=0.001,
    rotate_tolerance=0.01,
    scale_tolerance=0.001,
    pivot_tolerance=0.01
):
    """
    Validate transforms and pivots for transform nodes that have mesh shapes.

    Tolerances:
      - translate_tolerance: allowed deviation from 0.0
      - rotate_tolerance: allowed deviation from 0.0
      - scale_tolerance: allowed deviation from 1.0
      - pivot_tolerance: allowed distance from bbox center

    Returns:
        List[Dict]: validation results
    """
    results = []

    mesh_transforms = _list_mesh_transforms_long()

    for node in mesh_transforms:
        # --- Transform values ---
        t = cmds.getAttr(f"{node}.translate")[0]  # (x,y,z)
        r = cmds.getAttr(f"{node}.rotate")[0]
        s = cmds.getAttr(f"{node}.scale")[0]

        if _abs_any_gt(t, translate_tolerance):
            results.append(_warning(node, f"Translate not zero: {tuple(round(v, 4) for v in t)}"))

        if _abs_any_gt(r, rotate_tolerance):
            results.append(_warning(node, f"Rotate not zero: {tuple(round(v, 3) for v in r)}"))

        if _abs_any_gt((s[0] - 1.0, s[1] - 1.0, s[2] - 1.0), scale_tolerance):
            results.append(_warning(node, f"Scale not one: {tuple(round(v, 4) for v in s)}"))

        # --- Pivot vs bbox center ---
        bbox_center = _bbox_center_world(node)
        pivot = _rotate_pivot_world(node)

        if bbox_center and pivot:
            dist = _distance(bbox_center, pivot)
            if dist > pivot_tolerance:
                results.append(
                    _info(
                        node,
                        f"Pivot far from bbox center (dist {dist:.3f}). Pivot: {tuple(round(v, 3) for v in pivot)}"
                    )
                )

    return results


# ---------------------------
# Helpers
# ---------------------------
def _list_mesh_transforms_long():
    """
    Returns long-path transform nodes that directly parent mesh shapes.
    """
    meshes = cmds.ls(type="mesh", long=True) or []
    xforms = set()

    for shape in meshes:
        parent = cmds.listRelatives(shape, parent=True, fullPath=True)
        if parent:
            xforms.add(parent[0])

    return sorted(xforms)


def _bbox_center_world(node):
    """
    World-space bbox center from exactWorldBoundingBox.
    Returns (x,y,z) or None.
    """
    try:
        bb = cmds.exactWorldBoundingBox(node)  # [xmin,ymin,zmin,xmax,ymax,zmax]
        cx = (bb[0] + bb[3]) * 0.5
        cy = (bb[1] + bb[4]) * 0.5
        cz = (bb[2] + bb[5]) * 0.5
        return (cx, cy, cz)
    except Exception:
        return None


def _rotate_pivot_world(node):
    """
    World-space rotate pivot. Returns (x,y,z) or None.
    """
    try:
        rp = cmds.xform(node, q=True, ws=True, rp=True)  # [x,y,z]
        return (rp[0], rp[1], rp[2])
    except Exception:
        return None


def _distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return (dx*dx + dy*dy + dz*dz) ** 0.5


def _abs_any_gt(vals, tol):
    return any(abs(v) > tol for v in vals)


def _error(node, message):
    return {"level": "ERROR", "node": node, "message": message}


def _warning(node, message):
    return {"level": "WARNING", "node": node, "message": message}


def _info(node, message):
    return {"level": "INFO", "node": node, "message": message}
