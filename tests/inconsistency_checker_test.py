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
def test__check_install_requires_conflicts(
    install_requires, pipfile_packages: Dict[str, PipfileConfig], actual_conflicts
):
    # noinspection PyTypeChecker
    checker = InconsistencyChecker(install_requires, [], pipfile_packages)
    assert checker._check_install_requires_conflict() == actual_conflicts


@pytest.mark.parametrize(
    ("dependency_links", "pipfile_packages", "actual_conflicts"),
    [
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {"django": {"ref": "1.11.4", "editable": True}},
            ["pipfile lacks 'git' key for package django"],
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
                "pipfile url https://github.com/django/django.git is "
                "different than https://github.com/dgo/dgo.git in dependency links for package django"
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
                "branch/version 1.11.4 listed in pipfile but not specified in dependency_links for package django"
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
                "branch/version 1.11.4 listed in dependency_links but not in pipfile for package django"
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
                "branch/version 1.11.4 listed in dependency_links is different "
                "than 1.11.5 listed in pipfile for package django"
            ],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {"django": "==1.11.4"},
            [
                "git package django specified in dependency_links is not a vcs package in pipfile"
            ],
        ],
    ],
)
def test_check_dependency_links(
    dependency_links, pipfile_packages: Dict[str, PipfileConfig], actual_conflicts
):

    # noinspection PyTypeChecker
    checker = InconsistencyChecker([], dependency_links, pipfile_packages)
    assert checker.check_dependency_links_conflict() == actual_conflicts


@pytest.mark.parametrize(
    ("install_requires", "pipfile_packages", "actual_conflicts"),
    [
        [
            ["colorama"],
            {"django": "*", "colorama": "*", "black": "==19.2b0"},
            [
                "package django in pipfile but not in install_requires",
                "package black in pipfile but not in install_requires",
            ],
        ],
        [
            ["colorama==1.0.1"],
            {"django": "*", "colorama": "*", "black": "==19.2b0"},
            [
                "package django in pipfile but not in install_requires",
                "package black in pipfile but not in install_requires",
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
            ["package black in pipfile but not in install_requires"],
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
            ["package colorama in pipfile but not in install_requires"],
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
    install_requires, pipfile_packages: Dict[str, PipfileConfig], actual_conflicts
):
    # noinspection PyTypeChecker
    checker = InconsistencyChecker(install_requires, [], pipfile_packages)
    assert checker.check_lacking_install_requires() == actual_conflicts


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
            ["vcs package some-git-package in pipfile but not in dependency_links"],
        ],
        [
            ["git+https://github.com/django/django.git@1.11.4#egg=django"],
            {
                "e682b37": {
                    "file": "https://github.com/divio/django-cms/archive/release/3.4.x.zip"
                }
            },
            ["the link of package e682b37 is in pipfile but not in dependency_links"],
        ],
    ],
)
def test_check_lacking_dependency_links(
    dependency_links, pipfile_packages: Dict[str, PipfileConfig], actual_conflicts
):

    # noinspection PyTypeChecker
    checker = InconsistencyChecker([], dependency_links, pipfile_packages)
    assert checker.check_lacking_dependency_links() == actual_conflicts
