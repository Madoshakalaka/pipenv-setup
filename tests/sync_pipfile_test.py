from .conftest import data
from .main_test import copy_file, compare_list_of_string_kw_arg
from pipenv_setup.main import cmd

import pytest
from vistir.compat import Path


@pytest.mark.parametrize(
    ("source_pipfile_dirname", "update_count"),
    [("nasty_0", 23), ("no_original_kws_0", 23)],
)
def test_sync_pipfile_no_original(
    capsys, tmp_path, shared_datadir, source_pipfile_dirname, update_count
):
    """
    sync --pipfile should reference Pipfile (not Pipfile.lock) when printing results
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)

    with data(str(pipfile_dir), tmp_path) as path:
        setup_file = path / "setup.py"  # type: Path
        cmd(["", "sync", "--pipfile"])
        text = setup_file.read_text()
        generated_setup = Path("setup.py")
        assert generated_setup.exists()
        generated_setup_text = generated_setup.read_text()
        expected_setup_text = Path("setup.py").read_text()

    for kw_arg_names in ("install_requires", "dependency_links"):
        assert compare_list_of_string_kw_arg(
            generated_setup_text,
            expected_setup_text,
            kw_arg_names,
            ordering_matters=False,
        )

    captured = capsys.readouterr()
    assert "Pipfile.lock" not in captured.out, captured.out
    assert "Pipfile" in captured.out, captured.out


def test_sync_dev_pipfile_no_original(tmp_path):
    """
    sync --dev --pipfile should add extras_require: {"dev": [blah]} in the absence of an
    extras_require keyword
    """
    # todo: this test is too simple
    with data("self_0", tmp_path) as path:
        setup_file = path / "setup.py"  # type: Path
        cmd(["", "sync", "--dev", "--pipfile"])
        text = setup_file.read_text()
        assert "pytest~=5.1" in text, text
        assert "requirementslib~=1.5" in text, text


def test_sync_underscore_or_dash(shared_datadir):  # type: pathlib.Path
    """
    sync --pipfile should work for either dash or underscore names.

    Asserts fix for https://github.com/Madoshakalaka/pipenv-setup/issues/72.
    """
    pipfile_dir = shared_datadir / source_pipfile_dirname
    for filename in ("Pipfile", "Pipfile.lock", "setup.py"):
        copy_file(pipfile_dir / filename, tmp_path)

    with data(str(pipfile_dir), tmp_path):
        cmd(["", "sync", "--pipfile"])
        cmd(["", "check"])

    captured = capsys.readouterr()
    assert "in pipfile but not in install_requires" not in captured.out
