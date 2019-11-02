from typing import Dict, Any

import pytest

from pipenv_setup.constants import PipfileConfig
from pipenv_setup.inconsistency_checker import InconsistencyChecker
from pipenv_setup.inconsistency_checker import VersionConflict as VC


@pytest.mark.parametrize(
    ("install_requires", "pipfile_packages", "actual_conflicts"),
    [
        [["numpy"], {"numpy": "*"}, []],
        [["numpy> = 1.3"], {"numpy": "*"}, [("numpy", ">=1.3", "*", VC.COMPATIBLE)]],
        [
            ["numpy > = 1.3"],
            {"numpy": "!=1.3"},
            [("numpy", ">=1.3", "!=1.3", VC.POTENTIAL)],
        ],
        [
            ["numpy==1.3", "pandas"],
            {"numpy": "~=1.2"},
            [("numpy", "==1.3", "~=1.2", VC.COMPATIBLE)],
        ],
        [
            ["numpy==2.0.1"],
            {"numpy": "~=1.2"},
            [("numpy", "==2.0.1", "~=1.2", VC.DISJOINT)],
        ],
        [["numpy>=2.0, <3.0"], {"numpy": "~=2.0"}, []],
        [
            ["numpy==2.1.2"],
            {"numpy": "~=2.0.2"},
            [("numpy", "==2.1.2", "~=2.0.2", VC.DISJOINT)],
        ],
        [
            ["numpy>=2.0, <3.0; os_name='nt'", "python-opencv<2.0"],
            {"numpy": "~=2.0"},
            [],
        ],
        [
            ["numpy>=2.0, <3.0; os_name='nt'", "python-opencv<2.0"],
            {"numpy": ">=2.0, !=2.5, <3.0", "python-opencv": "==2.3"},
            [
                ("numpy", ">=2.0,<3.0", ">=2.0,!=2.5,<3.0", VC.POTENTIAL),
                ("python-opencv", "<2.0", "==2.3", VC.DISJOINT),
            ],
        ],
    ],
)
def test__check_install_requires_conflicts(
    install_requires, pipfile_packages, actual_conflicts
):  # type: (Any, Dict[str, PipfileConfig], Any) -> None
    # noinspection PyTypeChecker
    checker = InconsistencyChecker(install_requires, [], pipfile_packages, False)
    assert sorted(checker._check_install_requires_conflict()) == sorted(
        actual_conflicts
    )


@pytest.mark.parametrize(
    ("dependency_links", "pipfile_packages", "actual_conflicts"),
    [
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {"django": {"ref": "1.11.4", "editable": True}},
            ["package 'django' lacks 'git' key in pipfile"],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {
                "django": {
                    "git": "https://github.com/django/django.git",
                    "ref": "1.11.4",
                    "editable": True,
                }
            },
            [],
        ],
        [
            ["git+https://github.com/dgo/dgo.git@1.11.4#egg=django"],
            {
                "django": {
                    "git": "https://github.com/django/django.git",
                    "ref": "1.11.4",
                    "editable": True,
                }
            },
            [
                "package 'django' has url https://github.com/django/django.git in pipfile, "
                "which is different than https://github.com/dgo/dgo.git in dependency links"
            ],
        ],
        [
            ["git+https://github.com/django/django.git#egg=django"],
            {
                "django": {
                    "git": "https://github.com/django/django.git",
                    "ref": "1.11.4",
                    "editable": True,
                }
            },
            [
                "package 'django' has branch/version 1.11.4 in pipfile but it's not specified in dependency_links"
            ],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {
                "django": {
                    "git": "https://github.com/django/django.git",
                    "editable": True,
                }
            },
            [
                "package 'django' has branch/version 1.11.4 in dependency_links but not in pipfile"
            ],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {
                "django": {
                    "git": "https://github.com/django/django.git",
                    "ref": "1.11.5",
                    "editable": True,
                }
            },
            [
                "package 'django' has branch/version 1.11.4 in dependency_links, which is different "
                "than 1.11.5 listed in pipfile"
            ],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {"django": "==1.11.4"},
            [
                "git package 'django' specified in dependency_links is not a vcs package in pipfile"
            ],
        ],
    ],
)
def test_check_dependency_links(
    dependency_links, pipfile_packages, actual_conflicts
):  # type: (Any, Dict[str, PipfileConfig], Any) -> None

    # noinspection PyTypeChecker
    checker = InconsistencyChecker([], dependency_links, pipfile_packages, False)
    assert checker.check_dependency_links_conflict() == actual_conflicts


@pytest.mark.parametrize(
    ("install_requires", "pipfile_packages", "actual_conflicts"),
    [
        [
            ["colorama"],
            {"django": "*", "colorama": "*", "black": "==19.2b0"},
            [
                "package 'django' in pipfile but not in install_requires",
                "package 'black' in pipfile but not in install_requires",
            ],
        ],
        [
            ["colorama==1.0.1"],
            {"django": "*", "colorama": "*", "black": "==19.2b0"},
            [
                "package 'django' in pipfile but not in install_requires",
                "package 'black' in pipfile but not in install_requires",
            ],
        ],
        [
            ["colorama==1.0.1"],
            {
                "django": {
                    "git": "https://github.com/django/django.git",
                    "ref": "1.11.5",
                    "editable": True,
                },
                "colorama": "*",
                "black": "==19.2b0",
            },
            ["package 'black' in pipfile but not in install_requires"],
        ],
        [
            ["black==1.0.1"],
            {
                "some-local-package": {
                    "path": "/home/weeb27/phubscraper",
                    "editable": True,
                },
                "colorama": "*",
                "black": "==19.2b0",
            },
            ["package 'colorama' in pipfile but not in install_requires"],
        ],
        [
            ["black==1.0.1", "colorama"],
            {
                "some-local-package": {
                    "path": "/home/weeb27/phubscraper",
                    "editable": True,
                },
                "colorama": "*",
                "black": "==19.2b0",
            },
            [],
        ],
    ],
)
def test_check_lacking_install_requires(
    install_requires, pipfile_packages, actual_conflicts
):  # type: (Any, Dict[str, PipfileConfig], Any) -> None
    # noinspection PyTypeChecker
    checker = InconsistencyChecker(install_requires, [], pipfile_packages, False)
    assert sorted(checker.check_lacking_install_requires()) == sorted(actual_conflicts)


@pytest.mark.parametrize(
    ("dependency_links", "pipfile_packages", "actual_conflicts"),
    [
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {
                "some-git-package": {
                    "git": "https://github.com/some-git-package/some-git-package.git",
                    "ref": "1.11.4",
                    "editable": True,
                }
            },
            ["vcs package 'some-git-package' in pipfile but not in dependency_links"],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {
                "e682b37": {
                    "file": "https://github.com/divio/django-cms/archive/release/3.4.x.zip"
                }
            },
            ["package 'e682b37' has a url in pipfile but not in dependency_links"],
        ],
    ],
)
def test_check_lacking_dependency_links(
    dependency_links, pipfile_packages, actual_conflicts
):  # type: (Any, Dict[str, PipfileConfig], Any) -> None

    # noinspection PyTypeChecker
    checker = InconsistencyChecker([], dependency_links, pipfile_packages, False)
    assert checker.check_lacking_dependency_links() == actual_conflicts
