from pipenv_setup import pipfile_parser


def test_use_dependency_links_vcs_disabled(shared_datadir):
    destination_kw, value = pipfile_parser.format_remote_package(
        "django",
        {"git": "https://github.com/django/django.git"},
    )
    assert destination_kw == "install_requires"
    assert value == "django @ git+https://github.com/django/django.git"


def test_use_dependency_links_vcs_enabled(shared_datadir):
    destination_kw, value = pipfile_parser.format_remote_package(
        "django",
        {"git": "https://github.com/django/django.git"},
        use_dependency_links=True,
    )
    assert destination_kw == "dependency_links"
    assert value == "git+https://github.com/django/django.git#egg=django"


def test_use_dependency_links_file_disabled(shared_datadir):
    destination_kw, value = pipfile_parser.format_remote_package(
        "e682b37",
        {"file": "https://github.com/divio/django-cms/archive/release/3.4.x.zip"},
    )
    assert destination_kw == "install_requires"
    assert value == "https://github.com/divio/django-cms/archive/release/3.4.x.zip"


def test_use_dependency_links_file_enabled(shared_datadir):
    destination_kw, value = pipfile_parser.format_remote_package(
        "e682b37",
        {"file": "https://github.com/divio/django-cms/archive/release/3.4.x.zip"},
        use_dependency_links=True,
    )
    assert destination_kw == "dependency_links"
    assert value == "https://github.com/divio/django-cms/archive/release/3.4.x.zip"
