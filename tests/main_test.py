import contextlib
import os
import shutil
from os.path import dirname
from pathlib import Path
from typing import Optional

import pytest

from pipenv_setup import setup_parser, msg_formatter
from pipenv_setup.main import cmd

data_path = Path(dirname(__file__)) / "data"


@contextlib.contextmanager
def working_directory(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


def copy_pipfiles(src_dir: Path, target_dir: Path):
    for f in src_dir.glob("Pipfile*"):
        shutil.copy(str(f), str(target_dir))


def copy_files(src_dir: Path, target_dir: Path):
    for f in src_dir.glob("*"):
        shutil.copy(str(f), str(target_dir))


def copy_file(file: Path, target_dir: Path, new_name: Optional[str] = None):
    new_file = target_dir / file.name
    if new_name is not None:
        new_file = target_dir / new_name
    shutil.copy(str(file), str(new_file))


def compare_list_of_string_kw_arg(
    setup_text_a: str, setup_text_b: str, kw_name: str, ordering_matters: bool = True
) -> bool:
    """
    :return: whether these two setup files has the same keyword argument of type list of strings (element order can not be different)
    :raise ValueError TypeError: if failed to get a list of strings
    """
    args_a = setup_parser.get_kw_list_of_string_arg(setup_text_a, kw_name)
    args_b = setup_parser.get_kw_list_of_string_arg(setup_text_b, kw_name)
    if ordering_matters:
        return args_a == args_b
    else:
        return set(args_a) == set(args_b)


@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
def test_generation(tmp_path, shared_datadir, source_pipfile_dirname: str):
    """
    test boilerplate
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    copy_pipfiles(pipfile_dir, tmp_path)
    with working_directory(tmp_path):
        cmd(argv=[..., "sync"])
    generated_setup = tmp_path / "setup.py"
    assert generated_setup.exists()
    generated_setup_text = generated_setup.read_text()
    expected_setup_text = (pipfile_dir / "setup.py").read_text()
    for kw_arg_names in ("install_requires", "dependency_links"):

        assert compare_list_of_string_kw_arg(
            generated_setup_text,
            expected_setup_text,
            kw_arg_names,
            ordering_matters=False,
        )


@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
def test_update(tmp_path, shared_datadir, source_pipfile_dirname: str):
    """
    test updating setup.py (when it already exists)
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    copy_pipfiles(pipfile_dir, tmp_path)
    copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with working_directory(tmp_path):
        cmd(argv=[..., "sync"])
    generated_setup = tmp_path / "setup.py"
    assert generated_setup.exists()
    generated_setup_text = generated_setup.read_text()
    expected_setup_text = (pipfile_dir / "setup.py").read_text()
    for kw_arg_names in ("install_requires", "dependency_links"):

        assert compare_list_of_string_kw_arg(
            generated_setup_text,
            expected_setup_text,
            kw_arg_names,
            ordering_matters=False,
        )


@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
def test_sync_file_missing(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname: str
):
    """
    test updating setup.py (when it already exists)
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    copy_file(pipfile_dir / "Pipfile", tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with working_directory(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=[..., "sync"])
        assert e.value.code == 1
        captured = capsys.readouterr()

        assert msg_formatter.missing_pipfile(Path("Pipfile.lock")) in captured.out

        assert msg_formatter.no_sync_performed() in captured.out


def test_help_text(capsys):
    cmd(argv=[...])
    captured = capsys.readouterr()
    assert "Commands:" in captured.out
    assert "sync" in captured.out
    assert "check" in captured.out
    assert captured.err == ""
