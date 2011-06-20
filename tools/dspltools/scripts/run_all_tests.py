#!/usr/bin/python2.4
#
# Copyright 2011, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Run all tests defined in the DSPL Tools code."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import unittest

_TEST_MODULE_NAMES = [
    'dsplcheck_test',
    'dsplgen_test',
    'dspllib.data_sources.csv_data_source_test',
    'dspllib.data_sources.csv_data_source_sqlite_test',
    'dspllib.data_sources.data_source_test',
    'dspllib.data_sources.data_source_to_dspl_test',
    'dspllib.model.dspl_model_loader_test',
    'dspllib.model.dspl_model_test',
    'dspllib.validation.dspl_validation_test',
    'dspllib.validation.xml_validation_test']


def main():
  """Run all DSPL Tools tests and print the results to stderr."""
  test_suite = unittest.TestSuite()

  for test_module_name in _TEST_MODULE_NAMES:
    test_suite.addTests(
        unittest.defaultTestLoader.loadTestsFromName(test_module_name))

  unittest.TextTestRunner().run(test_suite)


if __name__ == '__main__':
  main()
