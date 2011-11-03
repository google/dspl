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

"""Implementation of a CSV data source.

Assumes that the parameters for each column are encoded in the header row as
follows:

column1_id[key1=value1;key2=value2;key3=value3;....],column2_id[...],...

Implements all of the necessary aggregation, sorting, etc. by using in-memory
Python objects.
"""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import csv
import itertools
import string

import csv_utilities
import data_source


class DataContainer(object):
  """Object that stores tabular data and executes queries on these data."""

  # Mapping from CSV column aggregation types to Python functions
  AGGREGATOR_FUNCTIONS = {
      'sum': sum,
      'max': max,
      'min': min,
      'avg': lambda r: sum(r) / float(len(r)),
      'count': len
  }

  def __init__(self, column_names):
    """Create a new DataContainer object.

    Args:
      column_names: A sequence of strings, representing the names of the columns
                    for this data container
    """
    self.column_names = column_names
    self.column_position_map = {}

    for column_index, column_name in enumerate(column_names):
      self.column_position_map[column_name] = column_index

    self.position_column_map = {}

    for column_name, column_index in self.column_position_map.items():
      self.position_column_map[column_index] = column_name

    self.rows = []

  def AddRow(self, row):
    """Add a new row to this data container object.

    Args:
      row: A sequence of values for the row
    """
    self.rows.append(row)

  def DistinctValues(self, column_names, omit_values=dict()):
    """Get the distinct combination of values for one or more columns.

    Args:
      column_names: List of columns to include
      omit_values: Dictionary of column->value mappings; rows where
                   the column has one of the given values are omitted

    Returns:
      A list of lists, one for each set of unique values of the input columns
    """
    observed_values = {}

    for row in self.rows:
      curr_values = []

      keep_row = True

      for column_name in column_names:
        curr_value = row[self.column_position_map[column_name]]

        # Drop rows with values in the omitted list
        if column_name in omit_values:
          if curr_value in omit_values[column_name]:
            keep_row = False
            break

        curr_values.append(row[self.column_position_map[column_name]])

      if keep_row:
        observed_values[tuple(curr_values)] = True

    return sorted([list(key) for key in observed_values.keys()])

  def CombinationCount(self, child_column, parent_column, omit_values=dict()):
    """Get the number of unique parent values associated with each child.

    Args:
      child_column: String representing child column
      parent_column: String representing parent column
      omit_values: Dictionary of column->value mappings; rows where
                   the column has one of the given values are omitted

    Returns:
      A list of lists. Each of the latter contains two elements: (1) the string
      value of the child concept, and (2) the number of distinct parent values
      associated with the child value in the table.
    """
    # Filter rows out based on omit_values parameter
    filtered_rows = []

    for row in self.rows:
      drop_row = False

      for column_id in omit_values.keys():
        column_position = self.column_position_map[column_id]

        if row[column_position] in omit_values[column_id]:
          drop_row = True
          break

      if not drop_row:
        filtered_rows.append(row)

    group_key_function = lambda r: r[self.column_position_map[child_column]]

    input_data = sorted(filtered_rows, key=group_key_function)

    result_rows = []

    for key, group in itertools.groupby(input_data, group_key_function):
      curr_row = []

      group_list = list(group)

      parent_values = {}

      curr_row.append(key)

      for row in group_list:
        parent_values[row[self.column_position_map[parent_column]]] = True

      curr_row.append(len(parent_values))
      result_rows.append(curr_row)

    return result_rows

  def GroupedValues(self, column_names, group_by_columns, order_by_columns,
                    column_aggregation_map,
                    keep_values=dict(), omit_values=dict()):
    """Get aggregated values grouped and sorted according to arguments.

    Roughly equivalent to running: 

    SELECT [column_names] FROM [table]
    WHERE [keep_value(key) = keep_value(value),
           omit_values(key) != omit_values(value)]
    GROUP BY [group_by_columns] ORDER BY [order_by_columns]

    including the aggregations from the column_aggregation_map as necessary.

    Args:
      column_names: List of strings representing columns to include in query
      group_by_columns: Subset of column_names to be used for grouping
      order_by_columns: Subset of column_names to be used for sorting
      column_aggregation_map: Mapping from column names to aggregator functions;
                              used to aggregate values in each group
      keep_values: Dictionary of column->value mappings; any rows containing
                   other values of these columns will be dropped
      omit_values: Dictionary of column->value mappings; rows containing these
                   values will be dropped

    Returns:
      List of lists containing results of running the query
    """
    # Drop or keep rows based on contents of keep_values and/or omit_values
    # parameters
    filtered_rows = []

    if keep_values or omit_values:
      for row in self.rows:
        keep_row_hit = False
        omit_row_hit = False

        for column_id in keep_values.keys():
          column_position = self.column_position_map[column_id]

          if row[column_position] in keep_values[column_id]:
            keep_row_hit = True
        for column_id in omit_values.keys():
          column_position = self.column_position_map[column_id]

          if row[column_position] in omit_values[column_id]:
            omit_row_hit = True

        if (not omit_row_hit) and (not keep_values or keep_row_hit):
          filtered_rows.append(row)
    else:
      filtered_rows = self.rows

    group_key_function = lambda r: tuple(
        [r[self.column_position_map[col]] for col in group_by_columns])
    sort_key_function = lambda r: tuple(
        [r[column_names.index(col)] for col in order_by_columns])

    input_data = sorted(filtered_rows, key=group_key_function)

    result_rows = []

    for unused_key, group in itertools.groupby(input_data, group_key_function):
      curr_row = []

      group_list = list(group)

      for column_name in column_names:
        if column_name in group_by_columns:
          curr_row.append(group_list[0][self.column_position_map[column_name]])
        else:
          group_values = []

          for row in group_list:
            group_values.append(row[self.column_position_map[column_name]])

          curr_row.append(
              DataContainer.AGGREGATOR_FUNCTIONS[
                  string.lower(
                      column_aggregation_map[column_name])](group_values))

      result_rows.append(curr_row)

    return sorted(result_rows, key=sort_key_function)


