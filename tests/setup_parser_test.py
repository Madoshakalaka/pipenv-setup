import ast

import pytest

from pipenv_setup import setup_parser
from .conftest import data

A_TO_O = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
]


@pytest.mark.parametrize(
    ("setup_filename", "expected_returnee"),
    [
        ["setup_0.py", None],
        ["setup_1.py", None],
        ["setup_2.py", []],
        ["setup_3.py", []],
        ["setup_4.py", []],
        ["setup_5.py", ["a", "b", "c", "d", "e", "f", "g", "h"]],
        ["setup_6.py", A_TO_O],
        ["setup_7.py", A_TO_O],
        ["setup_8.py", A_TO_O],
    ],
)
def test_get_extras_dev_list_node(setup_filename, expected_returnee, tmp_path):
    with data("setup_files_extras_require", tmp_path):
        r = ast.parse((tmp_path / setup_filename).read_bytes())
        node = setup_parser.get_extras_require_dev_list_node(r)
        if node is None:
            assert expected_returnee is None
        else:
            assert ast.literal_eval(node) == expected_returnee
