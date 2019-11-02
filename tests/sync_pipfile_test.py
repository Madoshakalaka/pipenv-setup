from vistir.compat import Path
from .conftest import data
from pipenv_setup.main import cmd


def test_sync_dev_no_original(tmp_path):
    """
    sync --dev should add extras_require: {"dev": [blah]} in the absence of a extras_require keyword
    """
    # todo: this test is too simple
    with data("self_0", tmp_path) as path:
        setup_file = path / "setup.py"  # type: Path
        cmd(["", "sync", "--dev", "--pipfile"])
        text = setup_file.read_text()
        assert '"pytest~=5.1"' in text
        assert '"requirementslib~=1.5"' in text
