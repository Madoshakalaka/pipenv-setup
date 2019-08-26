from pathlib import Path


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
