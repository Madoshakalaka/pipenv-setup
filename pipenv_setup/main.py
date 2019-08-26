import argparse
import json
import sys
from pathlib import Path
from sys import stderr
from typing import List, Union, NoReturn, Iterable

import pipfile
from colorama import Fore, init

from pipenv_setup import (
    lock_file_parser,
    setup_filler,
    setup_updater,
    pipfile_parser,
    setup_parser,
    msg_formatter,
)

# noinspection Mypy
from pipenv_setup.inconsistency_checker import InconsistencyChecker
from pipenv_setup.setup_updater import blacken


def print_help():
    print("Commands:")
    print(
        "  " + Fore.GREEN + "sync" + Fore.RESET + "\t\tsync Pipfile.lock with setup.py"
    )
    print(
        "  "
        + Fore.BLUE
        + "check"
        + Fore.RESET
        + "\t\tcheck whether Pipfile is consistent with setup.py.\n  \t\tNon-zero exit code if there is inconsistency\n  \t\t(package missing; version incompatible)"
    )


def cmd(argv=sys.argv):
    init()
    parser = argparse.ArgumentParser(description="sync Pipfile.lock with setup.py")

    subparsers = parser.add_subparsers(dest="command_name")

    # subparsers.required = True

    sync_parser = subparsers.add_parser(
        "sync", help="sync dependencies from Pipfile.lock to setup.py"
    )

    check_parser = subparsers.add_parser(
        "check",
        help="check whether Pipfile is consistent with setup.py. None zero exit code if there is inconsistency (package missing; version incompatible)",
    )

    check_parser.add_argument(
        "--ignore-local",
        action="store_true",
        help="allow local packages in pipfile default packages",
    )

    argv = parser.parse_args(argv[1:])

    if argv.command_name == "sync":
        sync(argv)
    elif argv.command_name == "check":
        check(argv)
    else:
        print_help()


def congratulate(msg: Union[str, Iterable[str]]):
    """
    print green text to stdout

    :raise TypeError: if `msg` is of wrong type
    """
    msgs = []  # type: List[str]
    if isinstance(msg, str):
        msgs = [msg]
    elif hasattr(msg, "__iter__"):
        for m in msg:
            msgs.append(m)
    else:
        raise TypeError()
    for m in msgs:
        print(Fore.GREEN + m + Fore.RESET)


def fatal_error(msg: Union[str, List[str]]) -> NoReturn:
    """
    print text or a list of text to stderr then exit with error code 1

    :raise TypeError: if msg is of wrong type
    """
    if isinstance(msg, str):
        print(msg, file=stderr)
    elif isinstance(msg, list):
        for m in msg:
            print(m, file=stderr)
    else:
        raise TypeError()
    sys.exit(1)


def check(args):
    if not Path("Pipfile").exists():
        fatal_error("Pipfile not found")
    if not Path("setup.py").exists():
        fatal_error("setup.py not found")

    parsed_pipfile = pipfile.load(Path("Pipfile"))
    local_packages, remote_packages = pipfile_parser.get_default_packages(
        parsed_pipfile
    )

    if local_packages and not args.ignore_local:
        package_names = ", ".join(local_packages)
        fatal_error(
            "local package found in default dependency: %s.\nDo you mean to make it dev dependency "
            % package_names
        )

    with open("setup.py") as setup_file:
        setup_code = setup_file.read()
    try:
        install_requires, dependency_links = setup_parser.get_install_requires_dependency_links(
            setup_code
        )
    except (ValueError, SyntaxError) as e:
        fatal_error(str(e))

    # fatal_error is a NoReturn function, pycharm gets confused
    # noinspection PyUnboundLocalVariable
    checker = InconsistencyChecker(install_requires, dependency_links, remote_packages)

    reports = []
    checks = (
        checker.check_install_requires_conflict,
        checker.check_dependency_links_conflict,
        checker.check_lacking_install_requires,
        checker.check_lacking_dependency_links,
    )
    for check_item in checks:
        try:
            reports += check_item()
        except ValueError as e:
            print(e, file=stderr)
            fatal_error("dependency check failed")
    if len(reports) == 0:
        congratulate(msg_formatter.checked_no_problem())
    else:
        fatal_error(reports)


def sync(args):
    pipfile_path, lock_file_path, setup_file_path = required_files = [
        Path("Pipfile"),
        Path("Pipfile.lock"),
        Path("setup.py"),
    ]

    # found_files = tuple(filter(Path.exists, required_files))
    missing_files = tuple(filter(lambda x: not x.exists(), required_files))
    only_setup_missing = len(missing_files) == 1 and not setup_file_path.exists()

    if not missing_files or only_setup_missing:
        dependency_arguments = {"dependency_links": [], "install_requires": []}
        with open(lock_file_path) as lock_file:
            lock_file_data = json.load(lock_file)
        local_packages, remote_packages = lock_file_parser.get_default_packages(
            lock_file_data
        )
        for local_package in local_packages:
            print("package %s is local, omitted in setup.py" % local_package)

        success_count = 0
        for remote_package_name, remote_package_config in remote_packages.items():
            try:
                destination_kw, value = lock_file_parser.format_remote_package(
                    remote_package_name, remote_package_config
                )
            except ValueError as e:
                fatal_error(
                    [
                        str(e),
                        "package %s is not synced to setup.py" % remote_package_name,
                    ]
                )
            else:
                success_count += 1
                dependency_arguments[destination_kw].append(value)
        if only_setup_missing:
            print(msg_formatter.setup_not_found())
            print("Creating boilerplate setup.py...")
            setup_code = setup_filler.fill_boilerplate(dependency_arguments)
            if setup_code is None:
                fatal_error("Can not find setup.py template file")
            try:
                with open(setup_file_path, "w") as new_setup_file:
                    new_setup_file.write(setup_code)
                blacken(str(setup_file_path))
            except OSError as e:
                fatal_error([str(e), "failed to write setup.py file"])
            else:
                congratulate(
                    [
                        "setup.py generated",
                        "%d packages moved from Pipfile.lock to setup.py"
                        % success_count,
                        "Please edit the required fields in the generated file",
                    ]
                )

        else:  # all files exist. Update setup.py
            try:
                setup_updater.update_setup(dependency_arguments, setup_file_path)
            except ValueError as e:
                fatal_error([str(e), msg_formatter.no_sync_performed()])
            congratulate(msg_formatter.update_success(success_count))
    else:
        msgs = []
        for file in missing_files:
            msgs.append(msg_formatter.missing_file(file))
        fatal_error(msgs + [msg_formatter.no_sync_performed()])
