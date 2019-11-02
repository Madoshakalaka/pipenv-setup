from collections import defaultdict
from vistir.compat import Path
from .conftest import data
from pipenv_setup import setup_updater


def test_no_unnecessary_dependency_link(tmp_path):
    """
    when there's no vcs distributed files in Pipfile, dependency_links keyword argument shouldn't be created
    """
    with data("generic_nice_0", tmp_path) as path:
        setup_file = path / "setup.py"  # type: Path
        text = setup_file.read_text()
        setup_file.write_text(text.replace("dependency_links=[],", ""))

        setup_updater.update_setup(defaultdict(list), path / "setup.py")

        assert "dependency_links=[]," not in setup_file.read_text()
