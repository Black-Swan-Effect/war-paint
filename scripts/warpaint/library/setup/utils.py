from warpaint import ROOT_DIR
from warpaint.library.setup.template import BaseTemplate
import sys


def reload_modules():
    """Deletes all instances of the module and reloads the module by removing
    it from the sys.modules, effectively refreshing the codebase."""

    BaseTemplate.del_instances()

    for module in sys.modules.copy():
        if module.startswith(ROOT_DIR.name):
            del sys.modules[module]
