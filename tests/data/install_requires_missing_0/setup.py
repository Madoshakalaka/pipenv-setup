from setuptools import setup, find_packages

setup(
    name="sampleproject",  # Required
    version="0.0.0",  # Required
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
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
        "pyyaml==3.12",
        "records==0.5.2",
        "sqlalchemy==1.1.14",
        "tablib==0.12.1",
        "unicodecsv==0.14.1",
        "urllib3==1.22",
        "xlrd==1.1.0",
        "xlwt==1.3.0",
    ],  # Optional
    dependency_links=[
        "git+https://github.com/django/django.git@1.11.4#egg=django",
        "https://github.com/divio/django-cms/archive/release/3.4.x.zip",
    ],
)
