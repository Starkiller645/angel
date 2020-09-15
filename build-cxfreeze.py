#!/usr/bin/python3
import sys
from cx_Freeze import setup, Executable
__author__ = 'Jacob Tye'
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
 name='angel/',
 version='0.7-beta.2',
 description='Angel for Linux - A Reddit Client',
 author='Jacob Tye',
 author_email='jacob.tye@outlook.com',
 license='GPLv3',
 url='https://github.com/hashbangstudios/angel',
 packages=['angel/'],
 package_data={'angel': ['assets/*']},
 entry_points={
 'console_scripts': [
 'angel=angel:MainWindow',
 ]
 },
 options = {"build_exe": build_exe_options},
 executables = [Executable("angel/__init__.py", base=base)],
)
