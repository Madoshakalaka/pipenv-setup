# Preparation

`pipenv install --dev`

is all you need

# Tests

`$ pytest` runs all the tests on 3.7

Optionally, if you have python 3.6, python 3.7, python 3.8 installed

`$ tox` will run tests on python 3.6 3.7 3.8

# Pull Request

Upon pull request, travis will run tests on python 3.6/3.7/3.8 across 3 Operating Systems. (9 tests in total)

# Caveate

Do not manually change dependencies or use `$ pipenv-setup sync` directly to change `setup.py`.

Run `$ pipenv run update-deps` instead

It installs old dependencies first just to run `pipenv-setup`
