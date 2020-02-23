# todo: refactor this file
import shutil
from os.path import dirname
from typing import Optional, List, Any

import pytest
from vistir.compat import Path

from pipenv_setup import msg_formatter, main
from pipenv_setup.main import cmd
from tests.conftest import cwd, data, assert_kw_args_eq

data_path = Path(dirname(__file__)) / "data"



def copy_file(
    file, target_dir, new_name=None
):  # type: (Path, Path, Optional[str]) -> None
    new_file = target_dir / file.name
    if new_name is not None:
        new_file = target_dir / new_name
    shutil.copy(str(file), str(new_file))



@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
@pytest.mark.parametrize(
    ("missing_filenames",),
    [
        [["Pipfile"]],
        [["Pipfile", "Pipfile.lock"]],
        [["Pipfile.lock", "setup.py"]],
        [["Pipfile", "setup.py"]],
    ],
)
def test_sync_file_missing_exit_code(
    capfd, tmp_path, shared_datadir, source_pipfile_dirname, missing_filenames
):  # type: (Any, Path, Path, str, List[str]) -> None
    """
    when Pipfile.lock is missing, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ["Pipfile", "Pipfile.lock", "setup.py"]:
        file = pipfile_dir / filename
        if filename not in missing_filenames:
            copy_file(file, tmp_path)

    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "sync"])
        assert e.value.code == 1


# fixme: capfd can not capture stderr on windows or ubuntu. How?? stderr is always empty for me
@pytest.mark.xfail
@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
def test_sync_lock_file_missing_messages(
    capfd, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    when pipfile is missing, there should be error msgs
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    copy_file(pipfile_dir / "Pipfile", tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with cwd(tmp_path):
        with pytest.raises(SystemExit):
            cmd(argv=["", "sync"])
    captured = capfd.readouterr()
    assert msg_formatter.no_sync_performed() in captured.err
    assert msg_formatter.missing_file(Path("Pipfile.lock")) in captured.err


def test_help_text(capsys):
    cmd(argv=[""])
    captured = capsys.readouterr()
    assert "Commands:" in captured.out
    assert "sync" in captured.out
    assert "check" in captured.out
    assert captured.err == ""


@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
@pytest.mark.parametrize(
    ("missing_filenames",),
    [
        [["Pipfile"]],
        [["Pipfile", "Pipfile.lock"]],
        [["Pipfile.lock", "setup.py"]],
        [["Pipfile", "setup.py"]],
        [["Pipfile", "setup.py", "Pipfile.Lock"]],
        [["setup.py"]],
    ],
)
def test_check_file_missing_exit_code(
    capfd, tmp_path, shared_datadir, source_pipfile_dirname, missing_filenames
):  # type: (Any, Path, Path, str, List[str]) -> None
    """
    when Pipfile.lock is missing, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ["Pipfile", "Pipfile.lock", "setup.py"]:
        file = pipfile_dir / filename
        if filename not in missing_filenames:
            copy_file(file, tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check"])
        assert e.value.code == 1


@pytest.mark.parametrize(("source_pipfile_dirname",), [("nasty_0",)])
def test_check_file_ignore_local(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    when Pipfile.lock is missing, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check"])
        assert e.value.code == 1

        cmd(argv=["", "check", "--ignore-local"])
        captured = capsys.readouterr()
        assert msg_formatter.checked_no_problem() in captured.out


@pytest.mark.parametrize(("source_pipfile_dirname",), [("loose_pass_strict_fail_0",)])
def test_check_file_strict(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    when --strict flag is passed. compatible but not identical versioning should fail
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)
    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check", "--strict"])
        assert e.value.code == 1

        cmd(argv=["", "check"])
        captured = capsys.readouterr()
        assert msg_formatter.checked_no_problem() in captured.out


@pytest.mark.parametrize(("source_pipfile_dirname",), [("many_conflicts_0",)])
def test_check_file_many_conflicts(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    many conflicts, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)

    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check"])
        assert e.value.code == 1


@pytest.mark.parametrize(("source_pipfile_dirname",), [("broken_0",), ("broken_1",)])
def test_check_file_broken_setup(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    when Pipfile.lock is missing, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check", "--ignore-local"])
        assert e.value.code == 1


@pytest.mark.parametrize(("source_pipfile_dirname",), [("install_requires_missing_0",)])
def test_check_file_install_requires_missing(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    when Pipfile.lock is missing, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check"])
        assert e.value.code == 1


@pytest.mark.parametrize(("source_pipfile_dirname",), [("lockfile_vcs_branch_0",)])
def test_check_lockfile_vcs_branch(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Any, Path, Path, str) -> None
    """
    When Pipfile specifies a VCS dependency with a `ref` that is a mutable reference
    (e.g. - a branch, not a tag or a commit hash), `setup.py` gets updated with the
    resolved `sha` of that branch from Pipfile.lock.

    This causes `check` to fail b/c setup.py doesn't match Pipfile.

    The `--lockfile` flag allows checking against `Pipefile.lock` instead, which
    fixes this check.
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)
    # copy_file(shared_datadir / "minimal_empty_setup.py", tmp_path, "setup.py")
    with cwd(tmp_path):
        # Check will fail b/c `master` branch resolves to commit sha in setup.py
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "check"])
        assert e.value.code == 1

        # `check --lockfile` will pass because Pipfile.lock also has the resolved sha
        cmd(argv=["", "check", "--lockfile"])


@pytest.mark.parametrize(("source_pipfile_dirname",), [("lock_package_broken_0",)])
def test_sync_lock_file_package_broken(
    tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Path, Path, str) -> None
    """
    when Pipfile.lock is missing, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)

    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "sync"])
        assert e.value.code == 1


@pytest.mark.parametrize(("source_pipfile_dirname",), [("broken_no_setup_call_0",)])
def test_sync_no_setup_call(
    tmp_path, shared_datadir, source_pipfile_dirname
):  # type: (Path, Path, str) -> None
    """
    when setup call is not found, return code should be one
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)
    with cwd(tmp_path):
        with pytest.raises(SystemExit) as e:
            cmd(argv=["", "sync"])
        assert e.value.code == 1


def test_wrong_use_of_congratulate():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        main.congratulate(123)  # type: ignore


def test_wrong_use_of_fatal_error():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        main.fatal_error(123)  # type: ignore
