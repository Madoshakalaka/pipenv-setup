# noinspection PyProtectedMember
import pytest

from pipenv_setup.inconsistency_checker import _VersionReqs


@pytest.mark.parametrize(
    ("setup_version", "pipfile_version", "expected"),
    [
        ["==1.0.2", "==1.0.2", True],
        [">=1.0.2", "==1.0.2", False],
        ["==1.0.2", ">=1.0.2", True],
        [">1.0", ">=1.0.2", False],
        [">1.0", ">0.9.2", True],
        [">1.0", "~=0.9.2", False],
        [">1.0", "~=1.9.2", False],
        ["==1.0", "~=1.9.2", False],
        ["==2.0", "~=1.9.2", False],
        ["==1.9", "~=1.8.2", False],
        ["==1.9.4", "~=1.8.2", False],
        ["==1.8.5", "~=1.8.2", True],
        ["==1.8", "~=1.8.2", False],
        ["==1.0", "~=1.9.2", False],
        ["==1.2", "~=1.0.2", False],
        ["==1.2", "~=1.0", True],
        ["==1.2", "*", True],
        [">=1.2, !=1.3, <2.0", "*", True],
        [">=1.2, !=1.3, <2.0", "~=1.1", True],
        [">=1.2, !=1.3, <2.0", "~=1.3", False],
        [">=1.2, !=1.3, <2.0", "~=1.3, != 1.9", False],
        [">=1.2, <2", "~=1.2", True],
        [">=1.2, <1.5", "~=1.2", True],
        ["", "~=1.2", False],
        ["", "*", True],
    ],
)
def test_check_compatibility(setup_version: str, pipfile_version: str, expected: bool):
    vr = _VersionReqs(setup_version)
    assert vr.check_compatibility(pipfile_version) == expected
