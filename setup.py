#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='recorder',
    version='0.1.0',
    description='stream recorder && automatic upload',
    long_description=readme,
    author='Jim Liu',
    author_email='hldh214@gmail.com',
    url='https://github.com/hldh214/recorder',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
