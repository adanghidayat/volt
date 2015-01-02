#!/usr/bin/env python

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from volt import __version__


# per http://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


install_requires = [
    "future>=0.14.3",
    "Jinja2>=2.6",
    "Markdown>=2.3.1,<2.5",
]
long_description = open("README.rst").read()

# handle dependencies for python2.x (x < 7)
try:
    __import__("argparse")
except ImportError:
    install_requires.append("argparse")

setup(
    name = "Volt",
    version = __version__,
    description = "The static website generator with potential",
    long_description = long_description,
    author = "Wibowo Arindrarto",
    author_email = "bow@bow.web.id",
    url = "http://github.com/bow/volt/",
    keywords = "static website",
    license = "BSD",
    packages = find_packages(),
    include_package_data = True,
    install_requires = install_requires,
    extras_require = {
        "rst": ["docutils>=0.8.1"],
        "textile": ["textile>=2.1.5"],
        "syntax highlight": ["pygments>=1.4,<=1.5"],
    },
    tests_require = [
        'pytest==2.6.4',
        'pytest-cov==1.8.1',
        'mock>=0.8.0',
    ],
    cmdclass = {'test': PyTest},
    zip_safe = False,
    entry_points = """
    [console_scripts]
    volt = volt.main:main
    """,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ]
)
