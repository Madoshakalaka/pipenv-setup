# Sync Pipfile with setup.py dependencies
# Assumptions:
# - You are running in a directory with Pipfile, Pipfile.lock & setup.py
# - Your setup.py calls a function named setup()
# - setup() is called with keyword arguments of install_requires and dependency_links (can be empty lists)
# - All your remote dependencies are HTTPS git

import pipfile
import ast
import json
import astunparse
from yapf.yapflib import yapf_api
from typing import Union

pipfile_ = pipfile.load()

with open("Pipfile.lock") as file:
    pipfile_lock = json.load(file)


def format_str_config(name: str, config: str) -> str:
    name = name.lower()
    if (
        name not in pipfile_lock["default"]
        and name.replace("_", "-") in pipfile_lock["default"]
    ):
        name = name.replace("_", "-")
    if config == "*":
        return f'{pipfile_lock["default"][name]["version"]}'
    return config


def format_dict_config(name: str, config: dict) -> str:
    formatted = ""
    for key, value in config.items():
        if key == "version":
            formatted += format_str_config(name, value)
        if key == "os_name":
            formatted += f"; os_name{value}"
    return formatted


def is_editable(config: Union[str, dict]) -> bool:
    return isinstance(config, dict) and "editable" in config


class InstallRequiresUpdater(ast.NodeTransformer):
    def __init__(self):
        self._install_requires_found = False
        self._dependency_links_found = False

    def visit_Call(self, node):
        # TODO stronger check
        if hasattr(node.func, "id"):
            if node.func.id == "setup":
                install_requires = None
                dependency_links = None
                for keyword in node.keywords:
                    if keyword.arg == "install_requires":
                        install_requires = keyword.value
                    if keyword.arg == "dependency_links":
                        dependency_links = keyword.value

                dependency_links.elts = [
                    ast.Str(f'{config["git"]}#egg={name}')
                    for name, config in pipfile_.data["default"].items()
                    if is_editable(config)
                ]
                install_requires.elts = [
                    ast.Str(
                        f"{name}{format_str_config(name, config) if isinstance(config, str) else format_dict_config(name, config)}"
                    )
                    if not is_editable(config)
                    else ast.Str(name)
                    for name, config in pipfile_.data["default"].items()
                ]
        return node


with open("setup.py") as file:
    tree = ast.parse(file.read())

tree = InstallRequiresUpdater().visit(tree)


source = astunparse.unparse(tree)
reformatted_source, _ = yapf_api.FormatCode(source)
# print(reformatted_source)

with open("setup.py", "w+") as file:
    file.write(reformatted_source)
