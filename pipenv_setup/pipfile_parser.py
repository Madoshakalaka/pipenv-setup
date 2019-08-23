from typing import Tuple, Dict

# noinspection Mypy
from pipfile import Pipfile

from pipenv_setup.constants import PipfileConfig


def is_remote_package(config: PipfileConfig) -> bool:
    if isinstance(config, dict) and "path" not in config:
        return True
    return False


def get_default_packages(
    parsed_pipfile: Pipfile
) -> Tuple[Dict[str, PipfileConfig], Dict[str, PipfileConfig]]:
    """
    return local packages and remote packages in default packages (not dev)
    """
    local_packages: Dict[str, PipfileConfig] = {}
    remote_packages: Dict[str, PipfileConfig] = {}
    for package_name, config in parsed_pipfile.data["default"].items():
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages
