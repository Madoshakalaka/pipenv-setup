import argparse


def cmd():
    # todo: fill command line functionality

    parser = argparse.ArgumentParser(description="sync pipfile with setup.py")

    # parser.add_argument(
    #     "blah",
    #     action="store",
    #     type=str,
    #     help="blah",
    # )

    argv = parser.parse_args()

    # add your command line program here

    print("reserved command line entry for python package pipenv-setup")
