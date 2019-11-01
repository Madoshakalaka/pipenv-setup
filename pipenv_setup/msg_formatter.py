"""
All kinds of messages pipenv-setup prints to console
"""

from pathlib import Path
from colorama import Fore


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


def missing_file(file: Path):
    return "file %s not found" % file.name


def setup_not_found():
    return "setup.py not found under current directory"


def no_sync_performed():
    return "can not perform sync"


def checked_no_problem():
    return "No version conflict or missing packages/dependencies found in setup.py!"


def update_success(package_count: int):
    """
    :param package_count: The number of updated packages
    """
    return (
        "setup.py successfully updated"
        + "\n%d packages from Pipfile.lock synced to setup.py" % package_count
    )
