# Preparation

`pipenv install --dev`

is all you need

> about python interpreter: this project doesn't have "requires python_version==x.x" in Pipfile.
> It means you have freedom using any version of python you want.
> say: pipenv install --dev --python 3.7
>
> This could result in an ever changing Lockfile as people develop in different python versions, and
> different version may result in different dependencies.

# To Introduce New Dependencies
- write compatible setup.py and code

This project aims to run on most compatible python versions.

If you want to introduce your favorite python package to this project, please note, Pipfile is synced to setup.py 
in this project and setup.py will be published to everyone.
 
This means you have the responsibility to specify markers 
(python version requirements, os requirements) when you `pipenv install ` a not so compatible package.

e.g. you can do a `$ pipenv install "advanced_tech~=x.x; python_versions>='3.6'"` and write python version dependent code for
lower python versions. (or you can do a simple `$ pipenv install advanced_tech`, edit markers in Pipfile, and do a `pipenv install` again)

An example in our project:

When we update user's `setup.py`, `black` is used to format the file. However `black` does not support python versions below
3.6. So we have `autopep8` as an alternative  

```
# pipfile

black = {markers = "python_version>='3.6'",version = ">=19.3b0"}
autopep8 = {markers = "python_version<'3.6'",version = "~=1.4"}
``` 

And in the code:

```
# setup_updater.py

def format_file(file):
    """
    use black or autopep8 to format python file
    """
    try:
        import black
        # do black formatting
        ...

    except ImportError:
        # use autopep8
        import autopep8
        ...
```



# Pull Request

Upon pull request, travis will run tox tests on python 2.7/3.5/3.6/3.7/3.8 across 3 Operating Systems.
(yep, at most 15 tests in total, some of them may be disabled now and then because of configuration issues)

Tox also tests packaging from `setup.py`. Before any pull request, be sure to sync changed dependencies to `setup.py`.

A caveat is that when you have changed dependencies, command entry `$ pipenv-setup sync` may not be able to start, 
as the shortcut command is provided by `setup.py` and `setup.py` detects mismatched dependencies and throw up.

Please use package entry instead: `python3 -m pipenv_setup sync --dev --pipfile`. Or use the shortcut in Pipfile:
`$ pipenv run sync-deps` 


# Tests

`$ pytest` runs tests with your python version

Optionally, if you have some of python 2.7/3.5/3.6/3.7/3.8 installed

`$ tox` will run tests on at most 6 python versions depending how many versions you installed on your machine

Specify `$ tox -e pyXX` to run tests with specific python version. It's worth noting `py37` is the major test environment 
and has extra `mypy` tests for static type checking (if type hints are used in code). For lightweight tests, it's a good
 choice is to at least have python3.7 and use `$ tox -e py37` instead of `$ pytest`

In this project, dev dependencies in Pipfile should be synced to `setup.py` in `extras_require`, as tox installs 
`pipenv-setup[dev]` before running tests.

As mentioned, if you made changes to dependencies in pipfile, before running tox tests, use `$ pipenv run sync-deps`  to
 update them to `setup.py`

# Test Data Creation

The majority of `pipenv-setup`'s function requires the presence of pipfile, lockfile, and setup.py

If you'd like to come up with test cases. Create one like this [generic test folder](tests/data/generic_nice_0).

If you manipulate test data with `pipenv`, be sure to do it in a different environment to 
avoid editing Pipfile of this project. 

> `gitdir` and `xml-subsetter` in generic test data are light-weight example packages

# Others

If you are working on something. It's appreciated to have an issue about it first so that we know it's being worked on :)