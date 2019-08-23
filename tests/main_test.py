import os
import sys
from os import path
from os.path import dirname
from pathlib import Path

from pipenv_setup.main import cmd

data_path = Path(dirname(__file__)) / "data"


def test_cmd():
    pass
