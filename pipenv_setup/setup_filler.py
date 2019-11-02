from __future__ import print_function

from os import path
from os.path import dirname
from sys import stderr
from typing import Dict, Optional, List


def fill_boilerplate(
    dependency_arguments,
):  # type: (Dict[str, List[str]]) -> Optional[str]
    """
    read boilerplate setup.py file, fill dependency_links and install_requires keyword arguments and format the code

    :return filled and formatted code. None when file reading is errored
    """

    try:
        with open(
            path.join(dirname(__file__), "res", "setup_template.py")
        ) as boilerplate_setup_file:
            boilerplate_setup_code = boilerplate_setup_file.read()
    except OSError as err:
        print(str(err), file=stderr)
        print("pipenv-setup failed to create setup.py", file=stderr)
        return None
    else:
        boilerplate_setup_code = boilerplate_setup_code.replace(
            "dependency_links=[]",
            "dependency_links=%s" % dependency_arguments["dependency_links"],
        )
        boilerplate_setup_code = boilerplate_setup_code.replace(
            "install_requires=[]",
            "install_requires=%s" % dependency_arguments["install_requires"],
        )
        return boilerplate_setup_code
