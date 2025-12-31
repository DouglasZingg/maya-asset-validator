import maya.cmds as cmds


def run_geometry_checks(max_ngon_verts=4):
    """
    Geometry integrity checks for mesh objects:
      - non-manifold vertices/edges
      - lamina faces
      - n-gons (faces with > max_ngon_verts)
      - zero-area faces (best-effort using polyInfo)

    Returns:
        List[Dict]: validation results
    """
    results = []

    mesh_shapes = cmds.ls(type="mesh", long=True) or []
    if not mesh_shapes:
        return results

    for shape in mesh_shapes:
        transform = _parent_transform(shape)

        # Skip intermediate shapes
        if cmds.getAttr(f"{shape}.intermediateObject"):
            continue

        # 1) Non-manifold
        nm_verts = _count_poly_select(transform, "polySelectConstraint -mode 3 -type 0x0001 -nonManifold 1;")
        nm_edges = _count_poly_select(transform, "polySelectConstraint -mode 3 -type 0x8000 -nonManifold 1;")

        if nm_verts > 0 or nm_edges > 0:
            results.append(_error(transform, f"Non-manifold geometry detected (verts: {nm_verts}, edges: {nm_edges})"))

        # 2) Lamina faces
        lamina_faces = _count_poly_select(transform, "polySelectConstraint -mode 3 -type 0x0008 -lamina 1;")
        if lamina_faces > 0:
            results.append(_error(transform, f"Lamina faces detected: {lamina_faces}"))

        # 3) N-gons
        ngon_faces = _count_ngons(transform, max_ngon_verts)
        if ngon_faces > 0:
            results.append(_warning(transform, f"N-gons detected (> {max_ngon_verts} verts): {ngon_faces}"))

        # 4) Zero-area faces (best-effort)
        zero_faces = _count_zero_area_faces(transform)
        if zero_faces > 0:
            results.append(_warning(transform, f"Possible zero-area faces: {zero_faces}"))

    # Always clear selection constraints so we don't affect the user
    _reset_constraints()
    cmds.select(clear=True)

    return results


# ---------------------------
# Helpers
# ---------------------------
def _parent_transform(shape):
    p = cmds.listRelatives(shape, parent=True, fullPath=True)
    return p[0] if p else shape


def _reset_constraints():
    try:
        cmds.polySelectConstraint(disable=True)
    except Exception:
        pass


def _count_poly_select(transform, mel_cmd):
    """
    Use polySelectConstraint via MEL commands.
    Returns number of selected components for that constraint.
    """
    import maya.mel as mel

    cmds.select(transform, r=True)

    # Reset constraints first
    _reset_constraints()

    try:
        mel.eval(mel_cmd)
        # Apply constraint by reselecting
        cmds.select(transform, r=True)
        sel = cmds.ls(sl=True, fl=True) or []
        return len(sel)
    except Exception:
        return 0
    finally:
        _reset_constraints()


def _count_ngons(transform, max_verts):
    """
    Counts faces with more than max_verts vertices.
    Uses polyEvaluate and iterates faces.
    """
    try:
        face_count = cmds.polyEvaluate(transform, face=True) or 0
        if face_count == 0:
            return 0

        ngon_count = 0
        for i in range(face_count):
            face = f"{transform}.f[{i}]"
            verts = cmds.polyInfo(face, faceToVertex=True)
            # Example: 'FACE 0:    1 2 3 4 5'
            if not verts:
                continue
            parts = verts[0].split()
            # last tokens are vertex indices
            # find the ':' then count after it
            if ":" in parts:
                idx = parts.index(":")
                vcount = len(parts[idx+1:])
            else:
                # fallback: subtract first two tokens ('FACE', '0:')
                vcount = max(0, len(parts) - 2)

            if vcount > max_verts:
                ngon_count += 1
        return ngon_count
    except Exception:
        return 0


def _count_zero_area_faces(transform):
    """
    Best-effort detection of zero-area faces.
    Maya doesn't expose a direct polyEvaluate for zero-area.
    We can sometimes detect via polyInfo/cleanup patterns,
    but here we do a minimal heuristic:
      - faces with duplicated vertex listing
    """
    try:
        face_count = cmds.polyEvaluate(transform, face=True) or 0
        if face_count == 0:
            return 0

        zero_like = 0
        for i in range(face_count):
            face = f"{transform}.f[{i}]"
            info = cmds.polyInfo(face, faceToVertex=True)
            if not info:
                continue
            parts = info[0].split()
            # collect vertex ids after ':'
            if ":" in parts:
                idx = parts.index(":")
                vids = parts[idx+1:]
            else:
                vids = parts[2:]

            # if there are repeated vertex ids in a face, it can indicate degenerate geometry
            if len(vids) != len(set(vids)):
                zero_like += 1

        return zero_like
    except Exception:
        return 0


def _error(node, message):
    return {"level": "ERROR", "node": node, "message": message}


def _warning(node, message):
    return {"level": "WARNING", "node": node, "message": message}
