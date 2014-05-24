"""
Created on May 24, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""

from distutils.core import setup

setup(
    name='slyme',
    version='0.1.0',
    author='John Brunelle <john_brunelle@harvard.edu>, Aaron Kitzmiller <aaron_kitzmiller@harvard.edu>',
    author_email='aaron_kitzmiller@harvard.edu',
    packages=['slyme', 'test'],
    url='http://pypi.python.org/pypi/Slyme/',
    license='LICENSE.txt',
    description='Slurm Python modules using the executables',
    long_description=open('README.txt').read(),
)
