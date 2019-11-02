from pipenv_setup import lockfile_parser


def test_get_dev_dependencies(shared_datadir):
    local, remote = lockfile_parser.get_dev_packages(
        shared_datadir / "generic_nice_0" / "Pipfile.lock"
    )
    assert "generic-package" in local
    assert "gitdir" in remote
