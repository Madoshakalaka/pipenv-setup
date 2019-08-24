"""
it's possible that `entry_points` in setup.py fail to create a command line entry
e.g. on windows when <python_dir>/Scripts is not in system path

this file gives an alternative of using `python -m pipenv-setup`
"""
from pipenv_setup.main import cmd

if __name__ == "__main__":
    cmd()
