# Preparation

`pipenv install --dev`

is all you need

# Tests

`$ pytest` runs all the tests on 3.7

Optionally, if you have python 3.6, python 3.7, python 3.8 installed

`$ tox` will run tests on python 3.6 3.7 3.8

# Pull Request

Upon pull request, travis will run tests on python 3.6/3.7/3.8 across 3 Operating Systems. (9 tests in total)
