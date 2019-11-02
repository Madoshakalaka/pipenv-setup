from setuptools import setup, find_packages


setup(
    name="generic-package",  # Required
    version="0.0.0",  # Required
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    extras_require={},  # Optional
)
