from .conftest import data
from .main_test import compare_list_of_string_kw_arg
from pipenv_setup.main import cmd

import pytest
from pathlib import Path


@pytest.mark.parametrize(
    ("source_pipfile_dirname", "update_count"),
    [("nasty_0", 23), ("no_original_kws_0", 23)],
)
def test_sync_pipfile_no_original(
    capsys, tmp_path, source_pipfile_dirname, update_count
):
    """
    sync --pipfile should reference Pipfile (not Pipfile.lock) when printing results
    """
    with data(source_pipfile_dirname, tmp_path) as cwd:
        setup_file: Path = cwd / "setup.py"
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


def test_sync_underscore_or_dash(shared_datadir):
    """
    sync --pipfile should work for either dash or underscore names.

    No need to run any assertions; we are testing that no error is
    raised.

    Asserts fix for https://github.com/Madoshakalaka/pipenv-setup/issues/72.
    """
    with data("dash_or_underscore_0", shared_datadir / "dash_or_underscore_0"):
        cmd(["", "sync", "--pipfile"])
        cmd(["", "check"])
