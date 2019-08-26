import ast
import sys
import tokenize
from io import BytesIO
from pathlib import Path
from subprocess import Popen, PIPE
from sys import stderr
from tokenize import OP
from typing import Tuple, List

from pipenv_setup.setup_parser import get_setup_call_node, get_kw_list_node


def update_setup(dependency_arguments, filename: Path):
    """
    Clear install_requires and dependency_links argument and fill new ones. Format the code.

    :raise ValueError: when setup.py is not recognized (malformed)
    """
    with open(str(filename), "rb") as setup_file:
        setup_bytes = setup_file.read()
    setup_text = setup_bytes.decode(encoding="utf-8")
    root_node = ast.parse(setup_text)
    setup_lines = setup_text.splitlines()

    setup_call_node = get_setup_call_node(root_node)
    if setup_call_node is None:
        raise ValueError("No setup() call found in setup.py")
    setup_call_lineno, setup_call_col_offset = (
        setup_call_node.lineno,
        setup_call_node.col_offset,
    )

    install_requires_lineno = -1
    install_requires_col_offset = -1
    dependency_links_lineno = -1
    dependency_links_col_offset = -1

    for kw in ["install_requires", "dependency_links"]:

        setup_bytes, setup_lines = clear_kw_list(kw, setup_bytes, setup_lines)

    root_node = ast.parse("\n".join(setup_lines))

    node = get_kw_list_node(root_node, "install_requires")
    if node is not None:
        install_requires_lineno = node.lineno
        install_requires_col_offset = node.col_offset
    node = get_kw_list_node(root_node, "dependency_links")
    if node is not None:
        dependency_links_lineno = node.lineno
        dependency_links_col_offset = node.col_offset

    if install_requires_lineno != -1:
        insert_at_lineno_col_offset(
            setup_lines,
            install_requires_lineno,
            install_requires_col_offset + 1,
            str(dependency_arguments["install_requires"])[1:-1],
        )
    else:
        insert_at_lineno_col_offset(
            setup_lines,
            setup_call_lineno,
            setup_call_col_offset + len("setup("),
            "install_requires=" + str(dependency_arguments["install_requires"]) + ",",
        )

    if dependency_links_lineno != -1:
        insert_at_lineno_col_offset(
            setup_lines,
            dependency_links_lineno,
            dependency_links_col_offset + 1,
            str(dependency_arguments["dependency_links"])[1:-1],
        )
    else:
        insert_at_lineno_col_offset(
            setup_lines,
            setup_call_lineno,
            setup_call_col_offset + len("setup("),
            "dependency_links=" + str(dependency_arguments["dependency_links"]) + ",",
        )
    with open("setup.py", "w+") as file:
        file.write("\n".join(setup_lines))

    blacken("setup.py")


def blacken(filename: str):
    with Popen(
        [sys.executable, "-m", "black", filename], stdout=PIPE, stderr=PIPE
    ) as p:
        p.communicate()


def insert_at_lineno_col_offset(
    lines: List[str], lineno: int, col_offset: int, content: str
):
    the_line = lines[lineno - 1]
    lines[lineno - 1] = the_line[:col_offset] + content + the_line[col_offset:]


def clear_kw_list(kw: str, file_bytes: bytes, file_lines: List[str]):
    """
    clear a list without moving number of lines in a file

    :raise ValueError: if list lineno col_offset can not be located
    """
    root_node = ast.parse(file_bytes)
    # This raises ValueError
    list_node = get_kw_list_node(root_node, kw)
    if list_node is None:
        return file_bytes, file_lines

    lbrace_lineno = list_node.lineno
    lbrace_col_offset = list_node.col_offset

    # this raises ValueError
    rbrace_lineno, rbrace_col_offset = get_list_closing_bracket_lineno_offset(
        list_node, file_bytes
    )
    first_line = file_lines[lbrace_lineno - 1]
    if lbrace_lineno == rbrace_lineno:
        file_lines[lbrace_lineno - 1] = (
            first_line[: lbrace_col_offset + 1] + first_line[rbrace_col_offset:]
        )
    else:
        # first line
        file_lines[lbrace_lineno - 1] = first_line[: lbrace_col_offset + 1]
        # last line
        last_line = file_lines[rbrace_lineno - 1]
        file_lines[rbrace_lineno - 1] = last_line[rbrace_col_offset:]

    for between_lineno in range(lbrace_lineno + 1, rbrace_lineno):
        file_lines[between_lineno - 1] = ""

    return "\n".join(file_lines).encode("utf-8"), file_lines


def get_list_closing_bracket_lineno_offset(
    ast_list_node: ast.List, file_bytes: bytes
) -> Tuple[int, int]:
    """
    :raise ValueError: if fails to locate
    """

    tokens = tokenize.tokenize(BytesIO(file_bytes).readline)
    list_met = False
    count = 1
    for (token_type, token_val, (start_lineno, start_offset), _, _) in tokens:
        # print(token_type, token_val)
        if list_met and token_type == OP:
            if list_met:
                if token_val == "]":
                    count -= 1
                elif token_val == "[":
                    count += 1
                if count == 0:
                    return start_lineno, start_offset
        if (
            start_lineno == ast_list_node.lineno
            and start_offset == ast_list_node.col_offset
        ):
            list_met = True
    raise ValueError("can not locate closing bracket ast list node %s" % ast_list_node)
