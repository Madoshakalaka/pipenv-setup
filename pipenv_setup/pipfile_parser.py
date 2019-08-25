from typing import Tuple, Dict

# noinspection Mypy
from pipfile import Pipfile

from pipenv_setup.constants import PipfileConfig, vcs_list


def is_vcs_package(config: PipfileConfig):
    """
    >>> is_vcs_package('==1.6.2')
    False
    >>> is_vcs_package({"git": "https://github.com/django/django.git","editable": True})
    True
    >>> is_vcs_package({'file': "https://www.a.com/b/c.zip"})
    False
    >>> is_vcs_package({'path': "/home/weeb27/phubscraper"})
    False
    """
    if isinstance(config, dict):
        return any(filter(config.__contains__, vcs_list))
    return False


def is_pypi_package(config: PipfileConfig) -> bool:
    # fixme: uh.. I guess there are special cases
    if isinstance(config, str):
        return True
    elif (
        isinstance(config, dict)
        and not is_vcs_package(config)
        and "file" not in config
        and "path" not in config
    ):
        return True
    return False


def is_remote_package(config: PipfileConfig) -> bool:
    if isinstance(config, dict) and "path" not in config:
        return True
    if isinstance(config, str):
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
