from setuptools import setup, find_packages
from os import path


setup(
    name="generic-package",  # Required
    version="0.0.0",  # Required
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    extras_require={"test": ["pytest"]},
    install_requires=[],
    dependency_links=[],
)
