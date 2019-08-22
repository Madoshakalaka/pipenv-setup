import traceback
from sys import stderr
from typing import Tuple, Union, List, Dict, Optional

# noinspection Mypy
from pipfile import Pipfile

from pipenv_setup.constants import Config


def is_remote_package(config: Config) -> bool:
    if isinstance(config, dict) and "path" not in config:
        return True
    return False


def get_default_packages(
    parsed_pipfile: Pipfile
) -> Tuple[Dict[str, Config], Dict[str, Config]]:
    """
    return local packages and remote packages in default packages (not dev)
    """
    local_packages: Dict[str, Config] = {}
    remote_packages: Dict[str, Config] = {}
    for package_name, config in parsed_pipfile.data["default"].items():
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages
