import ast
import codecs
import sys
import tokenize
from io import BytesIO
from subprocess import Popen, PIPE
from tokenize import OP
from typing import Tuple, List, Any

from vistir.compat import Path

from pipenv_setup import setup_parser
from pipenv_setup.setup_parser import get_setup_call_node, get_kw_list_node


def update_setup(
    dependency_arguments, filename, dev=False
):  # type: (Any, Path, bool) -> None
    """
    Clear install_requires and dependency_links argument and fill new ones. Format the code.

    :param dependency_arguments:
    :param filename:
    :param dev: update extras_require or not
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
    extras_require_lineno = -1
    extras_require_col_offset = -1

    for kw in ["install_requires", "dependency_links"]:
        setup_bytes, setup_lines = clear_kw_list(kw, setup_bytes, setup_lines)
    if dev:
        setup_bytes, setup_lines = clear_dev_value(setup_bytes, setup_lines)

    root_node = ast.parse("\n".join(setup_lines))

    node = get_kw_list_node(root_node, "install_requires")
    if node is not None:
        install_requires_lineno = node.lineno
        install_requires_col_offset = node.col_offset
    node = get_kw_list_node(root_node, "dependency_links")
    if node is not None:
        dependency_links_lineno = node.lineno
        dependency_links_col_offset = node.col_offset
    extras_require_node = setup_parser.get_extras_require_dict_node(root_node)
    if extras_require_node is not None:
        extras_require_lineno = extras_require_node.lineno
        extras_require_col_offset = extras_require_node.col_offset

    # update keyword arguments
    if install_requires_lineno != -1:
        # if install_requires exists from the start
        insert_at_lineno_col_offset(
            setup_lines,
            install_requires_lineno,
            install_requires_col_offset + 1,
            str(dependency_arguments["install_requires"])[1:-1],
        )
    elif len(dependency_arguments["install_requires"]) > 0:
        # install_requires does not exist, create a new one
        insert_at_lineno_col_offset(
            setup_lines,
            setup_call_lineno,
            setup_call_col_offset + len("setup("),
            "install_requires=" + str(dependency_arguments["install_requires"]) + ",",
        )

    if dependency_links_lineno != -1:
        # if dependency_links exists from the start
        insert_at_lineno_col_offset(
            setup_lines,
            dependency_links_lineno,
            dependency_links_col_offset + 1,
            str(dependency_arguments["dependency_links"])[1:-1],
        )
    elif len(dependency_arguments["dependency_links"]) > 0:
        # dependency_links does not exist, create a new one
        insert_at_lineno_col_offset(
            setup_lines,
            setup_call_lineno,
            setup_call_col_offset + len("setup("),
            "dependency_links=" + str(dependency_arguments["dependency_links"]) + ",",
        )

    # update extras_require
    root_node = ast.parse("\n".join(setup_lines))
    if len(dependency_arguments["extras_require"]) > 0 and dev:
        if extras_require_lineno == -1:
            # extras_require does not exist from the start
            insert_at_lineno_col_offset(
                setup_lines,
                setup_call_lineno,
                setup_call_col_offset + len("setup("),
                'extras_require = {"dev": []},',
            )
            extras_require_lineno = setup_call_lineno
            extras_require_col_offset = setup_call_col_offset + len("setup(")
            root_node = ast.parse("\n".join(setup_lines))

        dev_list_node = setup_parser.get_extras_require_dev_list_node(root_node)
        if dev_list_node is None:
            insert_at_lineno_col_offset(
                setup_lines,
                extras_require_lineno,
                extras_require_col_offset + 1,
                '"dev": [],',
            )
            root_node = ast.parse("\n".join(setup_lines))
            dev_list_node = setup_parser.get_extras_require_dev_list_node(root_node)
        assert dev_list_node is not None
        insert_at_lineno_col_offset(
            setup_lines,
            dev_list_node.lineno,
            dev_list_node.col_offset + 1,
            str(dependency_arguments["extras_require"])[1:-1] + ",",
        )

    f = codecs.open("setup.py", encoding="utf-8", mode="w")
    f.write("\n".join(setup_lines))
    f.close()

    format_file(Path("setup.py"))


def format_file(file):  # type: (Path) -> None
    """
    use black or autopep8 to format python file
    """
    try:
        # noinspection PyPackageRequirements
        import black

        with Popen(
            [sys.executable, "-m", "black", str(file)], stdout=PIPE, stderr=PIPE
        ) as p:
            p.communicate()

    except ImportError:
        # use autopep8
        import autopep8

        code = autopep8.fix_code(file.read_text())
        file.write_text(code)


def insert_at_lineno_col_offset(
    lines, lineno, col_offset, content
):  # type: (List[str], int, int, str) -> None
    the_line = lines[lineno - 1]
    lines[lineno - 1] = the_line[:col_offset] + content + the_line[col_offset:]


def clear_dev_value(
    file_bytes, file_lines
):  # type: (bytes, List[str]) -> Tuple[bytes, List[str]]
    """
    clear dev list in extra_require without moving number of lines in a file

    :raise ValueError: if list lineno col_offset can not be located
    """
    root_node = ast.parse(file_bytes)
    # This raises ValueError
    list_node = setup_parser.get_extras_require_dev_list_node(root_node)  # type: ignore
    if list_node is None:
        # nothing needs to be done
        return file_bytes, file_lines

    return clear_list_content(list_node, file_bytes, file_lines)


def clear_list_content(
    list_node, file_bytes, file_lines
):  # type: (ast.List, bytes, List[str]) -> Tuple[bytes, List[str]]
    """
    clear list content in a file

    :raise ValueError: if list lineno col_offset can not be located
    """
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


def clear_kw_list(
    kw, file_bytes, file_lines
):  # type: (str, bytes, List[str]) -> Tuple[bytes, List[str]]
    """
    clear list content in a keyword argument without moving number of lines in a file

    :raise ValueError: if list lineno col_offset can not be located
    """
    root_node = ast.parse(file_bytes)
    # This raises ValueError
    list_node = get_kw_list_node(root_node, kw)
    if list_node is None:
        # need to do nothing
        return file_bytes, file_lines

    return clear_list_content(list_node, file_bytes, file_lines)


def get_list_closing_bracket_lineno_offset(
    ast_list_node, file_bytes
):  # type: (ast.List, bytes) -> Tuple[int, int]
    """
    :raise ValueError: if fails to locate
    """
    import platform

    if platform.python_version().startswith("2"):
        tokens = tokenize.generate_tokens(BytesIO(file_bytes).readline)  # type: ignore
    else:
        tokens = tokenize.tokenize(BytesIO(file_bytes).readline)

    list_met = False
    count = 1
    for (token_type, token_val, (start_lineno, start_offset), _, _) in tokens:
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
