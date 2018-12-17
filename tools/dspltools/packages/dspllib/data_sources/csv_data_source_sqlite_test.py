#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Tests of csv_data_source_sqlite module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import unittest

import csv_data_source_sqlite
import csv_sources_test_suite


class CSVDataSourceSqliteTests(csv_sources_test_suite.CSVSourcesTests):
  """Tests of the CSVDataSourceSqlite object."""

  def setUp(self):
    self.data_source_class = csv_data_source_sqlite.CSVDataSourceSqlite

    super(CSVDataSourceSqliteTests, self).setUp()


class CSVDataSourceSqliteErrorTests(
        csv_sources_test_suite.CSVSourcesErrorTests):
  """Tests of the CSVDataSourceSqlite object under various error conditions."""

  def setUp(self):
    self.data_source_class = csv_data_source_sqlite.CSVDataSourceSqlite

    super(CSVDataSourceSqliteErrorTests, self).setUp()


if __name__ == '__main__':
  unittest.main()
