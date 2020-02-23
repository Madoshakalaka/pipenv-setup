from typing import Any
from vistir.compat import Path
import pytest

from pipenv_setup import msg_formatter
from pipenv_setup.main import cmd
from tests.conftest import assert_kw_args_eq, data


@pytest.mark.parametrize(
    ("source_pipfile_dirname", "update_count"),
    [("nasty_0", 23), ("no_original_kws_0", 23)],
)
def test_update(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname, update_count
):  # type: (Any, Path, Path, str, int) -> None
    """
    test updating setup.py (when it already exists)
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    expected_setup_text = (pipfile_dir/'setup_lockfile_synced.py').read_text()
    with data(str(pipfile_dir), tmp_path):
        cmd(argv=["", "sync"])
        generated_setup = Path("setup.py")
        assert generated_setup.exists()
        generated_setup_text = generated_setup.read_text()
    for kw_arg_names in ("install_requires", "dependency_links"):

        assert_kw_args_eq(
            generated_setup_text,
            expected_setup_text,
            kw_arg_names,
            ordering_matters=False,
        )
    captured = capsys.readouterr()
    assert msg_formatter.update_success(update_count) in captured.out


@pytest.mark.parametrize(
    ("source_pipfile_dirname", "update_count"),
    [("nasty_0", 23), ("no_original_kws_0", 23)],
)
def test_only_setup_missing(
        capsys, tmp_path, shared_datadir, source_pipfile_dirname, update_count
):  # type: (Any, Path, Path, str, int) -> None
    """
    test setup.py generation (when it is missing)
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    expected_setup_text = (pipfile_dir / "setup_lockfile_synced.py").read_text()
    with data(source_pipfile_dirname, tmp_path, mode="pipfiles"):
        # delete the setup.py file that was copied to the tmp_path
        cmd(argv=["", "sync"])
        generated_setup = Path("setup.py")
        assert generated_setup.exists()
        generated_setup_text = generated_setup.read_text()

    for kw_arg_names in ("install_requires", "dependency_links"):
        assert_kw_args_eq(
            generated_setup_text,
            expected_setup_text,
            kw_arg_names,
            ordering_matters=False,
        )
    captured = capsys.readouterr()
    assert msg_formatter.generate_success(update_count) in captured.out, captured.out