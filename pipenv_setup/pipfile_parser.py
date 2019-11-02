from typing import Tuple, Dict

import pipfile
from requirementslib import Requirement
from vistir.compat import Path
from six import string_types
from pipenv_setup.constants import PipfileConfig, vcs_list


def format_remote_package(
    package_name, config, dev=False
):  # type: (str, PipfileConfig, bool) -> Tuple[str, str]
    """
    format and return a string that can be put into either install_requires or dependency_links or extras_require

    :param package_name:
    :param config:
    :param dev: is package a development package
    :return: Tuple[keyword_target, list_argument]
    :raise ValueError: if a package config is not understood
    """
    if dev:
        return (
            "extras_require",
            Requirement.from_pipfile(package_name, config).as_line(
                include_hashes=False
            ),
        )
    else:
        # fixme: stronger checks?
        # https://setuptools.readthedocs.io/en/latest/setuptools.html#dependencies-that-aren-t-in-pypi
        if "file" in config:  # remote built distribution '.zip' file for example
            assert isinstance(config, dict)
            return "dependency_links", config["file"]
        if is_pypi_package(config):  # pypi package
            return (
                "install_requires",
                Requirement.from_pipfile(package_name, config).as_line(
                    include_hashes=False
                ),
            )
        else:  # vcs
            assert isinstance(config, dict)
            if "git" in config:
                vcs = "git"
            # fixme: test cases other than git
            elif "bzr" in config:
                vcs = "bzr"
            elif "svn" in config:
                vcs = "svn"
            elif "hg" in config:
                vcs = "hg"
            else:
                raise ValueError(
                    "Can not understand config of package %s" % package_name
                )

            link = "{vcs}+{link}".format(vcs=vcs, link=config[vcs])
            if "ref" in config:
                link += "@" + config["ref"]
            link += "#egg=" + package_name
            return "dependency_links", link


def is_vcs_package(config):  # type: (PipfileConfig) -> bool
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


def is_pypi_package(config):  # type: (PipfileConfig) -> bool
    # fixme: uh.. I guess there are special cases
    if isinstance(config, string_types):
        return True
    elif (
        isinstance(config, dict)
        and not is_vcs_package(config)
        and "file" not in config
        and "path" not in config
    ):
        return True
    return False


def is_remote_package(config):  # type: (PipfileConfig) -> bool
    if isinstance(config, dict) and "path" not in config:
        return True
    if isinstance(config, string_types):
        return True
    return False


def get_default_packages(
    pipfile_path,
):  # type: (Path) -> Tuple[Dict[str, PipfileConfig], Dict[str, PipfileConfig]]
    """
    return local packages and remote packages in default packages (not dev)
    """
    local_packages = {}  # type: Dict[str, PipfileConfig]
    remote_packages = {}  # type: Dict[str, PipfileConfig]
    for package_name, config in pipfile.load(str(pipfile_path)).data["default"].items():
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages


def get_dev_packages(
    pipfile_path,
):  # type: (Path) -> Tuple[Dict[str, PipfileConfig], Dict[str, PipfileConfig]]
    """
    return dev local packages and dev remote packages
    """
    local_packages = {}  # type: Dict[str, PipfileConfig]
    remote_packages = {}  # type: Dict[str, PipfileConfig]

    for package_name, config in pipfile.load(str(pipfile_path)).data["develop"].items():
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages
