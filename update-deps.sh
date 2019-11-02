#!/usr/bin/env bash
# install old dependencies first just be able to run itself
pip install -e .
pipenv-setup sync --dev --pipfile
# switch back
pipenv install --dev