# Maya Asset Validator

A production-style Maya validation tool built with Python and Qt (PySide6/PySide2 compatible) to enforce pipeline standards and prevent common scene issues before publishing.

## Features
- Naming convention checks (duplicates, type prefixes)
- Transform checks (translate/rotate/scale tolerances)
- Pivot checks (pivot distance from bbox center)
- Geometry checks (non-manifold, lamina, n-gons)
- Texture checks (missing/empty paths, UDIM sanity)
- Auto Fix (freeze transforms, center pivots, delete unused nodes) with undo support
- Export validation reports (JSON/TXT)
- UI polish: severity filter, search, summary counts, double-click selects objects

## Tech Stack
- Python (Maya embedded Python)
- Qt UI: PySide6 (Maya 2026+) with backwards compatibility to PySide2/PySide
- Maya Python API (`maya.cmds`)

## Installation
1. Clone/download this repo to a folder on your machine.
2. In Maya: **Script Editor → Python**, run:

***NOTE: You need to change the file path on line 21 in maya_launcher***
```python
import sys
sys.path.append(r"C:\PATH\TO\maya-asset-validator")

import maya_launcher
maya_launcher.run()