class CSVDataSource(data_source.DataSource):
  """A DataSource around a single CSV file."""

  def __init__(self, csv_file, verbose=True):
    """Populate a CSVDataSource object based on a CSV file.

    Note that the caller is responsible for closing the csv_file.

    Args:
      csv_file: A file-like object, opened for reading, that has CSV data in it
      verbose: Print out status messages to stdout

    Raises:
      DataSourceError: If CSV isn't properly formatted
    """
    self.verbose = verbose
    self.column_bundle = csv_utilities.ConstructColumnBundle(csv_file, verbose)

    column_ids = [column.column_id for column in
                  self.column_bundle.GetColumnIterator()]
    num_columns = self.column_bundle.GetNumColumns()
    self.data_container = DataContainer(column_ids)

    if self.verbose:
      print 'Reading CSV data'

    body_csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    body_csv_reader.next()

    for r, row in enumerate(body_csv_reader):
      transformed_row_values = []

      # Ignore blank rows
      if row:
        if len(row) != num_columns:
          raise data_source.DataSourceError(
              'Number of columns in row %d (%d) does not match number '
              'expected (%d)' %  (r + 2, len(row), num_columns))

        skip_row = False

        for v, row_value in enumerate(row):
          column = self.column_bundle.GetColumnByOrder(v)

          # Handle dropif_val and zeroif_val parameters
          if 'dropif_val' in column.internal_parameters:
            if row_value == column.internal_parameters['dropif_val']:
              skip_row = True
              break
          elif 'zeroif_val' in column.internal_parameters:
            if row_value == column.internal_parameters['zeroif_val']:
              row_value = 0.0

          if column.data_type == 'integer':
            typed_row_value = int(row_value)
          elif column.data_type == 'float':
            typed_row_value = float(row_value)
          else:
            typed_row_value = row_value

          transformed_row_values.append(typed_row_value)

        if skip_row:
          continue

        self.data_container.AddRow(transformed_row_values)

    if self.verbose:
      print 'Checking concept hierarchies'

    self._CheckHierarchies()

  def GetColumnBundle(self):
    """Get ColumnBundle object for this data source."""
    return self.column_bundle

  def _CheckHierarchies(self):
    """Make sure that each concept instance has no more than one parent."""
    for column in self.column_bundle.GetColumnIterator():
      total_vals = {}

      if column.parent_ref:
        # Do not count total values as instances
        if column.total_val:
          total_vals[column.column_id] = column.total_val

        if self.column_bundle.GetColumnByID(column.parent_ref).total_val:
          total_vals[column.parent_ref] = (
              self.column_bundle.GetColumnByID(column.parent_ref).total_val)

        combination_count = self.data_container.CombinationCount(
            column.column_id, column.parent_ref, total_vals)
        error_values = []

        for row in combination_count:
          if row[1] > 1:
            error_values.append(row[0])

        if error_values:
          raise data_source.DataSourceError(
              'Instances of column %s have multiple parent values: %s' %
              (column.column_id, error_values))

  def GetTableData(self, query_parameters):
    """Calculate and return the requested table data.

    Use in-memory data container to group and aggregate the raw data from the
    original CSV.

    Args:
      query_parameters: A QueryParameters object

    Returns:
      A TableData object containing the data for the requested table

    Raises:
      DataSourceError: If query against sqlite instance fails
    """
    if query_parameters.query_type == data_source.QueryParameters.CONCEPT_QUERY:
      omitted_values = {}

      # Pull out total values
      for column_id in query_parameters.column_ids:
        column = self.column_bundle.GetColumnByID(column_id)

        if column.total_val:
          omitted_values[column_id] = [column.total_val]

      query_results = self.data_container.DistinctValues(
          query_parameters.column_ids, omitted_values)
    elif query_parameters.query_type == data_source.QueryParameters.SLICE_QUERY:
      # This request is for a slice table
      all_columns = []

      dimension_columns = []
      time_dimension_id = ''
      metric_columns = []
      metric_aggregation_map = {}

      query_total_vals = {}

      # Construct a SQL query that selects all parameters (with the necessary
      # aggregations), groups by non-time dimensions, and orders by all the
      # dimensions, with time last.
      for column_id in query_parameters.column_ids:
        column = self.column_bundle.GetColumnByID(column_id)

        all_columns.append(column_id)

        if column.slice_role == 'dimension':
          dimension_columns.append(column_id)

          if column.data_type == 'date':
            time_dimension_id = column_id
        elif column.slice_role == 'metric':
          metric_columns.append(column_id)
          metric_aggregation_map[column_id] = (
              column.internal_parameters['aggregation'])

        if column.total_val:
          query_total_vals[column.column_id] = column.total_val

      order_by_columns = (
          [d for d in dimension_columns if d != time_dimension_id])

      if time_dimension_id:
        order_by_columns.append(time_dimension_id)

      # Calculate the rows to filter out based on totals
      aggregated_total_vals = {}

      for column in self.column_bundle.GetColumnIterator():
        if column.column_id not in query_parameters.column_ids:
          if column.total_val:
            aggregated_total_vals[column.column_id] = column.total_val

      query_results = self.data_container.GroupedValues(
          all_columns,
          dimension_columns, order_by_columns,
          metric_aggregation_map,
          aggregated_total_vals,
          query_total_vals)
    else:
      raise data_source.DataSourceError(
          'Unknown query type: %s' % query_parameters.query_type)

    return data_source.TableData(rows=query_results)

  def Close(self):
    """Close this data source."""
    pass
