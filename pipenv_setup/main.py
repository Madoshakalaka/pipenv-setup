from __future__ import print_function

import argparse
import sys
from sys import stderr
from typing import List, Union, Iterable, Text

try:
    # Seems like NoReturn is not backported properly in python 3.5
    # build failure
    # https://travis-ci.org/Madoshakalaka/pipenv-setup/jobs/613058915?utm_medium=notification&utm_source=github_status
    from typing import NoReturn
except ImportError:
    pass

from six import string_types

from colorama import Fore, init
from vistir.compat import Path
from pipenv_setup import (
    lockfile_parser,
    setup_filler,
    setup_updater,
    pipfile_parser,
    setup_parser,
    msg_formatter,
)

# noinspection Mypy
from .inconsistency_checker import InconsistencyChecker
from .setup_updater import format_file

# todo: fix version conflict report: "is a subset of {empty string} in pipfile"
# should report empty requirement as an asterisk


def cmd(argv=sys.argv):
    init()
    parser = argparse.ArgumentParser(
        description="sync Pipfile.lock with setup.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=msg_formatter.colorful_help(),
    )

    subparsers = parser.add_subparsers(dest="command_name")

    sync_parser = subparsers.add_parser(
        "sync", help="sync dependencies from Pipfile.lock to setup.py"
    )

    sync_parser.add_argument(
        "-p",
        "--pipfile",
        action="store_true",
        help="sync Pipfile instead of Pipfile.lock",
    )

    sync_parser.add_argument(
        "-d",
        "--dev",
        action="store_true",
        help="provide this flag to also sync development packages to extras [dev] in setup.py",
    )

    check_parser = subparsers.add_parser(
        "check",
        help="check whether Pipfile is consistent with setup.py.\n"
        " None zero exit code if there is inconsistency\n (package missing; version incompatible)",
    )

    check_parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="provide this flag to make check fail when pipfile is not identical with setup.py."
        " By default, compatible but not identical version configs will pass. e.g. ==1.1 is compatible with ~=1.0",
    )

    check_parser.add_argument(
        "-i",
        "--ignore-local",
        action="store_true",
        help="allow local packages in pipfile default packages",
    )

    check_parser.add_argument(
        "-l",
        "--lockfile",
        action="store_true",
        help="check the dependencies from setup.py against Pipfile.lock instead of Pipfile."
        " By default, the dependencies from setup.py are checked against the Pipfile.",
    )

    if len(argv[1:]) == 0:
        parser.print_help()
    else:
        argv = parser.parse_args(argv[1:])

        if argv.command_name == "sync":
            sync(argv)
        elif argv.command_name == "check":
            check(argv)


def congratulate(msg):  # type: (Union[Text, Iterable[Text]]) -> None
    """
    print green text to stdout

    :raise TypeError: if `msg` is of wrong type
    """
    msgs = []  # type: List[str]
    if isinstance(msg, string_types):
        msgs = [msg]
    elif hasattr(msg, "__iter__"):
        for m in msg:
            msgs.append(m)
    else:
        raise TypeError()
    for m in msgs:
        print(Fore.GREEN + m + Fore.RESET)


def fatal_error(msg):  # type: (Union[Text, List[Text]]) -> NoReturn
    """
    print text or a list of text to stderr then exit with error code 1

    :raise TypeError: if msg is of wrong type
    """
    if isinstance(msg, string_types):
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

    if args.lockfile:
        local_packages, remote_packages = lockfile_parser.get_default_packages(
            Path("Pipfile.lock")
        )
    else:
        local_packages, remote_packages = pipfile_parser.get_default_packages(
            Path("Pipfile")
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
        (
            install_requires,
            dependency_links,
        ) = setup_parser.get_install_requires_dependency_links(setup_code)
    except (ValueError, SyntaxError) as e:
        fatal_error(str(e))

    # fatal_error is a NoReturn function, pycharm gets confused
    # noinspection PyUnboundLocalVariable
    checker = InconsistencyChecker(
        install_requires, dependency_links, remote_packages, args.strict
    )

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


def sync(argv):
    pipfile_path, lockfile_path, setup_file_path = required_files = [
        Path("Pipfile"),
        Path("Pipfile.lock"),
        Path("setup.py"),
    ]

    missing_files = tuple(filter(lambda x: not x.exists(), required_files))
    only_setup_missing = len(missing_files) == 1 and not setup_file_path.exists()
    only_lockfile_missing = (
        len(missing_files) == 1 and missing_files[0] == lockfile_path
    )

    # todo: refactor out a parser class
    if argv.pipfile:
        parser = pipfile_parser
        file = pipfile_path
    else:
        parser = lockfile_parser
        file = lockfile_path

    if (
        not missing_files
        or only_setup_missing
        or (only_lockfile_missing and argv.pipfile)
    ):

        dependency_arguments = {
            "dependency_links": [],
            "install_requires": [],
            "extras_require": [],
        }
        local_packages, remote_packages = parser.get_default_packages(file)
        if argv.dev:
            # parse development package in lockfile
            dev_local_packages, dev_remote_packages = parser.get_dev_packages(file)
            for dev_local_package in dev_local_packages:
                print(
                    "Development package %s is local, omitted in setup.py"
                    % dev_local_package
                )

        for local_package in local_packages:
            print("package %s is local, omitted in setup.py" % local_package)

        default_package_success_count = 0
        # format default packages
        for remote_package_name, remote_package_config in remote_packages.items():
            try:
                destination_kw, value = parser.format_remote_package(
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
                default_package_success_count += 1
                dependency_arguments[destination_kw].append(value)

        dev_package_success_count = 0
        if argv.dev:
            # format dev packages
            # noinspection PyUnboundLocalVariable
            for (
                remote_package_name,
                remote_package_config,
            ) in dev_remote_packages.items():

                destination_kw, value = parser.format_remote_package(
                    remote_package_name, remote_package_config, dev=True
                )
                dev_package_success_count += 1
                dependency_arguments[destination_kw].append(value)

        if only_setup_missing:
            print(msg_formatter.setup_not_found())
            print("Creating boilerplate setup.py...")
            setup_code = setup_filler.fill_boilerplate(dependency_arguments)
            if setup_code is None:
                fatal_error("Cannot find setup.py template file")
            try:
                with open(str(setup_file_path), "w") as new_setup_file:
                    new_setup_file.write(setup_code)
                format_file(setup_file_path)
            except OSError as e:
                fatal_error([str(e), "failed to write setup.py file"])
            else:
                congratulate(
                    msg_formatter.generate_success(
                        default_package_success_count,
                        dev_package_success_count,
                        argv.pipfile,
                    )
                )

        else:  # all files exist. Update setup.py
            try:
                setup_updater.update_setup(
                    dependency_arguments, setup_file_path, argv.dev
                )
            except ValueError as e:
                fatal_error([str(e), msg_formatter.no_sync_performed()])
            congratulate(
                msg_formatter.update_success(
                    default_package_success_count,
                    dev_package_success_count,
                    argv.pipfile,
                )
            )
    else:
        msgs = []
        for file in missing_files:
            msgs.append(msg_formatter.missing_file(file))
        fatal_error(msgs + [msg_formatter.no_sync_performed()])
