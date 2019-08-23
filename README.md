# Pipenv-Setup
![travis-badge](https://travis-ci.org/Madoshakalaka/pipenv-setup.svg?branch=master)

sync dependencies in Pipfile.lock with setup.py

The ultimate python package development experience.

Never need again to change dependencies manually to `setup.py`

### Install

`$ pipenv install --dev pipenv-setup`

### Manual Usage

You can manually run `$ pipenv-setup` under directory that has your `Pipfile.lock` file.

If `setup.py` doesn't exist. A `setup.py` template will be created will dependencies extracted from the lock file.

### Travis CI

What's better, add to `.travis.yml` and run before every pypi release

The following yml file is an example that runs tests on python 3.6 and 3.7 and automatically syncs pipfile dependencies to setup.py before every release.
```yml
language: python
dist: xenial

install: 'pipenv install --dev'

stages:
- test
- deploy
jobs:
  include:
  - python: '3.7'
  - python: '3.6'
  - stage: deploy
    script: 'pipenv-setup'
    deploy:
      provider: pypi
      user: Madoshakalaka
      password:
        secure: xxxxxx
      on:
        tags: true
```