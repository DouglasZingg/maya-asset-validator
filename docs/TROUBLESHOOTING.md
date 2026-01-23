# Troubleshooting

## UI does not open
- Make sure you're running in **Script Editor → Python** (not MEL)
- Try running `maya_launcher.run()` again (it reloads modules best-effort)

## Shelf install errors
- Ensure shelves are visible:
  - **Windows → UI Elements → Shelves**
- If you use a custom workspace, try:
  - **Windows → Workspaces → Reset Current Workspace**

## Import errors (PySide / shiboken)
This tool tries in order:
- PySide6 / shiboken6 (Maya 2025+)
- PySide2 / shiboken2 (Maya 2020–2024)

If imports fail, verify your Maya version supports those modules.

## Paths / sys.path
If you see `No module named ...`, ensure you inserted the **repo root** folder:

```python
sys.path.insert(0, r"C:/tools/maya-asset-validator")
```

Not the `core/` or `ui/` subfolder.
