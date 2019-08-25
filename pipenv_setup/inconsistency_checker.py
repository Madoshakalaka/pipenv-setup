"""
check inconsistency between Pipfile and setup.py
"""
from string import digits
from typing import List, Dict, Tuple, Iterable, Optional, Set

import packaging.version
from packaging.version import Version

from pipenv_setup import pipfile_parser
from pipenv_setup.constants import PipfileConfig
from pipenv_setup.constants import vcs_list


class _VersionReqs:
    def __init__(self, string):
        """
        :param string: setup.py install_requires style e.g. '==1.3.2' '>=1.3, <2'
        """
        self._string = string
        self._op_versions = self._parse_reqs(string)  # type: List[Tuple[str, Version]]

    @staticmethod
    def _parse_reqs(req_string: str) -> List[Tuple[str, Version]]:
        """
        :param req_string: accepts both setup.py style and pipfile style
        :raise ValueError: if the string can not be understood
        :return: note: possibly empty list when req_string is empty
        >>> _VersionReqs._parse_reqs('')
        []
        >>> parse = packaging.version.parse
        >>> assert _VersionReqs._parse_reqs('==1.3.2') == [('==', parse('1.3.2'))]
        >>> assert _VersionReqs._parse_reqs('==2020.4.10') == [('==', parse('2020.4.10'))]
        >>> assert _VersionReqs._parse_reqs('*') == []
        >>> assert _VersionReqs._parse_reqs('~=1.2') == [('>=', parse('1.2')), ('<', parse('2.0'))]
        >>> assert _VersionReqs._parse_reqs('~=1') == [('>=', parse('1'))]
        >>> assert _VersionReqs._parse_reqs('~=1.2.4') == [('>=', parse('1.2.4')), ('<', parse('1.3.0'))]
        >>> assert _VersionReqs._parse_reqs('>=1.3.2, <2') == [('>=', parse('1.3.2')), ('<', parse('2'))]
        >>> assert _VersionReqs._parse_reqs(' >=1.3.2, <2 ') == [('>=', parse('1.3.2')), ('<', parse('2'))]
        >>> assert _VersionReqs._parse_reqs(' > =1.3.2, <2 ') == [('>=', parse('1.3.2')), ('<', parse('2'))]
        """
        reqs = []  # type: List[Tuple[str, Version]]
        for req_ver_string in req_string.split(","):
            if req_ver_string == "":
                continue
            op_string = ""
            ver_string = ""
            met_digit = False
            for c in req_ver_string:
                if c in digits:
                    met_digit = True
                if met_digit:
                    ver_string += c
                else:
                    op_string += c
            op_string = op_string.replace(" ", "")
            ver_string = ver_string.replace(" ", "")
            if op_string != "*":
                if op_string == "~=":
                    parts = ver_string.split(".")
                    if len(parts) >= 2:
                        parts[-2] = str(int(parts[-2]) + 1)
                    parts[-1] = "0"
                    reqs.append((">=", packaging.version.parse(ver_string)))
                    if len(parts) > 1:
                        reqs.append(("<", packaging.version.parse(".".join(parts))))
                else:
                    reqs.append((op_string, packaging.version.parse(ver_string)))
        return reqs

    def check_compatibility(self, pipfile_reqs: str):
        """
        :param pipfile_reqs: pipfile style version string
        """
        pipfile_op_versions = self._parse_reqs(pipfile_reqs)
        mapping = self._get_version_metric_mapping(
            list(map(lambda x: x[1], self._op_versions + pipfile_op_versions))
        )
        setup_filtered = list(range(2 * len(mapping) + 1))
        for op, version in self._op_versions:
            setup_filtered = list(
                self._filter_metric_by_op(op, mapping[version], setup_filtered)
            )

        pipfile_filtered = list(range(2 * len(mapping) + 1))
        for op, version in pipfile_op_versions:
            pipfile_filtered = list(
                self._filter_metric_by_op(op, mapping[version], pipfile_filtered)
            )

        return set(setup_filtered) <= set(pipfile_filtered)

    @staticmethod
    def _filter_metric_by_op(
        op: str, metric: int, space: Iterable[int]
    ) -> Iterable[int]:
        """
        filter int in space that 'op's metric
        :raise ValueError: for unrecognizable op

        >>> list(_VersionReqs._filter_metric_by_op('==', 1, range(3)))
        [1]
        >>> list(_VersionReqs._filter_metric_by_op('<=', 1, range(3)))
        [0, 1]
        >>> list(_VersionReqs._filter_metric_by_op('<', 1, range(3)))
        [0]
        >>> list(_VersionReqs._filter_metric_by_op('>', 1, range(3)))
        [2]
        >>> list(_VersionReqs._filter_metric_by_op('>', 1, [0,1,2,3,4]))
        [2, 3, 4]
        >>> list(_VersionReqs._filter_metric_by_op('>=', 1, range(3)))
        [1, 2]
        >>> list(_VersionReqs._filter_metric_by_op('!=', 1, range(3)))
        [0, 2]
        """
        if op == "==":
            return filter(metric.__eq__, list(space))
        elif op == ">=":
            return filter(metric.__le__, list(space))
        elif op == ">":
            return filter(metric.__lt__, list(space))
        elif op == "<":
            return filter(metric.__gt__, list(space))
        elif op == "<=":
            return filter(metric.__ge__, list(space))
        elif op == "!=":
            return filter(metric.__ne__, list(space))
        else:
            raise ValueError("not recognizable version string operator: " + op)

    @staticmethod
    def _get_version_metric_mapping(versions: List[Version]) -> Dict[Version, int]:
        """
        >>> parse = packaging.version.parse
        >>> v0 = parse('1.0')
        >>> v1 = parse('1.0')
        >>> v2 = parse('1.1')
        >>> v3 = parse('1.1.2')
        >>> v4 = parse('1.2')
        >>> v_list = [v1, v3, v0, v2, v4]
        >>> assert _VersionReqs._get_version_metric_mapping(v_list) == {v0: 1, v2:3, v3:5, v4: 7}
        """

        mapping = dict()  # type: Dict[Version, int]
        for i, v in enumerate([...] + sorted(list(set(versions)))):
            if i == 0:
                continue
            mapping[v] = 2 * i - 1
        return mapping

    def __str__(self):
        return self._string


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
        self._install_requires_package_names = (
            self._install_requires_version_reqs.keys()
        )
        self._dependency_links = dependency_links
        self._pipfile_packages = pipfile_packages

    # @staticmethod
    # def _parse_dependency_links(link) -> Tuple[str, str, str, str]:
    #     """
    #
    #     :param link:
    #     :return:
    #     """
    #     pass

    @staticmethod
    def _separate_name_version(package_string: str) -> Tuple[str, str]:
        """
        :param package_string: setup.py install_requires style string
        >>> InconsistencyChecker._separate_name_version('numpy==1.2.3')
        ('numpy', '==1.2.3')
        >>> InconsistencyChecker._separate_name_version('numpy==1.2.3, >1.2,<2')
        ('numpy', '==1.2.3,>1.2,<2')
        >>> InconsistencyChecker._separate_name_version("numpy==1.2.3, >1.2,<2 ; os_name='nt'")
        ('numpy', '==1.2.3,>1.2,<2')
        >>> InconsistencyChecker._separate_name_version("numpy")
        ('numpy', '')
        """
        name = ""
        version_reqs_string = ""

        met_comp_ops = False

        for c in package_string:
            if c in ("=", "<", ">", "!"):
                met_comp_ops = True
            elif c == ";":  # met other markers, which we ignore
                break
            if c != " ":
                if met_comp_ops:
                    version_reqs_string += c
                else:
                    name += c
        return name.replace(" ", ""), version_reqs_string.replace(" ", "")

    def _parse_install_requires(
        self, install_requires: List[str]
    ) -> Dict[str, _VersionReqs]:
        res = {}  # type: Dict[str, _VersionReqs]
        for package_string in install_requires:
            name, version_req_string = self._separate_name_version(package_string)
            res[name] = _VersionReqs(version_req_string)
        return res

    def check_install_requires_conflict(self) -> List[str]:
        """
        :raise ValueError: if some package in install_requires is not a pypi package in pipfile
        :return: string reports. Can be empty if there is no conflict
        """
        report = []
        for (
            name,
            setup_config,
            pipfile_config,
        ) in self._check_install_requires_conflict():
            report.append(
                "package %s has version string: %s in setup.py, which can violate %s in pipfile"
                % (name, setup_config, pipfile_config)
            )
        return report

    def _check_install_requires_conflict(self) -> List[Tuple[str, str, str]]:
        """
        :return: A list of conflicts in the form of (package_name, setup_config, pipfile_config), empty for no conflict
        """

        conflicts = []  # type: List[Tuple[str, str, str]]
        for name, vr in self._install_requires_version_reqs.items():
            if name in self._pipfile_packages:
                pipfile_config = self._pipfile_packages[name]
                if not pipfile_parser.is_pypi_package(pipfile_config):
                    raise ValueError(
                        "package %s in install_requires is not a pypi package in pipfile"
                        % name
                    )
                version_string = ""
                if isinstance(pipfile_config, str):
                    version_string = pipfile_config
                else:  # dict
                    if "version" in pipfile_config:
                        version_string = pipfile_config["version"]
                version_string = version_string.replace(" ", "")
                if not vr.check_compatibility(version_string):
                    conflicts.append((name, str(vr), version_string))

        return conflicts

    @staticmethod
    def _is_vcs_link(link: str):
        """
        :param link: setup.py dependency_link style string

        >>> InconsistencyChecker._is_vcs_link("git+https://github.com/django/django.git@1.11.4#egg=django")
        True
        >>> InconsistencyChecker._is_vcs_link("https://github.com/divio/django-cms/archive/release/3.4.x.zip")
        False
        >>> InconsistencyChecker._is_vcs_link("svn+https://svn.com/have/no/idea/how/svn/link/looks/like")
        True
        """
        return any([link.startswith(vcs) for vcs in vcs_list])

    @staticmethod
    def _parse_vcs_link(link: str) -> Tuple[str, str, Optional[str], str]:
        """
        :param link: a setup.py dependency_links style vcs link
        :return: vcs_name, url_stripped_of_ref_egg, ref(version/branch), package name
        :raise ValueError: if can not understand link

        >>> InconsistencyChecker._parse_vcs_link('git+https://github.com/requests/requests.git@v2.20.1#egg=requests')
        ('git', 'https://github.com/requests/requests.git', 'v2.20.1', 'requests')
        >>> InconsistencyChecker._parse_vcs_link('git+https://github.com/requests/requests.git#egg=requests')
        ('git', 'https://github.com/requests/requests.git', None, 'requests')
        """
        # todo: be less cringy (use some url parsing library?)
        # https://pipenv-fork.readthedocs.io/en/latest/basics.html#a-note-about-vcs-dependencies
        vcs = ""
        url = ""
        ref = ""  # type: Optional[str]
        name = ""

        plus_ind = -1
        for i, c in enumerate(link):
            if c == "+":
                plus_ind = i
                break
            else:
                vcs += c

        hash_ind = -1
        for i in range(len(link) - 1, -1, -1):
            c = link[i]
            if c == "#":
                hash_ind = i
                break
            else:
                name = c + name
        if not name.startswith("egg="):
            raise ValueError("Can not find egg= in link  %s" % link)
        else:
            name = name[4:]
        if plus_ind == -1:
            raise ValueError("link %s does not have <vcs_name>+" % link)

        at_ind = -1
        for i in range(hash_ind - 1, plus_ind - 1, -1):
            c = link[i]
            if c == "/":
                ref = None
                break
            elif c == "@":
                at_ind = i
                break
            else:
                ref = c + ref  # type: ignore

        if at_ind != -1:
            url = link[plus_ind + 1 : at_ind]
        else:
            url = link[plus_ind + 1 : hash_ind]

        if vcs == "" or url == "" or name == "":
            raise ValueError("Can not understand link %s" % link)

        return vcs, url, ref, name

    def check_dependency_links_conflict(self) -> List[str]:
        """
        :return A list of conflicts formatted as strings, can be empty when there's no conflict
        :raise ValueError: if check fails (e.g. can not parse dependency_links in setup.py)
        """
        msgs = []
        for link in self._dependency_links:
            if self._is_vcs_link(link):
                # raises value error
                vcs, url, ref, name = self._parse_vcs_link(link)
                if name in self._pipfile_packages:
                    config_in_pipfile = self._pipfile_packages[name]
                    if isinstance(config_in_pipfile, str):
                        msgs.append(
                            "%s package %s specified in dependency_links is not a vcs package in pipfile"
                            % (vcs, name)
                        )
                        continue
                    if vcs not in config_in_pipfile:
                        msgs.append(
                            "pipfile lacks '%s' key for package %s" % (vcs, name)
                        )
                    elif url != config_in_pipfile[vcs]:
                        msgs.append(
                            "pipfile url %s is different than %s in dependency links for package %s"
                            % (config_in_pipfile[vcs], url, name)
                        )
                    if ref is None and "ref" in config_in_pipfile:
                        msgs.append(
                            "branch/version %s listed in pipfile but not specified in dependency_links for package %s"
                            % (config_in_pipfile["ref"], name)
                        )
                    if ref is not None and "ref" not in config_in_pipfile:
                        msgs.append(
                            "branch/version %s listed in dependency_links but not in pipfile for package %s"
                            % (ref, name)
                        )
                    if (
                        ref is not None
                        and "ref" in config_in_pipfile
                        and config_in_pipfile["ref"] != ref
                    ):
                        msgs.append(
                            "branch/version %s listed in dependency_links is different "
                            "than %s listed in pipfile for package %s"
                            % (ref, config_in_pipfile["ref"], name)
                        )

        return msgs

    def check_lacking_install_requires(self) -> List[str]:
        """
        report pypi packages that are in pipfile default package but not in install_requires
        """
        reports = []
        for name, config in self._pipfile_packages.items():
            if pipfile_parser.is_pypi_package(config):
                if name not in self._install_requires_package_names:
                    reports.append(
                        "package %s in pipfile but not in install_requires" % name
                    )
        return reports

    def check_lacking_dependency_links(self) -> List[str]:
        """
        report vcs/url packages that are in pipfile default package but not in dependency_links

        :raise ValueError: if dependency_links can not be recognized
        """
        # parse dependency_links
        # name: vcs, url, ref
        vcs_dependency_names = set()  # type: Set[str]
        file_dependency_links = set()  # type: Set[str]

        # raises ValueError
        for link in self._dependency_links:
            if self._is_vcs_link(link):
                _, _, _, name = self._parse_vcs_link(link)
                vcs_dependency_names.add(name)
            else:
                file_dependency_links.add(link)
        reports = []
        for name, config in self._pipfile_packages.items():
            if pipfile_parser.is_remote_package(
                config
            ) and not pipfile_parser.is_pypi_package(config):
                if pipfile_parser.is_vcs_package(config):
                    if name not in vcs_dependency_names:
                        reports.append(
                            "vcs package %s in pipfile but not in dependency_links"
                            % name
                        )
                elif "file" in config:
                    assert isinstance(config, dict)
                    if config["file"] not in file_dependency_links:
                        reports.append(
                            "the link of package %s is in pipfile but not in dependency_links"
                            % name
                        )

        return reports
