
"""Maya Asset Validator launcher.

Safe to import: does not auto-create shelves or windows on import.

- run(): open the validator UI
- install_shelf(): create a shelf button that launches the UI (no hardcoded paths)

From Maya Script Editor (Python):

    import sys
    sys.path.insert(0, r"C:/path/to/maya-asset-validator")
    import maya_launcher
    maya_launcher.run()

Optional (recommended once):

    import sys
    sys.path.insert(0, r"C:/path/to/maya-asset-validator")
    import maya_launcher
    maya_launcher.install_shelf()

"""

from __future__ import annotations

import os
import sys
import importlib

import maya.cmds as cmds


def _repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _ensure_repo_on_syspath(repo_root: str | None = None) -> str:
    repo_root = os.path.abspath(repo_root or _repo_root())
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    return repo_root


def _reload_modules(module_names: list[str]) -> None:
    """Best-effort reload for iterative development."""
    for name in module_names:
        try:
            if name in sys.modules:
                importlib.reload(sys.modules[name])
        except Exception:
            pass


def run(repo_root: str | None = None) -> None:
    """Launch the validator UI."""
    _ensure_repo_on_syspath(repo_root)

    _reload_modules([
        "ui.validator_ui",
        "core.naming_checks",
        "core.transform_checks",
        "core.geometry_checks",
        "core.texture_checks",
        "core.auto_fix",
        "core.reporting",
    ])

    from ui import validator_ui
    validator_ui.show()


def install_shelf(shelf_name: str = "DougTools", repo_root: str | None = None) -> None:
    """Create a shelf button that launches the tool.

    This bakes the repo path into the shelf command so the user does NOT have to edit any files.
    """
    repo_root = _ensure_repo_on_syspath(repo_root)

    if not cmds.control("ShelfLayout", exists=True):
        raise RuntimeError(
            "ShelfLayout not found. Turn on shelves: Windows > UI Elements > Shelves, "
            "or reset workspace: Windows > Workspaces > Reset Current Workspace."
        )

    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.shelfLayout(shelf_name, parent="ShelfLayout")

    cmds.shelfTabLayout("ShelfLayout", edit=True, selectTab=shelf_name)

    cmd = f"""import sys
p=r"{repo_root}"
if p not in sys.path: sys.path.insert(0, p)
import maya_launcher
maya_launcher.run(p)
"""

    cmds.shelfButton(
        parent=shelf_name,
        command=cmd,
        annotation="Maya Asset Validator",
        label="Validator",
        image="commandButton.png",
    )

    print(f"[Shelf] Added 'Validator' button to shelf: {shelf_name}")
