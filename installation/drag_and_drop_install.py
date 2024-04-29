from pathlib import Path
import os, sys, importlib


def install_mod():
    """Creates a .mod file in the Maya modules directory, which points to the
    repository & adds the scripts directory to sys.path."""

    module_name = "warpaint"

    root_dir = Path(__file__).parent.parent
    template_mod_filepath = Path(__file__).with_name("template.mod")
    mod_content = template_mod_filepath.read_text().format(name=module_name, path=root_dir.as_posix())

    # —— Install .mod file.
    target_mod_filepath = Path(os.getenv("MAYA_APP_DIR"), "modules", f"{module_name}.mod")
    target_mod_filepath.parent.mkdir(parents=True, exist_ok=True)
    target_mod_filepath.write_text(mod_content)

    # —— Add Scripts Directory to sys.path.
    scripts_dir = root_dir.joinpath("scripts")
    if scripts_dir.as_posix() in sys.path:
        sys.path.pop(sys.path.index(scripts_dir.as_posix()))

    sys.path.insert(1, scripts_dir.as_posix())


def onMayaDroppedPythonFile(*args, **kwargs):
    self = importlib.import_module(__name__)

    importlib.reload(self)
    self.install_mod()
