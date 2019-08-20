# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import setuptools

setuptools.setup(
    name="dspl2",
    version="0.0.1",
    author="Natarajan Krishnaswami",
    author_email="nkrishnaswami@google.com",
    description="DSPL 2.0 tools",
    url="https://github.com/google/dspl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_data={
        'dspl2': ['templates/*', 'schema/*'],
    },
    scripts=[
        'scripts/validator.py',
        'scripts/validator-server.py',
    ],
)
