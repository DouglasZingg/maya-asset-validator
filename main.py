import importlib
import sys


def run():
    """
    Entry point for launching the tool inside Maya.
    Ensures UI module is reloaded during development.
    """
    import ui.validator_ui  # ensure module is imported first

    # Reload UI only if already loaded (dev workflow)
    if "ui.validator_ui" in sys.modules:
        importlib.reload(ui.validator_ui)

    ui.validator_ui.show()
