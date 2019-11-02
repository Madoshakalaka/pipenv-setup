# noinspection PyProtectedMember
import pytest

from pipenv_setup.constants import VersionConflict as VC
from pipenv_setup.inconsistency_checker import _VersionReqs


@pytest.mark.parametrize(
    ("setup_version", "pipfile_version", "expected"),
    [
        ["==1.0.2", "==1.0.2", None],
        [">=1.0.2", "==1.0.2", VC.POTENTIAL],
        ["==1.0.2", ">=1.0.2", VC.COMPATIBLE],
        [">1.0", ">=1.0.2", VC.POTENTIAL],
        [">1.0", ">0.9.2", VC.COMPATIBLE],
        [">1.0", "~=0.9.2", VC.DISJOINT],
        [">1.0", "~=1.9.2", VC.POTENTIAL],
        ["==1.0", "~=1.9.2", VC.DISJOINT],
        ["==2.0", "~=1.9.2", VC.DISJOINT],
        ["==1.9", "~=1.8.2", VC.DISJOINT],
        ["==1.9.4", "~=1.8.2", VC.DISJOINT],
        ["==1.8.5", "~=1.8.2", VC.COMPATIBLE],
        ["==1.8", "~=1.8.2", VC.DISJOINT],
        ["==1.0", "~=1.9.2", VC.DISJOINT],
        ["==1.2", "~=1.0.2", VC.DISJOINT],
        ["==1.2", "~=1.0", VC.COMPATIBLE],
        ["==1.2", "*", VC.COMPATIBLE],
        [">=1.2, !=1.3, <2.0", "*", VC.COMPATIBLE],
        [">=1.2, !=1.3, <2.0", "~=1.1", VC.COMPATIBLE],
        [">=1.2, !=1.3, <2.0", "~=1.3", VC.POTENTIAL],
        [">=1.2, !=1.3, <2.0", "~=1.3, != 1.9", VC.POTENTIAL],
        [">=1.2, <2", "~=1.2", None],
        [">=1.2, <1.5", "~=1.2", VC.COMPATIBLE],
        ["", "~=1.2", VC.POTENTIAL],
        ["", "*", None],
    ],
)
def test_check_compatibility(
    setup_version, pipfile_version, expected
):  # type: (str, str, bool) -> None
    vr = _VersionReqs(setup_version)
    assert vr.analyze_compatibility(pipfile_version) == expected
