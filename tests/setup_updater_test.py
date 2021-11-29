from collections import defaultdict
from platform import python_version
from typing import Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pipenv_setup import setup_updater
from vistir.compat import Path

from .conftest import data


@pytest.fixture
def dummy_import(monkeypatch):  # (MonkeyPatch) -> Callable
    """
    This fixture monkeypatches the import mechanism to fail.

    After raising an `ImportError`, the monkeypatch is immediately removed.
    """

    def dummy_import(*args, **kwargs):
        try:
            raise ImportError("this is a monkeypatch")
        finally:
            monkeypatch.undo()

    return dummy_import


@pytest.fixture
def extra_dummy_import(monkeypatch):  # (MonkeyPatch) -> Callable
    """
    similar to the `dummy_import` fixture, except it causes two import failures
    """
    monkeypatch.n_import = 0

    def extra_dummy_import(*args, **kwargs):
        try:
            raise ImportError(
                "this is a monkeypatch for import #%d" % monkeypatch.n_import
            )
        finally:
            if monkeypatch.n_import:
                monkeypatch.undo()
            else:
                monkeypatch.n_import += 1

    return extra_dummy_import


def patch_import(monkeypatch, dummy_import):  # type: (MonkeyPatch, Callable) -> None
    """
    monkeypatch the builtin __import__ function with the given function
    """
    try:
        monkeypatch.setattr("builtins.__import__", dummy_import)
    except ImportError:  # raised by python2.7 (no `builtins` module)
        monkeypatch.setattr("__builtin__.__import__", dummy_import)


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


def test_monkeypatch_import(
    monkeypatch, dummy_import
):  # type: (MonkeyPatch, Callable) -> None
    """
    verify that the builtin __import__ function can be monkeypatched
    """
    with pytest.raises(ImportError):
        patch_import(monkeypatch, dummy_import)
        import black


@pytest.mark.xfail(
    float(python_version()[:3]) < 3.6, reason="black requires python >= 3.6"
)
def test_black():  # type: () -> None
    """
    test the nominal case when `black` is returned
    """
    import black

    is_black = setup_updater._get_formatting_module()

    assert is_black is black


@pytest.mark.xfail(
    float(python_version()[:3]) < 3.6, reason="black requires python >= 3.6"
)
def test_not_black(monkeypatch, dummy_import):  # type: (MonkeyPatch, Callable) -> None
    """
    verify `black` import failures provide an alternative formatter (or None)
    """
    import black

    patch_import(monkeypatch, dummy_import)
    is_not_black = setup_updater._get_formatting_module()

    assert is_not_black is not black


def test_autopep8(monkeypatch, dummy_import):  # type: (MonkeyPatch, Callable) -> None
    """
    verify `autopep8` is returned if `black` isn't present but `autopep8` is
    """
    import autopep8

    patch_import(monkeypatch, dummy_import)
    is_autopep8 = setup_updater._get_formatting_module()

    assert is_autopep8 is autopep8


def test_none(monkeypatch, extra_dummy_import):  # type: (MonkeyPatch, Callable) -> None
    """
    verify `None` is returned if neither `black` nor `autopep8` is present
    """
    patch_import(monkeypatch, extra_dummy_import)
    is_none = setup_updater._get_formatting_module()

    assert is_none is None


def test_format_file(
    monkeypatch, extra_dummy_import
):  # type: (MonkeyPatch, Callable) -> None
    """
    perform the same test as `test_none`, just with the parent function

    closes issue #34 (https://github.com/Madoshakalaka/pipenv-setup/issues/34)
    """
    patch_import(monkeypatch, extra_dummy_import)
    setup_updater.format_file(Path(__file__))
