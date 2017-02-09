#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

metadata = {}
exec(compile(open("bottlenose/metadata.py").read(), "bottlenose/metadata.py", 'exec'), metadata)

install_requires = []
if sys.version_info < (2, 6):
    # Python 2.6 was the first version to come bundled with the json module.
    install_requires.append("simplejson>=1.7.1")

# http://pypi.python.org/pypi?:action=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Utilities",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5"
]

setup(
    name='bottlenose',
    version=metadata['__version__'],
    description="A Python hook into the Amazon.com Product Advertising API",
    classifiers=classifiers,
    keywords='amazon, product advertising, api',
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    url='https://github.com/lionheart/bottlenose',
    packages=["bottlenose"],
    data_files=[("", ["LICENSE", "README.md"])],
    license=metadata['__license__'],
    install_requires=install_requires,
)
