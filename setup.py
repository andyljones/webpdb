#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 09:55:17 2016

@author: andyjones
"""

from distutils.core import setup

setup(name='RemoteDebugger',
      version='0.1',
      description='Remote debugger with web interface',
      author='Andy Jones',
      author_email='andyjones.ed@gmail.com',
      url='https://github.com/andyljones/webdebugger',
      packages=['webdebugger'],
      package_data={'webdebugger': ['resources', 'templates']},
      install_requires = ['flask']
     )