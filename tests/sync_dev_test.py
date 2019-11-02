from vistir.compat import Path
from .conftest import data
from pipenv_setup.main import cmd


def test_sync_dev_no_original(tmp_path):
    """
    sync --dev should add extras_require: {"dev": [blah]} in the absence of a extras_require keyword
    """
    with data("generic_nice_1", tmp_path) as path:
        setup_file = path / "setup.py"  # type: Path
        cmd(["", "sync", "--dev"])
        text = setup_file.read_text()
        assert "gitdir==1.1.3" in text


def test_sync_dev_original_other_extras(tmp_path):
    """
    sync --dev should update extras_require: {"dev": [blah]} in place when there is existing extras_require
    """
    # todo: better test
    with data("generic_nice_2", tmp_path) as path:
        setup_file = path / "setup.py"  # type: Path
        cmd(["", "sync", "--dev"])
        text = setup_file.read_text()
        print(text)
        assert "gitdir==1.1.3" in text
        assert "pytest" in text
