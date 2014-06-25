"""
Created on May 24, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os
from setuptools import setup, find_packages

setup(
    name = "slyme",
    version = "0.2.0",
    author='John Brunelle <john_brunelle@harvard.edu>, Aaron Kitzmiller <aaron_kitzmiller@harvard.edu>',
    author_email='aaron_kitzmiller@harvard.edu',
    description='Python modules for wrapping the Slurm tools',
    license='LICENSE.txt',
    keywords = "slurm",
    url='http://pypi.python.org/pypi/slyme/',
    packages = find_packages(),
    package_data={'slyme': ['*.conf']},
    long_description=open('README.txt').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
