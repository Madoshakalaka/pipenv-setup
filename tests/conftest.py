import contextlib
import os

# noinspection PyUnresolvedReferences
from distutils import dir_util
from typing import Generator

from vistir.compat import Path


@contextlib.contextmanager
def cwd(path):  # type: (Path) -> Generator[Path, None, None]
    """
    change to a path and then change back
    """
    prev_cwd = os.getcwd()
    os.chdir(str(path))
    yield path
    os.chdir(prev_cwd)


@contextlib.contextmanager
def data(data_name, temp_dir):  # type: (str, Path) -> Generator[Path, None, None]
    """
    copy files in tests/data/data_name/ to a temporary directory, change work directory to the temporary directory
    , and change back after everything is done

    :param data_name:
    :param temp_dir: should be tmp_dir fixture provided by pytest
    """
    data_dir = Path(__file__).parent / "data" / data_name
    dir_util.copy_tree(str(data_dir), str(temp_dir))
    with cwd(temp_dir) as temp_path:
        yield temp_path
