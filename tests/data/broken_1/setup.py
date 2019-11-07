"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
Modified by Madoshakalaka@Github (dependency links added)
"""

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="sampleproject",  # Required
    version="0.0.0",  # Required
    description="A sample Python project",  # Optional
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    install_requires=[
        "certifi==2017.7.27.1",
        "chardet==3.0.4",
        "docopt==0.6.2",
        "et-xmlfile==1.0.1",
        "idna==2.6",
        "jdcal==1.3",
        "lxml==4.0.0",
        "odfpy==1.3.5",
        "openpyxl==2.4.8",
        "pysocks==1.6.7",
        "pytz==2017.2",
        "pywinusb==0.4.2; os_name == 'nt'",
        "pyyaml==5.1",
        "records==0.5.2",
        "requests==2.20.0",
        "sqlalchemy==1.1.14",
        "tablib==0.12.1",
        "unicodecsv==0.14.1",
        "urllib3==1.24.2",
        "xlrd==1.1.0",
        "xlwt==1.3.0",
    ],  # Optional
    # the first link is messed up
    dependency_links=[
        "git+https://github.com/djagg=dango",
        "https://github.com/divio/django-cms/archive/release/3.4.x.zip",
    ],
)
