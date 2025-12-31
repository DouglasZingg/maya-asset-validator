import importlib
import sys

def run():
    # Import UI module first
    import ui.validator_ui

    # Reload ONLY if already loaded
    if "ui.validator_ui" in sys.modules:
        importlib.reload(ui.validator_ui)

    ui.validator_ui.show()
