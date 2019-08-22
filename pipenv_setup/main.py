import argparse
from pathlib import Path
from sys import stderr


def cmd():

    parser = argparse.ArgumentParser(description="sync pipfile with setup.py")

    # parser.add_argument(
    #     "blah",
    #     action="store",
    #     type=str,
    #     help="blah",
    # )

    # argv = parser.parse_args()

    # add your command line program here

    required_files = [Path("Pipfile"), Path("Pipfile.lock"), Path("setup.py")]

    missing_files = tuple(filter(Path.exists, required_files))
    if len(missing_files) == 1 and missing_files[0].name == "setup.py":
        print("setup.py not found under current directory")
        print("Creating boilerplate setup.py...")
        try:
            with open(missing_files[0], "w") as setup_file:
                setup_file.write("123")
        except OSError as err:
            print(f"OS error: {err}", file=stderr)
            print("pipenv-setup failed to create setup.py", file=stderr)

    if any(missing_files):
        pass
