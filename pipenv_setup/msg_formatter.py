from pathlib import Path


def missing_pipfile(file: Path):
    return "%s not found under current directory" % file.name


def setup_not_found():
    return "setup.py not found under current directory"


def no_sync_performed():
    return "can not perform sync"
