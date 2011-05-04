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

"""Tests of data_source_to_dspl module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import unittest

import data_source
import data_source_to_dspl


class _MockDataSource(data_source.DataSource):
  """A fake DataSource, for testing purposes."""

  def __init__(self, data_source_identifier, verbose=True):
    pass

  def GetColumnBundle(self):
    column1 = data_source.DataSourceColumn(
        'col1', data_type='string', slice_role='dimension',
        concept_extension='entity:entity', rollup=True)
    column2 = data_source.DataSourceColumn(
        'col2', data_type='string', slice_role='dimension', parent_ref='col6')
    column3 = data_source.DataSourceColumn(
        'col3', data_type='date', concept_ref='time:year', data_format='yyyy',
        slice_role='dimension')
    column4 = data_source.DataSourceColumn(
        'col4', data_type='float', slice_role='metric')
    column5 = data_source.DataSourceColumn(
        'col5', data_type='integer', slice_role='metric')
    column6 = data_source.DataSourceColumn(
        'col6', data_type='string', slice_role='dimension', rollup=True)

    return data_source.DataSourceColumnBundle(
        columns=[column1, column2, column3, column4, column5, column6])

  def GetTableData(self, query_parameters):
    if query_parameters.column_ids == ('col1',):
      return data_source.TableData(rows=[['blue'], ['green'], ['red']])
    elif query_parameters.column_ids == ('col2',):
      return data_source.TableData(rows=[['california'], ['maine'], ['oregon']])
    elif query_parameters.column_ids == ('col6',):
      return data_source.TableData(rows=[['east'], ['west']])
    elif query_parameters.column_ids == ('col2', 'col6'):
      return data_source.TableData(rows=[['california', 'west'],
                                         ['maine', 'east'], ['oregon', 'west']])
    else:
      data_columns = []

      for column_id in query_parameters.column_ids:
        if column_id == 'col1':
          data_columns.append(['blue', 'blue', 'green', 'red'])
        elif column_id == 'col2':
          data_columns.append(['california', 'california', 'maine', 'oregon'])
        elif column_id == 'col3':
          data_columns.append(['1989', '1990', '1991', '1992'])
        elif column_id == 'col4':
          data_columns.append(['1.2', '1.3', '1.4', '1.5'])
        elif column_id == 'col5':
          data_columns.append(['4', '5', '6', '7'])
        elif column_id == 'col6':
          data_columns.append(['west', 'west', 'east', 'west'])

      # Transpose rows and columns so that table is properly set up
      return data_source.TableData([list(r) for r in zip(*data_columns)])

  def Close(self):
    pass


class CalculateSlicesTests(unittest.TestCase):
  """Tests of _CalculateSlices function."""

  def setUp(self):
    pass

  def testCalculateSlices(self):
    """Test of _CalculateSlices with powersets."""
    column1 = data_source.DataSourceColumn(
        'col1', rollup=True, concept_extension='entity:entity')
    column2 = data_source.DataSourceColumn('col2', rollup=False)
    column3 = data_source.DataSourceColumn('col3', rollup=True)
    column4 = data_source.DataSourceColumn(
        'col4', rollup=True, parent_ref='col3')

    column_bundle = data_source.DataSourceColumnBundle(
        columns=[column1, column2, column3, column4])

    slice_column_sets = data_source_to_dspl._CalculateSlices(column_bundle)

    # Convert columns to id strings
    slice_column_ids = []

    for slice_column_set in slice_column_sets:
      slice_column_ids.append([c.column_id for c in slice_column_set])

    # Sort the actual and expected results so that the test is not order
    # dependent
    self.assertEqual(
        sorted([sorted(s) for s in slice_column_ids]),
        sorted([sorted(s) for s in [['col1', 'col2', 'col3'],
                                    ['col1', 'col2', 'col4'],
                                    ['col1', 'col2'], ['col2', 'col3'],
                                    ['col2', 'col4'], ['col2']]]))


class PopulateDatasetTest(unittest.TestCase):
  """Tests of PopulateDataset functionality."""

  def setUp(self):
    self.dataset = data_source_to_dspl.PopulateDataset(
        _MockDataSource(None), verbose=False)

  def testDatasetImports(self):
    """Test that the dataset imports are properly created."""
    # Sort so that the test results aren't sensitive to ordering
    sorted_imports = sorted(self.dataset.imports, key=lambda i: i.namespace_id)

    self.assertEqual(
        [i.namespace_id for i in sorted_imports],
        ['entity', 'geo', 'geo_us', 'quantity', 'time', 'unit'])
    self.assertEqual(
        [i.namespace_url for i in sorted_imports],
        ['http://www.google.com/publicdata/dataset/google/entity',
         'http://www.google.com/publicdata/dataset/google/geo',
         'http://www.google.com/publicdata/dataset/google/geo/us',
         'http://www.google.com/publicdata/dataset/google/quantity',
         'http://www.google.com/publicdata/dataset/google/time',
         'http://www.google.com/publicdata/dataset/google/unit'])

  def testDatasetConcepts(self):
    """Test that the dataset concepts are properly created."""
    # Sort so that the test results aren't sensitive to ordering
    sorted_concepts = sorted(self.dataset.concepts, key=lambda c: c.concept_id)

    self.assertEqual(
        [c.concept_id for c in sorted_concepts],
        ['col1', 'col2', 'col4', 'col5', 'col6', 'time:year'])

    self.assertEqual(
        [c.data_type for c in sorted_concepts],
        ['string', 'string', 'float', 'integer', 'string', 'date'])

    self.assertEqual(
        [c.table_ref for c in sorted_concepts],
        ['col1_table', 'col2_table', '', '', 'col6_table', ''])

    self.assertEqual(
        [c.concept_extension_reference for c in sorted_concepts],
        ['entity:entity', '', '', '', '', ''])

    self.assertEqual(
        [c.concept_reference for c in sorted_concepts],
        ['', '', '', '', '', 'time:year'])

  def testDatasetSlices(self):
    """Test that the dataset slices are properly created."""
    # Slice ids are based on order, so no need to sort here
    self.assertEqual(
        [s.slice_id for s in self.dataset.slices],
        ['slice_0', 'slice_1'])

    self.assertEqual(
        [s.table_ref for s in self.dataset.slices],
        ['slice_0_table', 'slice_1_table'])

    self.assertEqual(
        [s.dimension_map for s in self.dataset.slices],
        [{'time:year': 'col3'}, {'time:year': 'col3'}])

    # Test dimensions in an order-independent way
    self.assertEqual(
        sorted([
            sorted(self.dataset.slices[0].dimension_refs),
            sorted(self.dataset.slices[1].dimension_refs)]),
        [['col1', 'col2', 'time:year'], ['col2', 'time:year']])

    # Test metrics in an order-independent way
    self.assertEqual(
        [sorted(self.dataset.slices[0].metric_refs),
         sorted(self.dataset.slices[1].metric_refs)],
        [['col4', 'col5'], ['col4', 'col5']])

    # Test that dimension maps are set up appropriately
    self.assertEqual(self.dataset.slices[0].dimension_map,
                     {'time:year': 'col3'})
    self.assertEqual(self.dataset.slices[1].dimension_map,
                     {'time:year': 'col3'})

  def testDatasetTables(self):
    """Test that the dataset tables are properly created."""
    # Sort tables so that test results aren't dependent on order
    sorted_tables = sorted(self.dataset.tables, key=lambda t: t.table_id)

    self.assertEqual(
        [t.table_id for t in sorted_tables],
        ['col1_table', 'col2_table', 'col6_table',
         'slice_0_table', 'slice_1_table'])

    self.assertEqual(
        [t.file_name for t in sorted_tables],
        ['col1_table.csv', 'col2_table.csv', 'col6_table.csv',
         'slice_0_table.csv', 'slice_1_table.csv'])

    # Map tables to what concepts they have in them
    col1_table = sorted_tables[0]
    col2_table = sorted_tables[1]
    col6_table = sorted_tables[2]

    if len(sorted_tables[3].columns) == 5:
      col1_to_col5_table = sorted_tables[3]
      col2_to_col5_table = sorted_tables[4]
    else:
      col1_to_col5_table = sorted_tables[4]
      col2_to_col5_table = sorted_tables[3]

    # Do in-depth tests of each table
    self._TableColumnTestHelper(
        col1_table,
        expected_ids=['col1', 'name'],
        expected_types=['string', 'string'],
        expected_formats=['', ''],
        expected_data={'col1': ['col1', 'blue', 'green', 'red'],
                       'name': ['name', 'blue', 'green', 'red']})

    self._TableColumnTestHelper(
        col2_table,
        expected_ids=['col2', 'col6'],
        expected_types=['string', 'string'],
        expected_formats=['', ''],
        expected_data={'col2': ['col2', 'california', 'maine', 'oregon'],
                       'col6': ['col6', 'west', 'east', 'west']})

    self._TableColumnTestHelper(
        col6_table,
        expected_ids=['col6'],
        expected_types=['string'],
        expected_formats=[''],
        expected_data={'col6': ['col6', 'east', 'west']})

    self._TableColumnTestHelper(
        col1_to_col5_table,
        expected_ids=['col1', 'col2', 'col3', 'col4', 'col5'],
        expected_types=['string', 'string', 'date', 'float', 'integer'],
        expected_formats=['', '', 'yyyy', '', ''],
        expected_data={'col1': ['col1', 'blue', 'blue', 'green', 'red'],
                       'col2': ['col2', 'california', 'california', 'maine',
                                'oregon'],
                       'col3': ['col3', '1989', '1990', '1991', '1992'],
                       'col4': ['col4', '1.2', '1.3', '1.4', '1.5'],
                       'col5': ['col5', '4', '5', '6', '7']})

    self._TableColumnTestHelper(
        col2_to_col5_table,
        expected_ids=['col2', 'col3', 'col4', 'col5'],
        expected_types=['string', 'date', 'float', 'integer'],
        expected_formats=['', 'yyyy', '', ''],
        expected_data={'col2': ['col2', 'california', 'california', 'maine',
                                'oregon'],
                       'col3': ['col3', '1989', '1990', '1991', '1992'],
                       'col4': ['col4', '1.2', '1.3', '1.4', '1.5'],
                       'col5': ['col5', '4', '5', '6', '7']})

  def _TableColumnTestHelper(self, table, expected_ids=(), expected_types=(),
                             expected_formats=(), expected_data=dict()):
    """Help test contents of a single DSPL table object."""
    # Sort the columns so the test results aren't order dependent
    sorted_table_columns = sorted(
        table.columns, key=lambda c: c.column_id)

    self.assertEqual(
        [c.column_id for c in sorted_table_columns],
        expected_ids)

    self.assertEqual(
        [c.data_type for c in sorted_table_columns],
        expected_types)

    self.assertEqual(
        [c.data_format for c in sorted_table_columns],
        expected_formats)

    # Transpose data table so we can look at the data by columns
    transposed_table_data = [list(r) for r in zip(*table.table_data)]

    self.assertEqual(len(transposed_table_data), len(table.columns))

    for c, column in enumerate(table.columns):
      self.assertEqual(
          transposed_table_data[c],
          expected_data[column.column_id])


if __name__ == '__main__':
  unittest.main()
