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

"""Utility functions useful for CSV data sources."""

__author__ = 'Benjamin Yolken <yolken@google.com>'


import csv
import re
import string
import warnings

import data_source


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
      elif key == 'parent':
        column.parent_ref = value
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


def ConstructColumnBundle(csv_file, verbose=True):
  """Construct a ColumnBundle from the header information in a CSV file.

  Args:
    csv_file: The complete string for the column header
    verbose: Print out extra information to stdout

  Returns:
    A data_source.ColumnBundle object populated based on the CSV header

  Raises:
    DataSourceError: If there are any parsing errors or data
                     inconsistencies
  """
  # Get the first and second rows of the CSV
  header_csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
  header_row_values = header_csv_reader.next()
  second_row_values = header_csv_reader.next()
  csv_file.seek(0)

  # Check that second row is properly formatted
  if len(header_row_values) != len(second_row_values):
    raise data_source.DataSourceError(
        'Number of columns in row 2 (%d) does not match number '
        'expected (%d)' %  (len(second_row_values), len(header_row_values)))

  column_bundle = data_source.DataSourceColumnBundle()

  for header_element in header_row_values:
    column_bundle.AddColumn(_HeaderToColumn(header_element))

  num_date_columns = 0
  has_metric_column = False
  column_ids = [column.column_id for column in
                column_bundle.GetColumnIterator()]

  # Iterate through columns, populating and refining DataSourceColumn
  # parameters as necessary
  for c, column in enumerate(column_bundle.GetColumnIterator()):
    if verbose:
      print '\nEvaluating column %s' % column.column_id

    # Check data type
    if not column.data_type:
      column.data_type = (
          data_source.GuessDataType(second_row_values[c], column.column_id))

      if verbose:
        print 'Guessing that column %s is of type %s' % (
            column.column_id, column.data_type)

    # Check slice type
    if not column.slice_role:
      if column.data_type == 'integer' or column.data_type == 'float':
        column.slice_role = 'metric'
      else:
        column.slice_role = 'dimension'

      if verbose:
        print 'Guessing that column %s is a %s' % (
            column.column_id, column.slice_role)

    # Check aggregation
    if column.slice_role == 'metric':
      has_metric_column = True

      if 'aggregation' not in column.internal_parameters:
        column.internal_parameters['aggregation'] = 'SUM'

        if verbose:
          print 'Guessing that column %s should be aggregated by %s' % (
              column.column_id, column.internal_parameters['aggregation'])

    # Check parent
    if column.parent_ref:
      if column.parent_ref not in column_ids:
        raise data_source.DataSourceError(
            'Column %s references a parent not defined in this dataset: %s' %
            (column.column_id, column.parent_ref))

      parent_column = column_bundle.GetColumnByID(column.parent_ref)

      if not parent_column.rollup:
        parent_column.rollup = True

        if verbose:
          print ('Making column %s rollup since it is a parent to column %s'
                 % (parent_column.column_id, column.column_id))

    # Check date format and concept
    if column.data_type == 'date':
      num_date_columns += 1

      if not column.data_format:
        column.data_format = (
            data_source.GuessDateFormat(second_row_values[c]))

      if not column.concept_ref:
        column.concept_ref = (
            data_source.GuessDateConcept(column.data_format))

      if verbose:
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

  return column_bundle
