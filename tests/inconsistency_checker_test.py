from typing import Dict

import pytest

from pipenv_setup.constants import PipfileConfig
from pipenv_setup.inconsistency_checker import InconsistencyChecker


@pytest.mark.parametrize(
    ("install_requires", "pipfile_packages", "actual_conflicts"),
    [
        [["numpy"], {"numpy": "*"}, []],
        [["numpy> = 1.3"], {"numpy": "*"}, []],
        [["numpy > = 1.3"], {"numpy": "!=1.3"}, [("numpy", ">=1.3", "!=1.3")]],
        [["numpy==1.3", "pandas"], {"numpy": "~=1.2"}, []],
        [["numpy==2.0.1"], {"numpy": "~=1.2"}, [("numpy", "==2.0.1", "~=1.2")]],
        [["numpy>=2.0, <3.0"], {"numpy": "~=2.0"}, []],
        [["numpy==2.1.2"], {"numpy": "~=2.0.2"}, [("numpy", "==2.1.2", "~=2.0.2")]],
        [
            ["numpy>=2.0, <3.0; os_name='nt'", "python-opencv<2.0"],
            {"numpy": "~=2.0"},
            [],
        ],
        [
            ["numpy>=2.0, <3.0; os_name='nt'", "python-opencv<2.0"],
            {"numpy": ">=2.0, !=2.5, <3.0", "python-opencv": "==2.3"},
            [
                ("numpy", ">=2.0,<3.0", ">=2.0,!=2.5,<3.0"),
                ("python-opencv", "<2.0", "==2.3"),
            ],
        ],
    ],
)
def test_check_install_requires_conflicts(
    install_requires, pipfile_packages: Dict[str, PipfileConfig], actual_conflicts
):
    # noinspection PyTypeChecker
    checker = InconsistencyChecker(install_requires, [], pipfile_packages)
    assert checker.check_install_requires_conflict() == actual_conflicts
