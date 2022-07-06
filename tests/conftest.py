import contextlib
import os
import shutil

from typing import Generator, Callable, Optional
from pathlib import Path


@contextlib.contextmanager
def cwd(path):  # type: (Path) -> Generator[Path, None, None]
    """
    change to a path and then change back
    """
    prev_cwd = os.getcwd()
    os.chdir(str(path))
    yield path
    os.chdir(prev_cwd)


def strip_example_suffix(p: Path) -> Path:
    new_name = p.name[: -len(".example")]
    return p.with_name(new_name)


@contextlib.contextmanager
def data(
    data_name: str, temp_dir: Path, filter: Optional[Callable[[str], bool]] = None
) -> Generator[Path, None, None]:
    """
    copy files in tests/data/data_name/ to a temporary directory, change work directory to the temporary directory
    , and change back after everything is done

    :param filter: the filter receives the name of the file. If the filter returns true, then the file is copied.
    By default, everything is copied.
    :param data_name:
    :param temp_dir: should be tmp_dir fixture provided by pytest
    """
    data_dir = Path(__file__).parent / "data" / data_name

    # essentially doing a `rm -r` and then a `cp -r`
    # todo: for python versions >= 3.8 there is a `dirs_exist_ok` optional argument,
    #   we won't need shutil.rmtree() when we drop the support for python3.7
    shutil.rmtree(temp_dir)
    shutil.copytree(data_dir, temp_dir)
    for p in temp_dir.rglob("*"):
        if p.is_file() and p.name.endswith(".example"):
            target_path = strip_example_suffix(p)
            if filter is None or filter(target_path.name):
                shutil.move(p, target_path)

    with cwd(temp_dir) as temp_path:
        yield temp_path
