from pipenv_setup import lockfile_parser
from tests.conftest import data


def test_get_dev_dependencies(shared_datadir, tmp_path):
    with data("generic_nice_0", tmp_path) as cwd:
        local, remote = lockfile_parser.get_dev_packages(cwd / "Pipfile.lock")
        assert "generic-package" in local
        assert "gitdir" in remote
