import maya.cmds as cmds


def run_geometry_checks(max_ngon_verts=4):
    """
    Geometry integrity checks for mesh objects:
      - non-manifold vertices/edges (polyInfo)
      - lamina faces (polyInfo)
      - n-gons (faces with > max_ngon_verts) (polyInfo faceToVertex)
      - zero-area faces (best-effort heuristic)

    Returns:
        List[Dict]: validation results
    """
    results = []

    mesh_shapes = cmds.ls(type="mesh", long=True) or []
    if not mesh_shapes:
        return results

    for shape in mesh_shapes:
        # Skip intermediate shapes
        try:
            if cmds.getAttr(f"{shape}.intermediateObject"):
                continue
        except Exception:
            pass

        transform = _parent_transform(shape)

        # 1) Non-manifold vertices/edges
        nmv = _polyinfo_count(transform, nonManifoldVertices=True)
        nme = _polyinfo_count(transform, nonManifoldEdges=True)
        if nmv > 0 or nme > 0:
            results.append(_error(transform, f"Non-manifold geometry detected (verts: {nmv}, edges: {nme})"))

        # 2) Lamina faces
        lam = _polyinfo_count(transform, laminaFaces=True)
        if lam > 0:
            results.append(_error(transform, f"Lamina faces detected: {lam}"))

        # 3) N-gons
        ngon_faces = _count_ngons(transform, max_ngon_verts)
        if ngon_faces > 0:
            results.append(_warning(transform, f"N-gons detected (> {max_ngon_verts} verts): {ngon_faces}"))

        # 4) Zero-area faces (best-effort)
        zero_faces = _count_zero_area_faces(transform)
        if zero_faces > 0:
            results.append(_warning(transform, f"Possible degenerate/zero-area faces: {zero_faces}"))

    return results


# ---------------------------
# Helpers
# ---------------------------
def _parent_transform(shape):
    p = cmds.listRelatives(shape, parent=True, fullPath=True)
    return p[0] if p else shape


def _polyinfo_count(node, **kwargs):
    """
    Count items returned by cmds.polyInfo for a given flag.
    Example: _polyinfo_count(node, nonManifoldVertices=True)
    """
    try:
        info = cmds.polyInfo(node, **kwargs) or []
        return len(info)
    except Exception:
        return 0


def _count_ngons(transform, max_verts):
    try:
        face_count = cmds.polyEvaluate(transform, face=True) or 0
        if face_count == 0:
            return 0

        ngon_count = 0
        for i in range(face_count):
            face = f"{transform}.f[{i}]"
            verts = cmds.polyInfo(face, faceToVertex=True)
            if not verts:
                continue

            parts = verts[0].split()
            if ":" in parts:
                idx = parts.index(":")
                vids = parts[idx + 1:]
            else:
                vids = parts[2:]

            if len(vids) > max_verts:
                ngon_count += 1

        return ngon_count
    except Exception:
        return 0


def _count_zero_area_faces(transform):
    """
    Best-effort heuristic: repeated vertex ids on a face can indicate degenerate geometry.
    """
    try:
        face_count = cmds.polyEvaluate(transform, face=True) or 0
        if face_count == 0:
            return 0

        degenerate = 0
        for i in range(face_count):
            face = f"{transform}.f[{i}]"
            info = cmds.polyInfo(face, faceToVertex=True)
            if not info:
                continue

            parts = info[0].split()
            if ":" in parts:
                idx = parts.index(":")
                vids = parts[idx + 1:]
            else:
                vids = parts[2:]

            if len(vids) != len(set(vids)):
                degenerate += 1

        return degenerate
    except Exception:
        return 0


def _error(node, message):
    return {"level": "ERROR", "node": node, "message": message}


def _warning(node, message):
    return {"level": "WARNING", "node": node, "message": message}
