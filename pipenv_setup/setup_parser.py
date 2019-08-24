from os.path import dirname
from pathlib import Path
from typing import List, Optional, Union, Tuple
import ast


def _parse_list_of_string(node: ast.List) -> List[str]:
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
    setup_code: str
) -> Tuple[List[str], List[str]]:
    """
    :raise ValueError: if can not get 'install_requires' or 'dependency_links' keyword list in the file

    :param setup_code: path for setup file
    """
    root_node = ast.parse(setup_code)

    install_requires_node = get_kw_list_node(root_node, "install_requires")
    if install_requires_node is None:
        raise ValueError("keyword install_requires is not found")

    dependency_links_node = get_kw_list_node(root_node, "dependency_links")
    if dependency_links_node is None:
        raise ValueError("keyword dependency_links is not found")

    return (
        _parse_list_of_string(install_requires_node),
        _parse_list_of_string(dependency_links_node),
    )


def get_setup_call_node(root_node) -> Optional[ast.Call]:

    for node in ast.walk(root_node):

        if (
            hasattr(node, "func")
            and hasattr(node.func, "id")  # type: ignore
            and node.func.id == "setup"  # type: ignore
        ):
            return node  # type: ignore
    return None


def get_kw_list_node(root_node, kw: str) -> Optional[ast.List]:
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
