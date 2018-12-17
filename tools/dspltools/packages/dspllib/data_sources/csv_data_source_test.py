#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Tests of csv_data_source module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import unittest

import csv_data_source
import csv_sources_test_suite


class CSVDataSourceTests(csv_sources_test_suite.CSVSourcesTests):
  """Tests of the CSVDataSource object."""

  def setUp(self):
    self.data_source_class = csv_data_source.CSVDataSource

    super(CSVDataSourceTests, self).setUp()


class CSVDataSourceErrorTests(csv_sources_test_suite.CSVSourcesErrorTests):
  """Tests of the CSVDataSource object under various error conditions."""

  def setUp(self):
    self.data_source_class = csv_data_source.CSVDataSource

    super(CSVDataSourceErrorTests, self).setUp()


if __name__ == '__main__':
  unittest.main()
