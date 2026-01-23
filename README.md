# Maya Asset Validator

A production-style **validation + auto-fix** tool for Autodesk Maya (2020–2026) built with Python + Qt.

## What it does
- **Validate Scene**: naming, transforms, geometry, and texture checks
- **Clear Results**: reset UI output
- **Select on click** (if implemented in your UI): quickly find offending nodes
- **Optional Auto Fix** (if enabled in your build): safe fixes like freeze transforms / center pivots / delete unused nodes
- **Reports**: JSON/TXT output (if enabled in your build)

## Compatibility
The UI imports Qt based on Maya version:
- Maya 2025+ → PySide6 / shiboken6
- Maya 2020–2024 → PySide2 / shiboken2

---

## Quickstart (run from Script Editor)
1) Download/clone this repo to any folder, e.g. `C:/tools/maya-asset-validator`
2) In **Maya → Script Editor → Python**, run:

```python
import sys
sys.path.insert(0, r"C:/path/to/maya-asset-validator")
import maya_launcher
maya_launcher.run()
```

---

## Install a shelf button (recommended)
Run this once in **Maya → Script Editor → Python**:

```python
import sys
sys.path.insert(0, r"C:/tools/maya-asset-validator")
import maya_launcher
maya_launcher.install_shelf(shelf_name="DougTools")
```

After that, use the **DougTools** shelf → **Validator** button.

---

## Demo / Testing walkthrough (for reviewers)
This repo includes a demo scene file:
- `demo/validator.mb`

### A) Open the demo scene
- In Maya: **File → Open Scene** → select `demo/validator.mb`

### B) Launch the tool
Use either Quickstart run (above) or the shelf button.

### C) Click **Validate Scene**
You should see results like:
- Naming issues (uppercase / spaces / duplicates)
- Transform issues (non-zero transforms / non-uniform scale)
- Geometry issues (non-manifold / lamina / n-gons) depending on your rules
- Texture issues (missing or empty file paths)

### D) Optional: create test objects yourself
If you want to generate some intentionally bad test objects, run:
- `demo/create_test_objects.py` in maya script editor

---

## Repo layout
```
maya-asset-validator/
  core/                 # validation checks + auto-fix + reporting
  ui/                   # PySide UI
  demo/                 # demo scene + demo scripts
  maya_launcher.py      # safe entrypoints + shelf installer
  main.py               # optional entrypoint (if present)
```

---

## Troubleshooting
See `docs/TROUBLESHOOTING.md`.

Common fixes:
- If nothing shows, ensure shelves are enabled:
  **Windows → UI Elements → Shelves**
- If imports fail after editing files, re-run `maya_launcher.run()` (reloads modules best-effort).

---

## License
MIT (see `LICENSE`).
