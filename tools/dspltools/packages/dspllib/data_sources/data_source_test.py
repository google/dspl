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

"""Tests of data_source module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import unittest

import data_source


class DataSourceColumnBundleTests(unittest.TestCase):
  """Tests of DataSourceColumnBundle object."""

  def setUp(self):
    self.column_bundle = data_source.DataSourceColumnBundle(
        [data_source.DataSourceColumn(column_id='col1'),
         data_source.DataSourceColumn(column_id='col2'),
         data_source.DataSourceColumn(column_id='col3')])

  def testAddColumn(self):
    self.column_bundle.AddColumn(
        data_source.DataSourceColumn(column_id='col4'))
    self.assertEqual(self.column_bundle.GetColumnByID('col4').column_id,
                     'col4')

  def testGetColumnByID(self):
    column = self.column_bundle.GetColumnByID('col2')
    self.assertEqual(column.column_id, 'col2')

  def testGetColumnByOrder(self):
    column = self.column_bundle.GetColumnByOrder(2)
    self.assertEqual(column.column_id, 'col3')

  def testGetNumColumns(self):
    self.assertEqual(self.column_bundle.GetNumColumns(), 3)

  def testGetColumnIterator(self):
    column_iterator = self.column_bundle.GetColumnIterator()
    column_id_list = [c.column_id for c in column_iterator]
    self.assertEqual(column_id_list, ['col1', 'col2', 'col3'])


class TableDataTest(unittest.TestCase):
  """Tests of TableData object."""

  def setUp(self):
    self.table_data = data_source.TableData(
        [[1, 2, 3], [4, 5, 6]])

  def testMergeValues(self):
    another_table_data = data_source.TableData([[4, 5, 6], [6, 7, 8]])
    merged_table_data = self.table_data.MergeValues(
        another_table_data, num_columns=2)
    self.assertEqual(merged_table_data.rows,
                     [[1, 2, 3, 4, 5], [4, 5, 6, 6, 7]])

  def testMergeContant(self):
    merged_table_data = self.table_data.MergeConstant('abcd')
    self.assertEqual(merged_table_data.rows,
                     [[1, 2, 3, 'abcd'], [4, 5, 6, 'abcd']])


class DataGuessingTest(unittest.TestCase):
  """Test of data type / format guessing functions."""

  def setUp(self):
    pass

  def testGuessType(self):
    self.assertEqual(data_source.GuessDataType('312332'), 'integer')
    self.assertEqual(data_source.GuessDataType('1999', 'year'), 'date')
    self.assertEqual(data_source.GuessDataType('3123.32'), 'float')
    self.assertEqual(data_source.GuessDataType('-3399332'), 'integer')
    self.assertEqual(data_source.GuessDataType('-3.0'), 'float')
    self.assertEqual(data_source.GuessDataType('1/1/11'), 'date')
    self.assertEqual(data_source.GuessDataType('01/1932'), 'date')
    self.assertEqual(data_source.GuessDataType('2-3-1932'), 'date')
    self.assertEqual(data_source.GuessDataType('something'), 'string')
    self.assertEqual(data_source.GuessDataType('3278.23728.223'), 'string')

  def testGuessDateFormat(self):
    self.assertEqual(data_source.GuessDateFormat('2819'), 'yyyy')
    self.assertEqual(data_source.GuessDateFormat('3/1990'), 'MM/yyyy')
    self.assertEqual(data_source.GuessDateFormat('1990-3'), 'yyyy-MM')
    self.assertEqual(data_source.GuessDateFormat('01-2-1981'), 'MM-dd-yyyy')
    self.assertEqual(data_source.GuessDateFormat('1990/2/3'), 'yyyy/MM/dd')

    self.assertRaises(data_source.DataSourceError,
                      data_source.GuessDateFormat, '1990.12')
    self.assertRaises(data_source.DataSourceError,
                      data_source.GuessDateFormat, 'Jan 1981')

  def testGuessDateConcept(self):
    self.assertEqual(data_source.GuessDateConcept('yyyy'), 'time:year')
    self.assertEqual(data_source.GuessDateConcept('yyyy-MM'), 'time:month')
    self.assertEqual(data_source.GuessDateConcept('yy.MM.dd'), 'time:day')
    self.assertEqual(data_source.GuessDateConcept('dd/MM/yyyy'), 'time:day')

    self.assertRaises(data_source.DataSourceError,
                      data_source.GuessDateConcept, 'yy-mm')
    self.assertRaises(data_source.DataSourceError,
                      data_source.GuessDateConcept, 'GG yyyy')


if __name__ == '__main__':
  unittest.main()
