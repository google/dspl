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

A local, in-memory sqlite instance is used to aggregate and filter the data as
required by the DataSource interface.
"""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import csv
import re
import sqlite3
import string
import warnings

import data_source


# Mapping from DSPL to sqlite data types
_DSPL_TYPE_TO_SQLITE_TYPE = {
    'string': 'text',
    'integer': 'integer',
    'float': 'real',
    'date': 'text',
    'boolean': 'text'}


def _HeaderToColumn(header_string):
  """Parse the header string for a column.

  Args:
    header_string: The complete string for the column header

  Returns:
    A DataColumn object populated based on the header data

  Raises:
    DataSourceError: If there are any errors in parsing, e.g. if an unrecognized
                     key is found.
  """
  # The column id must be at least one character long, and cannot contain the
  # characters '[', ']', ';', or whitespace
  parameters_match = re.match(
      '^([^\]\[;\s]+)(?:\[(.*)\]){0,1}$',
      header_string.strip().replace('"', ''))

  if not parameters_match:
    raise data_source.DataSourceError(
        'Formatting error for header string: %s' % header_string)

  column_id = parameters_match.group(1)
  column = data_source.DataSourceColumn(column_id, internal_parameters={})

  if parameters_match.group(2):
    # Parse the column parameters
    key_value_pairs = parameters_match.group(2).split(';')

    for key_value_pair in key_value_pairs:
      try:
        [key, value] = key_value_pair.split('=')
      except ValueError:
        raise data_source.DataSourceError(
            'Formatting error for header string: %s' % header_string)      

      # Map the key to the appropriate field of the DataSourceColumn object
      if key == 'type':
        if value not in ['date', 'float', 'integer', 'string']:
          raise data_source.DataSourceError(
              'Unknown data type for column %s: %s' %
              (column.column_id, value))

        column.data_type = value
      elif key == 'format':
        column.data_format = value
      elif key == 'concept':
        column.concept_ref = value
      elif key == 'extends':
        column.concept_extension = value
      elif key == 'slice_role':
        role_value = value.lower()

        if role_value not in ['dimension', 'metric']:
          raise data_source.DataSourceError(
              'Unrecognized slice_roll in column %s: %s' %
              (column.column_id, value))
        else:
          column.slice_role = role_value
      elif key == 'rollup':
        if value.lower() == 'true':
          column.rollup = True
        elif value.lower() == 'false':
          column.rollup = False
        else:
          raise data_source.DataSourceError(
              'Unrecognized boolean value in column %s: %s' %
              (column.column_id, value))
      elif key == 'dropif':
        column.internal_parameters['dropif_val'] = value
      elif key == 'zeroif':
        column.internal_parameters['zeroif_val'] = value
      elif key == 'aggregation':
        if string.lower(value) not in ['sum', 'max', 'min', 'avg', 'count']:
          raise data_source.DataSourceError(
              'Unknown aggregation for column %s: %s' %
              (column.column_id, value))

        column.internal_parameters['aggregation'] = value
      else:
        raise data_source.DataSourceError(
            'Unknown parameter for column %s: %s' %
            (column.column_id, key))
  return column


def _CleanDBValue(value, data_type):
  """Clean the argument value for import into sqlite.

  TODO(yolken): Make this more sophisticated, particularly for integer and
                float values.

  Args:
    value: A value from the table
    data_type: The DSPL data type for the value

  Returns:
    A cleaned value that will be accepted by sqlite
  """
  cleaned_value = value.strip()

  if data_type == 'string' or data_type == 'date':
    # Escape single quotes
    cleaned_value = cleaned_value.replace('\'', '\'\'')

    # Add quotation marks around value
    return '\'%s\'' % cleaned_value
  elif data_type == 'integer' or data_type == 'float':
    # Remove dollar symbols
    return re.sub('[\$\,]', '', cleaned_value)
  else:
    return cleaned_value


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

    # Get the first and second rows of the CSV
    header_csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    header_row_values = header_csv_reader.next()
    second_row_values = header_csv_reader.next()
    csv_file.seek(0)

    self.column_bundle = data_source.DataSourceColumnBundle()

    for header_element in header_row_values:
      self.column_bundle.AddColumn(_HeaderToColumn(header_element))

    num_columns = self.column_bundle.GetNumColumns()
    num_date_columns = 0
    has_metric_column = False

    # Iterate through columns, populating and refining DataSourceColumn
    # parameters as necessary
    for c, column in enumerate(self.column_bundle.GetColumnIterator()):
      if self.verbose:
        print '\nEvaluating column %s' % column.column_id

      # Check data type
      if not column.data_type:
        column.data_type = (
            data_source.GuessDataType(second_row_values[c]))

        if self.verbose:
          print 'Guessing that column %s is of type %s' % (
              column.column_id, column.data_type)

      # Check slice type
      if not column.slice_role:
        if column.data_type == 'integer' or column.data_type == 'float':
          column.slice_role = 'metric'
        else:
          column.slice_role = 'dimension'

        if self.verbose:
          print 'Guessing that column %s is a %s' % (
              column.column_id, column.slice_role)

      # Check aggregation
      if column.slice_role == 'metric':
        has_metric_column = True

        if 'aggregation' not in column.internal_parameters:
          column.internal_parameters['aggregation'] = 'SUM'

          if self.verbose:
            print 'Guessing that column %s should be aggregated by %s' % (
                column.column_id, column.internal_parameters['aggregation'])

      # Check date format and concept
      if column.data_type == 'date':
        num_date_columns += 1

        if not column.data_format:
          column.data_format = (
              data_source.GuessDateFormat(second_row_values[c]))

        if not column.concept_ref:
          column.concept_ref = (
              data_source.GuessDateConcept(column.data_format))

        if self.verbose:
          print ('Guessing that column %s is formatted as %s and '
                 'corresponds to %s' % (
                     column.column_id, column.data_format, column.concept_ref))

    # Warn user if their file will not produce interesting DSPL visualizations
    if num_date_columns == 0:
      warnings.warn('Input file does not have a date column',
                    data_source.DataSourceWarning)

    elif num_date_columns > 1:
      warnings.warn('Input file has more than one date column',
                    data_source.DataSourceWarning)

    if not has_metric_column:
      warnings.warn('Input file does not have any metrics',
                    data_source.DataSourceWarning)

    # Set up sqlite table to store data
    columns_string = (
        ','.join(
            ['%s %s' % (column.column_id,
                        _DSPL_TYPE_TO_SQLITE_TYPE[column.data_type])
             for column in self.column_bundle.GetColumnIterator()]))

    if self.verbose:
      print '\nCreating sqlite3 table: %s' % (columns_string)

    self.sqlite_connection = sqlite3.connect(':memory:')
    cursor = self.sqlite_connection.cursor()
    cursor.execute('create table csv_table (%s)' % (columns_string))

    if self.verbose:
      print 'Adding CSV data to SQLite table'

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
              row_value = '0'

          transformed_row_values.append(
              _CleanDBValue(
                  row_value, column.data_type))

        if skip_row:
          continue

        # Add row to sqlite table
        transformed_values_str = ','.join(transformed_row_values)

        try:
          cursor.execute('insert into csv_table values (%s)' %
                         (transformed_values_str))
        except sqlite3.OperationalError as e:
          raise data_source.DataSourceError(
              'Error putting line %d of input file into database: %s'
              '\n%s' % (r + 2, transformed_values_str, str(e)))

    if self.verbose:
      print 'Committing transactions\n'

    self.sqlite_connection.commit()

    cursor.close()

  def GetColumnBundle(self):
    """Get ColumnBundle object for this data source."""
    return self.column_bundle

  def GetTableData(self, query_parameters):
    """Calculate and return the requested table data.

    Uses sqlite to group and aggregate the raw data from the original CSV.

    Args:
      query_parameters: A QueryParameters object

    Returns:
      A TableData object containing the data for the requested table

    Raises:
      DataSourceError: If query against sqlite instance fails
    """
    if len(query_parameters.column_ids) == 1:
      # This request is for a concept definition table
      query_str = (
          'SELECT DISTINCT %s FROM csv_table ORDER BY %s' %
          (query_parameters.column_ids[0], query_parameters.column_ids[0]))
    else:
      # This request is for a slice table
      sql_names = []
      dimension_sql_names = []

      time_dimension_id = ''

      # Construct a SQL query that selects all parameters (with the necessary
      # aggregations), groups by non-time dimensions, and orders by all the
      # dimensions, with time last.
      for column_id in query_parameters.column_ids:
        column = self.column_bundle.GetColumnByID(column_id)

        if column.slice_role == 'dimension':
          sql_names.append(column_id)
          dimension_sql_names.append(column_id)

          if column.data_type == 'date':
            time_dimension_id = column_id
        elif column.slice_role == 'metric':
          sql_names.append(
              '%s(%s) AS %s' % (column.internal_parameters['aggregation'],
                                column_id, column_id))

      order_sql_names = (
          [d for d in dimension_sql_names if d != time_dimension_id])

      if time_dimension_id:
        order_sql_names.append(time_dimension_id)

      query_str = (
          'SELECT %s FROM csv_table GROUP BY %s ORDER BY %s' %
          (','.join(sql_names),
           ','.join(dimension_sql_names),
           ','.join(order_sql_names)))

    if self.verbose:
      print 'Executing query:\n%s\n' % (query_str)

    # Execute the query against the sqlite backend
    cursor = self.sqlite_connection.cursor()

    try:
      cursor.execute(query_str)
    except sqlite3.OperationalError as e:
      raise data_source.DataSourceError(
          'Error executing query: %s\n%s' % (query_str, str(e)))

    query_results = []

    for row in cursor:
      query_results.append(list(row))

    cursor.close()

    return data_source.TableData(rows=query_results)

  def Close(self):
    """Close this data source."""
    self.sqlite_connection.close()
