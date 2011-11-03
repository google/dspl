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

"""A set of tests useful for CSV data sources."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import StringIO
import unittest

import data_source


_TEST_CSV_CONTENT = (
"""date[type=date;format=yyyy-MM-dd],category1,category2[concept=geo:us_state;parent=category3;total_val=total],category3,metric1[extends=quantity:ratio;slice_role=metric],metric2[aggregation=avg],metric3[aggregation=count]
1980-01-01,red,california,west,89,321,71.21
1981-01-01,red,california,west,99,231,391.2
1982-01-01,blue,maine's,east,293,32,2.31
1983-01-01,blue,california,west,293,12,10.3
1984-01-01,red,maine's,east,932,48,10.78
1984-01-01,red,oregon,west,32,33,-14.34
1985-01-01,red,total,east,21,98,87.0
1986-01-01,red,total,west,33,90,-10.1""")


class CSVSourcesTests(unittest.TestCase):
  """Basic tests of a CSV DataSource object."""

  def setUp(self):
    self.csv_file = StringIO.StringIO(_TEST_CSV_CONTENT)
    self.data_source_obj = self.data_source_class(self.csv_file, verbose=False)

  def tearDown(self):
    self.data_source_obj.Close()
    self.csv_file.close()

  def testColumnBundle(self):
    """Test that column bundle is properly generated."""
    column_bundle = self.data_source_obj.GetColumnBundle()

    self.assertEqual(
        [c.column_id for c in column_bundle.GetColumnIterator()],
        ['date', 'category1', 'category2', 'category3',
         'metric1', 'metric2', 'metric3'])
    self.assertEqual(
        [c.data_type for c in column_bundle.GetColumnIterator()],
        ['date', 'string', 'string', 'string', 'integer', 'integer', 'float'])
    self.assertEqual(
        [c.data_format for c in column_bundle.GetColumnIterator()],
        ['yyyy-MM-dd', '', '', '', '', '', ''])
    self.assertEqual(
        [c.concept_ref for c in column_bundle.GetColumnIterator()],
        ['time:day', '', 'geo:us_state', '', '', '', ''])
    self.assertEqual(
        [c.concept_extension for c in column_bundle.GetColumnIterator()],
        ['', '', '', '', 'quantity:ratio', '', ''])
    self.assertEqual(
        [c.slice_role for c in column_bundle.GetColumnIterator()],
        ['dimension', 'dimension', 'dimension', 'dimension', 'metric', 'metric',
         'metric'])
    self.assertEqual(
        [c.rollup for c in column_bundle.GetColumnIterator()],
        [False, False, False, True, False, False, False])
    self.assertEqual(
        [c.parent_ref for c in column_bundle.GetColumnIterator()],
        ['', '', 'category3', '', '', '', ''])
    self.assertEqual(
        [c.total_val for c in column_bundle.GetColumnIterator()],
        ['', '', 'total', '', '', '', ''])

  def testEntityTableGeneration(self):
    """Test that single-concept tables are generated correctly."""
    table_data = self.data_source_obj.GetTableData(
        data_source.QueryParameters(
            data_source.QueryParameters.CONCEPT_QUERY, ['category2']))

    # Make sure quotes are properly escaped
    self.assertEqual(table_data.rows,
                     [['california'], ['maine\'s'], ['oregon']])

  def testMultiEntityTableGeneration(self):
    """Test that multi-concept tables are generated correctly."""
    table_data = self.data_source_obj.GetTableData(
        data_source.QueryParameters(
            data_source.QueryParameters.CONCEPT_QUERY,
            ['category2', 'category3']))

    # Make sure quotes are properly escaped
    self.assertEqual(table_data.rows,
                     [['california', 'west'], ['maine\'s', 'east'],
                      ['oregon', 'west']])

  def testSliceTableGeneration(self):
    """Test that slice tables are generated correctly."""
    table_data = self.data_source_obj.GetTableData(
        data_source.QueryParameters(
            data_source.QueryParameters.SLICE_QUERY,
            ['metric3', 'category2', 'metric1', 'metric2']))

    self.assertEqual(
        table_data.rows,
        [[3, 'california', 89 + 99 + 293, (321.0 + 231.0 + 12.0) / 3.0],
         [2, 'maine\'s', 293 + 932, (32.0 + 48.0) / 2.0],
         [1, 'oregon', 32, 33]])

  def testTotalsSliceTableGeneration(self):
    """Test that slice tables are generated correctly with total values."""
    table_data = self.data_source_obj.GetTableData(
        data_source.QueryParameters(
            data_source.QueryParameters.SLICE_QUERY,
            ['category1', 'metric1', 'metric2', 'metric3']))

    self.assertEqual(
        table_data.rows,
        [['red', 21 + 33, (98.0 + 90.0) / 2.0, 2]])


class CSVSourcesErrorTests(unittest.TestCase):
  """Tests of a CSV DataSource object for error cases."""

  def setUp(self):
    pass

  def testBadHeaderKey(self):
    """Test that unknown key in header generates error."""
    csv_file = StringIO.StringIO(
        'date[unknown_key=unknown_value],metric\n1990,23232')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testBadDataType(self):
    """Test that unknown type value generates error."""
    csv_file = StringIO.StringIO('date[type=unknown_type],metric\n1990,23232')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testBadAggregation(self):
    """Test that unknown aggregation operator generates error."""
    csv_file = StringIO.StringIO(
        'date[aggregation=unknown_aggregation],metric\n1990,23232')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testBadSliceRoleKey(self):
    """Test that unknown value for slice_role generates error."""
    csv_file = StringIO.StringIO(
        'date[slice_role=unknown_role],metric\n1990,23232')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testBadColumnID(self):
    """Test that a badly formatted column ID generates error."""
    csv_file = StringIO.StringIO('my date[type=date],metric\n1990,23232')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testBadDataRow(self):
    """Test that row with wrong number of entries causes error."""
    csv_file = StringIO.StringIO(
        'date,column\n01/01/1990,abcd,1234')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testBadParentReference(self):
    """Test that illegal parent reference causes error."""
    csv_file = StringIO.StringIO(
        'date,column[parent=unknown_parent]\n01/01/1990,abcd')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()

  def testMultipleParents(self):
    """Test that having multiple parent instances causes error."""
    csv_file = StringIO.StringIO(
        'date,column1[parent=column2],column2,column3\n'
        '1/1/2001,val1,parent1,323\n1/2/2001,val1,parent2,123')

    self.assertRaises(
        data_source.DataSourceError,
        self.data_source_class,
        csv_file, False)

    csv_file.close()
