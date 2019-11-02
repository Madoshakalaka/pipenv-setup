from setuptools import setup, find_packages


setup(
    name="generic-package",  # Required
    version="0.0.0",  # Required
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    extras_require={
        "test": [],
        "dev": [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
        ],
    },  # Optional
)
