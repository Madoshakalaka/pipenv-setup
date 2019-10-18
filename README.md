# Pipenv-Setup
[![travis-badge](https://travis-ci.org/Madoshakalaka/pipenv-setup.svg?branch=master)](https://travis-ci.org/Madoshakalaka/pipenv-setup)
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

## Features
### Beautiful pipenv flavored help

`$ pipenv-setup`

   ![help](https://raw.githubusercontent.com/Madoshakalaka/pipenv-setup/master/readme_assets/help.PNG)

### Sync `Pipfile.lock` to `setup.py`
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
### Checks Only
run `$ pipenv-setup check`
- checks four items
    - local package in default pipfile packages
    - Package version requirements in `install_requires` in setup.py that potentially violates Pipfile
    - Package version requirements in `dependency_links` in setup.py that differs from Pipfile
    - Default package in pipfile missing in `install_requires` or `dependency_links` in setup.py
- exits with non-zero code when conflict found (can be used in travis-ci)
- here is a somewhat extreme example
    
    ```
    $ pipenv-setup check
    
    package 'numpy' has version string: >=1.2 in setup.py, which potentially violates >=1.5 in pipfile
    package 'pywinusb' has version string: ==0.4.2 in setup.py, which is disjoint from ~=0.3.0 in pipfile
    package 'records' has version string: >=0.4.2,<0.5 in setup.py, which is disjoint from >0.5.0 in pipfile
    package 'django' has branch/version 1.11.5 in dependency_links, which is different than 1.11.4 listed in pipfile
    package 'requests' in pipfile but not in install_requires
    package 'e682b37' has a url in pipfile but not in dependency_links
    (exits with 1)
    ```


- provide `--ignore-local` flag to allow local packages in pipfile
    
    ```
    $ pipenv-setup check
  
    local package found in default dependency: e1839a8.
    Do you mean to make it dev dependency    
    (exits with 1)
    ```

    ```
    $ pipenv-setup check --ignore-local

    No version conflict or missing packages/dependencies found in setup.py!
    (exits with 0)
    ```

- provide `--strict` flag to only pass identical version requirements

    By default `pipenv-setup check` passes when the version `setup.py` specifies is "compatible" with `Pipfile`, i.e. is a subset of it.

    For example, `pipfile`: django~=1.1 `setup.py`: django==1.2 is such a case.
    
    provide `--strict` to allow only identical requirements such as `pipfile`: django~=1.1 `setup.py`: django>=1.1,<2.0
    
    Example output:
    ```
    pipenv-setup check --strict
    
    package 'pywinusb' has version string: ==0.4.2 in setup.py, which specifies a subset of * in pipfile
    package 'django' has version string: >=0.5 in setup.py, which is disjoint from ~=0.3.0 in pipfile
    package 'records' has version string: ==0.5.2 in setup.py, which specifies a subset of >0.5.0 in pipfile
    package 'requests' has version string: ==2.18.4 in setup.py, which specifies a subset of * in pipfile
    (exits with 1)
    ```

## Note
`$ pipenv-setup sync` command syncs `Pipfile.lock` to `setup.py`

While `$ pipenv-setup check` checks conflicts between `Pipfile` and `setup.py` (not `Pipfile.lock`!) 


This means `sync` will copy pinned versions from `Pipfile.lock`. This ensures the releases runs with almost exact the same dependencies as the dev environment.

While `check` allows more relaxed constraints (when you have semantic versioning in pipfile)

There is no philosophy behind this asymmetry and it makes a lot of sense to allow more user choice: add `sync --pipfile` and `check --lock` functionality. I welcome a feature request or PR :)
