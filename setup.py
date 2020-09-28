#!/usr/bin/python3
from setuptools import setup
__author__ = 'Jacob Tye'
setup(
 name='angel',
 version='0.8-beta',
 description='Angel for Linux - A Reddit Client',
 author='Jacob Tye',
 author_email='jacob.tye@outlook.com',
 license='GPLv3',
 url='https://github.com/Starkiller645/angel',
 packages=['angel'],
 package_data={'angel': ['assets/*']},
 entry_points={
 'console_scripts': [
 'angel=angel:MainWindow',
 ]
 },
)
