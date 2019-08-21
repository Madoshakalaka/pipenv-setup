'A setuptools based setup module.\nSee:\nhttps://packaging.python.org/guides/distributing-packages-using-setuptools/\nhttps://github.com/pypa/sampleproject\n'
from setuptools import setup, find_packages
from os import path
from io import open
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='pipenv-setup',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['lmao', 'pipfile~=0.0', 'astunparse~=1.6', 'yapf~=0.28'],
    dependency_links=['https://github.com/dask/distributed#egg=lmao'])
