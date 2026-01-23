# Setup

## Requirements
- Autodesk Maya 2020–2026
- No external Python install required (runs inside Maya)

## Running
1. Download/clone repo (example: `C:/tools/maya-asset-validator`)
2. In Maya Script Editor (Python):

```python
import sys
sys.path.insert(0, r"C:/tools/maya-asset-validator")
import maya_launcher
maya_launcher.run()
```

## Shelf button
Run once:

```python
import sys
sys.path.insert(0, r"C:/tools/maya-asset-validator")
import maya_launcher
maya_launcher.install_shelf(shelf_name="DougTools")
```
