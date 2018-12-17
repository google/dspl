#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Setup script for the DSPLtools suite."""

from distutils.core import setup


setup(name='dspltools',
      version='0.5.0',
      description='Suite of command-line tools for generating DSPL datasets',
      author='Benjamin Yolken',
      author_email='yolken@google.com',
      url='http://code.google.com/apis/publicdata/docs/dspltools.html',
      packages=['dspllib', 'dspllib.data_sources',
                'dspllib.model', 'dspllib.validation'],
      package_dir={'dspllib': 'packages/dspllib'},
      package_data={'dspllib.validation': ['schemas/*.xsd',
                                           'test_dataset/*.csv',
                                           'test_dataset/*.xml']},
      scripts=['scripts/dsplcheck.py', 'scripts/dsplgen.py',
               'scripts/run_all_tests.py'])
