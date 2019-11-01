# Preparation

`pipenv install --dev`

is all you need

# Tests

`$ pytest` runs all the tests on 3.7

Optionally, if you have python 3.6, python 3.7, python 3.8 installed

`$ tox` will run tests on python 3.6 3.7 3.8

# Pull Request

Upon pull request, travis will run tox tests on python 3.6/3.7/3.8 across 3 Operating Systems.(9 tests in total)

Tox also tests packaging from `setup.py`. Be sure to run `pipenv-setup sync` to update `setup.py` before a pull request.

# Test Data Creation

The majority of `pipenv-setup`'s function requires the presence of pipfile, lockfile, and setup.py

If you'd like to come up with test cases. Create one like this [generic test folder](tests/data/generic_nice_0).

When you manipulate test data with `pipenv`, be sure to do it in a different environment to 
avoid editing pipfile of `pipenv-setup`

> `gitdir` and `xml-subsetter` in generic test data are light-weight example packages