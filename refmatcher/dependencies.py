import bpy
import os
import sys
import subprocess
import importlib
from importlib.metadata import version
import site
from typing import Iterable

DEPENDENCIES = {"scipy" : "1.12.0"}

def get_missing_dependencies() -> Iterable[str]:
    return (module for module in DEPENDENCIES if importlib.util.find_spec(module) is None)

def check_dependencies() -> bool:
    return all(importlib.util.find_spec(module) is not None for module in DEPENDENCIES)

def get_unmatched_versions() -> dict[str, tuple[str, str]]:
    """Returns a dictionary of wrongly versioned package names with their installed and required versions."""
    unmatched_versions = {}
    for package_name, required_version in DEPENDENCIES.items():
        if importlib.util.find_spec(package_name) is not None:
            installed_version = version(package_name)
            if installed_version != required_version:
                unmatched_versions[package_name] = (installed_version, required_version)
    return unmatched_versions

def check_versions() -> bool:
    return not get_unmatched_versions()

def install_dependencies() -> bool:
    modules_path = bpy.utils.user_resource('SCRIPTS', path=os.path.join('addons', 'modules'), create=True) # TODO: try os.path.join('addons', 'refmatcher', 'modules')
    python_exe = sys.executable
    success_ensurepip = subprocess.call([python_exe, "-m", "ensurepip"]) == 0
    success_upgradepip = subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip", '--verbose']) == 0
    success_install_packages = True
    for package_name, version in DEPENDENCIES.items():
        if version:
            package_name += f"=={version}"
        success_install_packages = success_install_packages and subprocess.call([python_exe, "-m", "pip", "install", package_name, "--target", modules_path, "--verbose", "--force-reinstall"]) == 0
    importlib.reload(site) # refresh accessible modules
    return success_ensurepip and success_upgradepip and success_install_packages
