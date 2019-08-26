# Pipenv-Setup
![travis-badge](https://travis-ci.org/Madoshakalaka/pipenv-setup.svg?branch=master)
[![PyPI version](https://badge.fury.io/py/pipenv-setup.svg)](https://badge.fury.io/py/pipenv-setup)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pipenv-setup.svg)](https://pypi.python.org/pypi/pipenv-setup/)
[![codecov](https://codecov.io/gh/Madoshakalaka/pipenv-setup/branch/master/graph/badge.svg)](https://codecov.io/gh/Madoshakalaka/pipenv-setup)

Sync dependencies in Pipfile.lock to setup.py

A beautiful python package development tool.

Never need again to change dependencies 
manually in `setup.py` and enjoy the same
 dependency locking
 
 Or just check whether setup.py and pipfile are consistent and sync dependency when necessary
### Install

`$ pipenv install --dev pipenv-setup`

it creates command line entry `$ pipenv-setup`

### Features
##### Beautiful pipenv flavored help
    `$ pipenv-setup`

   ![help](https://raw.githubusercontent.com/Madoshakalaka/pipenv-setup/master/readme_assets/help.PNG)

##### Sync `Pipfile.lock` to `setup.py`
- supports assorted package configuration. You can have a pipfile as ugly as you want:
    ```Pipfile
    [package]
    requests = { extras = ['socks'] }
    records = '>0.5.0'
    django = { git = 'https://github.com/django/django.git', ref = '1.11.4', editable = true }
    "e682b37" = {file = "https://github.com/divio/django-cms/archive/release/3.4.x.zip"}
    "e1839a8" = {path = ".", editable = true}
    pywinusb = { version = "*", os_name = "=='nt'", index="pypi"}
    ```
    `pipenv-setup` will still figure things out:
    
    `$ pipenv-setup sync`
    ```
    package e1839a8 is local, omitted in setup.py
    setup.py successfully updated
    23 packages from Pipfile.lock synced to setup.py
    ```
    And things will be where they should be
    ```python
    # setup.py
        install_requires=[
            "certifi==2017.7.27.1",
            "chardet==3.0.4",
            "pywinusb==0.4.2; os_name == 'nt'",
            ...,
            "xlrd==1.1.0",
            "xlwt==1.3.0",
        ],
        dependency_links=[
            "git+https://github.com/django/django.git@1.11.4#egg=django",
            "https://github.com/divio/django-cms/archive/release/3.4.x.zip",
        ],
    ```
- [Blackened](https://github.com/psf/black) setup.py file.
- [Template](https://github.com/pypa/sampleproject/blob/master/setup.py) generation with filled dependencies in the absence of a setup file.

    `$ pipenv-setup sync`
    ```
    setup.py not found under current directory
    Creating boilerplate setup.py...
    setup.py successfully generated under current directory
    23 packages moved from Pipfile.lock to setup.py
    Please edit the required fields in the generated file
    ```
##### Check `Pipfile` and `setup.py`
run `$ pipenv-setup check`
- checks four items
    - local package in default pipfile packages
    - Package version requirements in `install_requires` in setup.py potentially violates that in Pipfile
    - Package version requirements in `dependency_links` in setup.py potentially violates that in Pipfile
    - Default package in pipfile missing in `install_requires` or `dependency_links` in setup.py
- exits with non-zero code when conflict found (for use in travis-ci)
- here is a somewhat extreme example

    ![extreme](https://raw.githubusercontent.com/Madoshakalaka/pipenv-setup/master/readme_assets/extreme_errors.png)

- provide `--ignore-local` flag to allow local packages in pipfile

    ![ignore-local](https://raw.githubusercontent.com/Madoshakalaka/pipenv-setup/master/readme_assets/ignore_local.PNG)

### Travis CI

You can add `pipenv-setup` to `.travis.yml` and sync automatically before every pypi release. Or just check consistency and fail the build to remind manual modification.

The following yml file is an example that runs tests on python 3.6 and 3.7 and automatically syncs pipfile dependencies to setup.py before every release. For explanation see [this gist](https://gist.github.com/Madoshakalaka/84198d7c1b042027375481dc1b8cbae8)
```yml
language: python
dist: xenial

install: 'pipenv install --dev'
script: 'pytest'

stages:
- test
- deploy
jobs:
  include:
  - python: '3.7'
  - python: '3.6'
  - stage: deploy
    script: 'pipenv-setup sync'
    deploy:
      provider: pypi
      user: Madoshakalaka
      password:
        secure: xxxxxxxxx
      on:
        tags: true
```

### Note
`$ pipenv-setup sync` command syncs `Pipfile.lock` to `setup.py`

While `$ pipenv-setup check` checks conflicts between `Pipfile` and `setup.py` (not `Pipfile.lock`!) 


This means `sync` will copy pinned versions from `Pipfile.lock`. This ensures the releases runs with almost exact the same dependencies as the dev environment.

While `check` allows more relaxed constraints (when you have semantic versioning in pipfile)

There is no philosophy behind this asymmetry and it makes a lot of sense to allow more user choice: add `sync --pipfile` and `check --lock` functionality. I welcome a feature request or PR :)
