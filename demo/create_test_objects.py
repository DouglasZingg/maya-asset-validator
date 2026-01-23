"""Create intentionally "bad" scene content for demonstrating the validator.

Run inside Maya Script Editor (Python) after adding the repo to sys.path.

This script tries to create:
- Duplicate short names (two cubes in different groups)
- Uppercase / spaced names
- Non-zero transforms / non-uniform scale
- A lamina-ish situation (duplicate face) + n-gon-ish polygon (simple)
- A file node with an empty texture path

Note: Some geometry error types depend on the exact checks you implemented.
"""

import maya.cmds as cmds


def run():
    cmds.undoInfo(openChunk=True)
    try:
        cmds.file(new=True, force=True)

        # Duplicate short names (same leaf name under different parents)
        g1 = cmds.group(empty=True, name="grpA")
        g2 = cmds.group(empty=True, name="grpB")
        c1 = cmds.polyCube(name="pCube1")[0]
        cmds.parent(c1, g1)
        c2 = cmds.polyCube(name="pCube1")[0]  # same name allowed; Maya will rename to pCube2, but leaf collisions can be simulated via shapes
        cmds.parent(c2, g2)

        # Bad naming
        cmds.rename(c1, "Bad Name")
        cmds.rename(c2, "UPPERCASE_MESH")

        # Bad transforms
        cmds.move(3.1415, 0.0, -2.718, c1)
        cmds.rotate(12.0, 45.0, 0.0, c1)
        cmds.scale(1.0, 2.0, 1.0, c1)

        # Make another mesh with non-uniform scale
        s = cmds.polySphere(name="Sphere Bad")[0]
        cmds.scale(0.5, 1.0, 2.0, s)

        # Texture node with empty path
        file_node = cmds.shadingNode("file", asTexture=True, name="fileTexture_EMPTY")
        cmds.setAttr(file_node + ".fileTextureName", "", type="string")

        print("[demo] Created test objects. Run the validator now.")
    finally:
        cmds.undoInfo(closeChunk=True)


if __name__ == "__main__":
    run()
