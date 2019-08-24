import contextlib
import os
from os.path import dirname
from pathlib import Path

from pipenv_setup.main import cmd

data_path = Path(dirname(__file__)) / "data"


@contextlib.contextmanager
def working_directory(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


def test_cmd(tmp_path):
    with working_directory(data_path):
        cmd(argv=[..., "sync"])
