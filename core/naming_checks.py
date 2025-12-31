import maya.cmds as cmds


def run_naming_checks():
    """
    Runs naming convention checks on the current Maya scene.

    Returns:
        List[Dict]: validation results with fields:
            - level: "ERROR" | "WARNING" | "INFO"
            - node: full DAG path to the transform
            - message: description of the issue
    """
    results = []

    all_transforms = cmds.ls(type="transform", long=True)

    seen_names = set()

    for node in all_transforms:
        short_name = node.split("|")[-1]

        # Duplicate short names
        if short_name in seen_names:
            results.append(_error(node, "Duplicate object name"))
        else:
            seen_names.add(short_name)

        # Enforce lowercase naming (studio-common rule)
        if any(c.isupper() for c in short_name):
            results.append(_error(node, "Object name contains uppercase letters (use lowercase)"))


        # Shape-based rules
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []

        # If this transform has shapes, apply type rules
        for shape in shapes:
            shape_type = cmds.nodeType(shape)

            if shape_type == "mesh":
                if not short_name.startswith("geo_"):
                    results.append(_warning(node, "Mesh transform should start with 'geo_'"))

            # Note: joints are transforms themselves; still safe to check if encountered as shape
            elif shape_type == "joint":
                if not short_name.startswith("jnt_"):
                    results.append(_warning(node, "Joint should start with 'jnt_'"))

        # Group rule (no shapes)
        if not shapes:
            if not short_name.startswith("grp_"):
                results.append(_info(node, "Empty transform should start with 'grp_'"))

    return results


# ---------------------------
# Result Helpers
# ---------------------------
def _error(node, message):
    return {"level": "ERROR", "node": node, "message": message}


def _warning(node, message):
    return {"level": "WARNING", "node": node, "message": message}


def _info(node, message):
    return {"level": "INFO", "node": node, "message": message}
