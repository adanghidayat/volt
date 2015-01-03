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


with open('README.rst') as src:
    long_description = src.read()

with open('requirements.txt') as src:
    install_requires = [line.strip() for line in src]

with open('dev-requirements.txt') as src:
    tests_require = [line.strip() for line in src]

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
        "rst": ["docutils==0.8.1"],
        "textile": ["textile==2.1.5"],
        "syntax highlight": ["pygments==1.5"],
    },
    tests_require = tests_require,
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
