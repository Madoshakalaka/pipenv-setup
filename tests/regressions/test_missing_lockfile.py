# https://github.com/Madoshakalaka/pipenv-setup/issues/18
from pipenv_setup.main import cmd
from tests.conftest import data


def test_sync_pipfile_but_lockfile_missing(tmp_path):
    """
    expected behavior:
    if the user uses `pipenv-setup sync --pipfile`, the absence of a lockfile should not fail the command
    """
    with data("missing_lockfile_0", tmp_path) as path:
        cmd(["", "sync", "--pipfile"])
