import contextlib
import os

# noinspection PyUnresolvedReferences
import shutil
# noinspection PyUnresolvedReferences
from distutils import dir_util
from typing import Generator

from vistir.compat import Path

from pipenv_setup import setup_parser

# todo: guarantee expected_setup_text are read correctly both here, and in other sync tests
# todo: tests for checks.
# todo: make sure check knows --process-dependency-links option

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
def data(data_name, temp_dir, mode="all"):  # type: (str, Path, str) -> Generator[Path, None, None]
    """
    copy files in tests/data/data_name/ to a temporary directory, change work directory to the temporary directory
    , and change back after everything is done

    :param data_name:
    :param temp_dir: should be tmp_dir fixture provided by pytest
    :param mode: "all" | "pipfiles"
    """
    data_dir = Path(__file__).parent / "data" / data_name
    if mode == 'all':
        dir_util.copy_tree(str(data_dir), str(temp_dir))
    elif mode == 'pipfiles':
        for f in data_dir.glob("Pipfile*"):
            shutil.copy(str(f), str(temp_dir))
    else:
        raise ValueError

    with cwd(temp_dir) as temp_path:
        yield temp_path


def assert_kw_args_eq(
    setup_text_a, setup_text_b, kw_name, ordering_matters=True
):  # type: (str, str, str, bool) -> None
    """
    :return: whether these two setup files has the same keyword argument of type list of strings (element order can not be different)
    :raise ValueError TypeError: if failed to get a list of strings
    """
    args_a = setup_parser.get_kw_list_of_string_arg(setup_text_a, kw_name)
    args_b = setup_parser.get_kw_list_of_string_arg(setup_text_b, kw_name)
    if ordering_matters:
        assert args_a == args_b
    else:
        assert set(args_a) == set(args_b)