import ast
from typing import List, Optional, Tuple


def get_kw_list_of_string_arg(setup_text, kw_name):  # type: (str, str) -> List[str]
    """
    :raise TypeError ValueError: when failed to get a list of strings
    """
    root_node = ast.parse(setup_text)
    kw_list_node = get_kw_list_node(root_node, kw_name)
    if kw_list_node is None:
        raise ValueError("keyword argument %s not found" % kw_name)
    return parse_list_of_string(kw_list_node)


def parse_list_of_string(node):  # type: (ast.List) -> List[str]
    """
    raise: TypeError: when node is not a `ast.List`
    raise: ValueError: when node has non-string element
    """

    if not isinstance(node, ast.List):
        raise TypeError("Node is not a ast.List node")

    res = []
    for element_node in ast.walk(node):
        if (
            element_node is not node
            and not isinstance(element_node, ast.Str)
            and not isinstance(element_node, ast.Load)  # matt: what is this????
        ):
            raise ValueError("List has non_string node: %s" % element_node)
        elif isinstance(element_node, ast.Str):
            res.append(element_node.s)
    return res


def get_install_requires_dependency_links(
    setup_code,
):  # type: (str) -> Tuple[List[str], List[str]]
    """
    :raise ValueError SyntaxError: if can not get 'install_requires' or 'dependency_links' keyword list in the file

    :param setup_code: path for setup file
    """
    # raises syntax error
    root_node = ast.parse(setup_code)
    install_requires_node = get_kw_list_node(root_node, "install_requires")
    if install_requires_node is None:
        raise ValueError("keyword install_requires is not found")

    dependency_links_node = get_kw_list_node(root_node, "dependency_links")
    if dependency_links_node is None:
        raise ValueError("keyword dependency_links is not found")

    return (
        parse_list_of_string(install_requires_node),
        parse_list_of_string(dependency_links_node),
    )


def get_setup_call_node(root_node):  # type: (ast.AST)-> Optional[ast.Call]

    for node in ast.walk(root_node):

        if (
            hasattr(node, "func")
            and hasattr(node.func, "id")  # type: ignore
            and node.func.id == "setup"  # type: ignore
        ):
            return node  # type: ignore
    return None


def get_extras_require_dev_list_node(
    root_node,
):  # type: (ast.AST) -> Optional[ast.List]
    """
    get the list from [dev]

    :raise ValueError: When the extras_require exist but is not a dictionary
    :return: a list node, or None if it does not exist
    """
    node = get_extras_require_dict_node(root_node)
    if node is not None:
        dev_index = -1

        current = -1
        children = list(ast.iter_child_nodes(node))
        for child in children:
            current += 1
            if isinstance(child, ast.Str):
                if child.s == "dev":
                    dev_index = current
            else:
                break

        if dev_index == -1:
            return None
        else:
            return children[current + dev_index]  # type: ignore

    return None


def get_extras_require_dict_node(root_node):  # type: (ast.AST) ->Optional[ast.Dict]
    """
    :raise ValueError: When the keyword argument is not a list or when can not get the list
    :return: a dict node, or None if it does not exist
    """
    setup_call_node = get_setup_call_node(root_node)
    if setup_call_node is None:
        raise ValueError("Can not find keyword argument extra_require")
    node = None
    for keyword in setup_call_node.keywords:
        if keyword.arg == "extras_require":
            node = keyword.value
            if not isinstance(node, ast.Dict):
                raise ValueError(
                    "Error parsing setup.py: extra_require keyword argument is not a dictionary"
                )
    return node  # type: ignore


def get_kw_list_node(root_node, kw):  # type(ast.AST, str) -> Optional[ast.List]
    """
    :raise ValueError: When the keyword argument is not a list or when can not get the list
    :return: a list node, or None if it does not exist
    """
    setup_call_node = get_setup_call_node(root_node)
    if setup_call_node is None:
        raise ValueError("Can not find keyword argument %s" % kw)
    for keyword in setup_call_node.keywords:
        if keyword.arg == kw:
            node = keyword.value
            if not isinstance(node, ast.List):
                raise ValueError("Error parsing setup.py: %s is not a list" % kw)
            return node
    return None
