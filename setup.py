#!/usr/bin/env python
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    _license = f.read()

setup(
    name='recorder',
    version='1.10.0',
    description='stream recorder && automatic upload',
    long_description=readme,
    author='Jim Liu',
    author_email='hldh214@gmail.com',
    url='https://github.com/hldh214/recorder',
    license=_license,
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='~=3.5',
    install_requires=requirements
)
