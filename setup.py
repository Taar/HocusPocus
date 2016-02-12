#!/usr/bin/env python

import sys

from setuptools.command.test import test as TestCommand
from setuptools import setup


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


install_requires = [
    'setuptools',
    # 'Adafruit_BBIO',
]

tests_require = [
    'pytest',
    'mock',
]

setup_requires = [
    'pytest-runner',
]

setup(
    name='HocusPocus',
    version='0.1',
    description='Door Controller',
    author='Randy Topliffe',
    author_email='randytopliffe@gamil.com',
    url='https://github.com/Taar/HocusPocus',
    packages=['hocuspocus'],
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    test_suite="tests",
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Door Controller :: Authentication',
    ],
    zip_safe=False,
    include_package_data=True,
)
