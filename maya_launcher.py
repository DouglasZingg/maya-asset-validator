import maya.cmds as cmds

SHELF_NAME = "DougTools"

# Ensure the main shelf tabLayout exists
if not cmds.control("ShelfLayout", exists=True):
    raise RuntimeError(
        "ShelfLayout not found. Turn on shelves: Windows > UI Elements > Shelves, "
        "or reset workspace: Windows > Workspaces > Reset Current Workspace."
    )

# Create the shelf if missing (parent is the shelf tabLayout)
if not cmds.shelfLayout(SHELF_NAME, exists=True):
    cmds.shelfLayout(SHELF_NAME, parent="ShelfLayout")

# Select our shelf tab
cmds.shelfTabLayout("ShelfLayout", edit=True, selectTab=SHELF_NAME)

cmd = r'''
import sys
sys.path.insert(0, r"C:\PATH\TO\maya-asset-validator")
import maya_launcher
maya_launcher.run()
'''

cmds.shelfButton(
    parent=SHELF_NAME,
    command=cmd,
    annotation="Maya Asset Validator",
    label="Validator",
    image="commandButton.png"
)

print(f"[Shelf] Added button to shelf: {SHELF_NAME}")
