from typing import Tuple, Dict

try:
    from requirementslib import Lockfile
except AssertionError:
    import os

    os.environ["SETUPTOOLS_USE_DISTUTILS"] = "stdlib"
    from requirementslib import Lockfile

from requirementslib import Requirement
from pathlib import Path

from pipenv_setup.constants import LockConfig


def is_remote_package(config):  # type: (LockConfig) -> bool
    """
    This function is written according to the following file
    https://github.com/pypa/pipfile/blob/master/examples/Pipfile.lock
    """
    # fixme: stronger checks?
    if "path" in config:  # local package
        return False
    return True


def format_remote_package(
    package_name: str, config: LockConfig, dev=False, use_dependency_links=False
) -> Tuple[str, str]:
    """
    format and return a string that can be put into either install_requires or dependency_links or extras_require

    :param package_name:
    :param config:
    :param dev: is package a development package
    :param use_dependency_links: use deprecated dependency_links field
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
            if use_dependency_links:
                return "dependency_links", config["file"]
            else:
                return "install_requires", config["file"]
        if "version" in config:  # pypi package
            return (
                "install_requires",
                Requirement.from_pipfile(package_name, config).as_line(
                    include_hashes=False
                ),
            )
        else:  # vcs
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

            if use_dependency_links:
                link += "#egg=" + package_name
                return "dependency_links", link
            else:
                link = "{package_name} @ {link}".format(
                    package_name=package_name, link=link
                )
                return "install_requires", link


def get_default_packages(
    lockfile_path,
):  # type: (Path) -> Tuple[Dict[str, LockConfig], Dict[str, LockConfig]]
    """
    return local packages and remote packages in default packages (not dev)
    """
    local_packages = {}  # type: Dict[str, LockConfig]
    remote_packages = {}  # type: Dict[str, LockConfig]
    for package_name, config in (
        Lockfile.create(lockfile_path.parent).get_deps().items()
    ):
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages


def get_dev_packages(
    lockfile_path,
):  # type: (Path) -> Tuple[Dict[str, LockConfig], Dict[str, LockConfig]]
    """
    return ONLY development packages.

    :return: a tuple of local packages and dev packages
    """
    local_packages = {}  # type: Dict[str, LockConfig]
    remote_packages = {}  # type: Dict[str, LockConfig]
    for package_name, config in (
        Lockfile.create(str(lockfile_path.parent)).get_deps(dev=True).items()
    ):
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages
