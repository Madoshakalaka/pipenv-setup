"""
check inconsistency between Pipfile and setup.py
"""
from typing import List, Dict, Tuple, Any, Iterable
import packaging.version
from packaging.version import Version

from pipenv_setup.constants import PipfileConfig


class _VersionReqs:
    def __init__(self, string):
        """
        :param string: setup.py install_requires style e.g. '==1.3.2' '>=1.3, <2'
        """
        self._string = string
        self._version_req_strings = self._parse_reqs(string)  # type: Iterable[str]

    @staticmethod
    def _parse_reqs(req_string: str) -> Iterable[str]:
        return map(str.strip, req_string.split(","))

    def check_compatibility(self, ver: str):
        """
        :param ver: pipfile style version string
        """
        pass


class InconsistencyChecker:
    def __init__(
        self,
        install_requires: List[str],
        dependency_links: List[str],
        pipfile_packages: Dict[str, PipfileConfig],
    ):
        """
        :param pipfile_packages: default packages
        """

        self._install_requires = install_requires
        self._install_requires_version_reqs = self._parse_install_requires(
            install_requires
        )
        self._dependency_links = dependency_links
        self._pipfile_packages = pipfile_packages

    @staticmethod
    def _separate_name_version(package_string: str) -> Tuple[str, str]:
        """
        :param package_string: setup.py install_requires style string
        >>> InconsistencyChecker._separate_name_version('numpy==1.2.3')
        ('numpy', '==1.2.3')
        >>> InconsistencyChecker._separate_name_version('numpy==1.2.3, >1.2,<2')
        ('numpy', '==1.2.3, >1.2,<2')
        >>> InconsistencyChecker._separate_name_version("numpy==1.2.3, >1.2,<2 ; os_name='nt'")
        ('numpy', '==1.2.3, >1.2,<2')
        """
        name = ""
        version_reqs_string = ""

        met_comp_ops = False

        for c in package_string:
            if c in ("=", "<", ">", "!"):
                met_comp_ops = True
            elif c == ";":  # met other markers, which we ignore
                break

            if met_comp_ops:
                version_reqs_string += c
            else:
                name += c
        return name.strip(), version_reqs_string.strip()

    def _parse_install_requires(
        self, install_requires: List[str]
    ) -> Dict[str, _VersionReqs]:
        res = {}  # type: Dict[str, _VersionReqs]
        for package_string in install_requires:
            name, version_req_string = self._separate_name_version(package_string)
            res[name] = _VersionReqs(version_req_string)
        return res

    def check_install_requires_conflict(self):
        for string in self._install_requires:
            name = ""
            version_requirements: List[str] = []
