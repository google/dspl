#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

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
