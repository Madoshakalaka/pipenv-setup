"""
All kinds of messages pipenv-setup prints to console
"""

from colorama import Fore
from vistir.compat import Path


def colorful_help():
    string = ""
    string += "Commands:\n"
    string += (
        "  "
        + Fore.GREEN
        + "sync"
        + Fore.RESET
        + "\t\tsync Pipfile.lock with setup.py\n"
    )
    string += (
        "  "
        + Fore.BLUE
        + "check"
        + Fore.RESET
        + "\t\tcheck whether Pipfile is consistent with setup.py.\n  \t\tNon-zero exit code"
        " if there is inconsistency\n  \t\t(package missing; version incompatible)\n"
    )
    return string


def missing_file(file):  # type: (Path) -> str
    return "file %s not found" % file.name


def setup_not_found():
    return "setup.py not found under current directory"


def no_sync_performed():
    return "can not perform sync"


def checked_no_problem():
    return "No version conflict or missing packages/dependencies found in setup.py!"


def generate_success(
    default_package_count, dev_package_count=0, pipfile=False
):  # type: (int, int, bool) -> str
    """
    :param default_package_count: The number of updated default packages
    :param dev_package_count: The number of updated dev packages
    :param bool lockfile: indicate that Pipfile was used to update setup.py
    """
    src = "Pipfile" if pipfile else "Pipfile.lock"
    string = (
        "setup.py was successfully generated"
        "\n%d default packages synced from %s to setup.py"
        % (default_package_count, src)
    )

    if dev_package_count != 0:
        string += "\n%d dev packages from %s synced to setup.py" % (
            default_package_count,
            src,
        )

    string += "\nPlease edit the required fields in the generated file"
    return string


def update_success(
    default_package_count, dev_package_count=0, pipfile=False
):  # type: (int, int, bool) -> str
    """
    :param default_package_count: The number of updated default packages
    :param dev_package_count: The number of updated dev packages
    :param bool lockfile: indicate that Pipfile was used to update setup.py
    """
    src = "Pipfile" if pipfile else "Pipfile.lock"
    string = (
        "setup.py was successfully updated"
        + "\n%d default packages from %s synced to setup.py"
        % (default_package_count, src)
    )

    if dev_package_count != 0:
        string += "\n%d dev packages from %s synced to setup.py" % (
            dev_package_count,
            src,
        )
    return string
