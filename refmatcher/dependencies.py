import bpy
import os
import sys
import subprocess
import importlib
import importlib.util
from typing import Iterable
import refmatcher

DEPENDENCIES = {("scipy", "scipy", "1.12.0")} # package_name, module_name, version
MODULES_PATH = bpy.utils.user_resource('SCRIPTS', path=os.path.join("addons", refmatcher.__name__, "modules"), create=True)

def get_missing_dependencies() -> Iterable[str]:
    return [package_name for package_name, module_name, _ in DEPENDENCIES if not os.path.isfile(os.path.join(MODULES_PATH, module_name, "__init__.py"))]

def check_dependencies() -> bool:
    return all(os.path.isfile(os.path.join(MODULES_PATH, module_name, "__init__.py")) for _, module_name, _ in DEPENDENCIES)

def check_dependency(module_name: str) -> bool:
    return os.path.isfile(os.path.join(MODULES_PATH, module_name, "__init__.py"))

def install_dependencies() -> bool:
    python_exe = sys.executable
    success_ensurepip = subprocess.call([python_exe, "-m", "ensurepip"]) == 0
    success_upgradepip = subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip", '--verbose']) == 0
    success_install_packages = True
    for package_name, _, version in DEPENDENCIES:
        if version:
            package_name += f"=={version}"
        success_install_packages = success_install_packages and subprocess.call([python_exe, "-m", "pip", "install", package_name, "--target", MODULES_PATH, "--verbose"]) == 0
    return success_ensurepip and success_upgradepip and success_install_packages

def expose_module(module_name: str) -> bool:
    file_path = os.path.join(MODULES_PATH, module_name, "__init__.py")
    if os.path.isfile(file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return True
    return False
