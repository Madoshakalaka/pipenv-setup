from typing import Tuple, Dict

from pipenv_setup.constants import LockConfig


def is_remote_package(config: LockConfig) -> bool:
    """
    This function is written according to the following file
    https://github.com/pypa/pipfile/blob/master/examples/Pipfile.lock
    """
    # fixme: stronger checks?
    if "path" in config:  # local package
        return False
    return True


def format_remote_package(package_name: str, config: LockConfig) -> Tuple[str, str]:
    """
    format and return a string that can be put into the square brackets

    :return: Tuple[keyword_target, list_argument]
    :raise ValueError: if a package config is not understood
    """
    # fixme: stronger checks?
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#dependencies-that-aren-t-in-pypi
    if "file" in config:  # remote built distribution '.zip' file for example
        return "dependency_links", config["file"]
    if "version" in config:  # pypi package
        dependency_string = package_name + config["version"]
        if "markers" in config:
            dependency_string += "; " + config["markers"]
        return "install_requires", dependency_string
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
            raise ValueError("Can not understand config of package %s" % package_name)

        link = "{vcs}+{link}".format(vcs=vcs, link=config[vcs])
        if "ref" in config:
            link += "@" + config["ref"]
        link += "#egg=" + package_name
        return "dependency_links", link


def get_default_packages(
    lock_data: dict
) -> Tuple[Dict[str, LockConfig], Dict[str, LockConfig]]:
    """
    return local packages and remote packages in default packages (not dev)
    """
    local_packages: Dict[str, LockConfig] = {}
    remote_packages: Dict[str, LockConfig] = {}
    for package_name, config in lock_data["default"].items():
        if is_remote_package(config):
            remote_packages[package_name] = config
        else:
            local_packages[package_name] = config
    return local_packages, remote_packages
