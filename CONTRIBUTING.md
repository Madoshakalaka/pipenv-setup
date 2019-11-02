# Preparation

`pipenv install --dev`

is all you need

# Tests

`$ pytest` runs all the tests with your python version

Optionally, if you have python 2.7/3.4/3.5/3.6/3.7/3.8 installed

`$ tox -r` will run tests on 6 python versions

Specify `$ tox -r -e pyXX` to run tests with specific python version

# Pull Request

Upon pull request, travis will run tox tests on python 2.7/3.4/3.5/3.6/3.7/3.8 across 3 Operating Systems.(yep, 18 tests in total)

Tox also tests packaging from `setup.py`. 

> If dependency is changed, 
> be sure to run `$ pipenv run update-deps` to update `setup.py` before a pull request.
> Note you can't just do `$ pipenv-setup sync` if dependency is changed. `pipenv-setup` won't start because of un-matched dependencies.
> `$ pipenv run update-deps` may fail too if new dependency is introduced in code, in which case please manually change setup.py.

tl;dr: manually change dependency in `setup.py` is a safe bet

# Test Data Creation

The majority of `pipenv-setup`'s function requires the presence of pipfile, lockfile, and setup.py

If you'd like to come up with test cases. Create one like this [generic test folder](tests/data/generic_nice_0).

When you manipulate test data with `pipenv`, be sure to do it in a different environment to 
avoid editing pipfile of `pipenv-setup`

> `gitdir` and `xml-subsetter` in generic test data are light-weight example packages
