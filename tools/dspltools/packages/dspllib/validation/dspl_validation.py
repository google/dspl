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

"""Validate a DSPL dataset model."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import re


class DSPLValidationIssue(object):
  """Object that records a single potential import issue in a dataset."""

  # Issue scopes
  GENERAL = 0
  CONCEPT = 1
  SLICE = 2
  TABLE = 3
  DATA = 4

  # Issue types
  MISSING_INFO = 100
  REPEATED_INFO = 101
  BAD_REFERENCE = 102
  INCONSISTENCY = 103
  OTHER = 104

  def __init__(self, issue_scope, issue_type, base_entity_id, message):
    """Create a new DSPLValidationIssue object.

    Args:
      issue_scope: Scope of this issue; value must be from class enum above
      issue_type: Issue type; value must be from class enum above
      base_entity_id: String id of DSPL entity where issue is found
      message: Human-readable description of the issue
    """
    self.issue_scope = issue_scope
    self.issue_type = issue_type
    self.base_entity_id = base_entity_id
    self.message = message

  def __str__(self):
    return self.message


class DSPLDatasetValidator(object):
  """Object for validating a DSPL dataset model."""

  def __init__(self, dspl_dataset, full_data_check=True):
    """Create a new DSPLDatasetValidator object.

    Args:
      dspl_dataset: An instance of dspllib.model.dspl_model.DataSet
      full_data_check: Boolean indicating whether validator should look through
                       CSV data
    """
    self.dspl_dataset = dspl_dataset
    self.full_data_check = full_data_check

    self.issues = []

  def AddIssue(self, new_issue):
    """Add a new issue to this validation instance.

    Args:
      new_issue: An instance of DSPLValidationIssue
    """
    self.issues.append(new_issue)

  def GetIssues(self):
    """Return list of stored issues."""
    return self.issues

  def SortIssues(self):
    """Sort the issues in the same order as they appear in the dataset."""
    entity_ids = [None]

    for concept in self.dspl_dataset.concepts:
      entity_ids.append(concept.concept_id)

    for data_slice in self.dspl_dataset.slices:
      entity_ids.append(data_slice.slice_id)

    for table in self.dspl_dataset.tables:
      entity_ids.append(table.table_id)

    self.issues.sort(key=lambda r: entity_ids.index(r.base_entity_id))

  def CheckConcepts(self):
    """Check for issues related to the concepts in this dataset."""
    if not self.dspl_dataset.concepts:
      self.AddIssue(DSPLValidationIssue(
          DSPLValidationIssue.GENERAL, DSPLValidationIssue.MISSING_INFO, None,
          'No concepts found in dataset'))

    for concept in self.dspl_dataset.concepts:
      # Check table reference
      if concept.table_ref:
        table = self.dspl_dataset.GetTable(concept.table_ref)

        if not table:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.CONCEPT,
                  DSPLValidationIssue.BAD_REFERENCE,
                  concept.concept_id,
                  'Concept \'%s\' refers to a non-existent table: \'%s\'' %
                  (concept.concept_id, concept.table_ref)))
      elif not concept.concept_reference:
        # Make sure this concept has a table reference if it is ever used as a
        # dimension
        for data_slice in self.dspl_dataset.slices:
          for dimension_ref in data_slice.dimension_refs:
            if dimension_ref == concept.concept_id:
              self.AddIssue(
                  DSPLValidationIssue(
                      DSPLValidationIssue.CONCEPT,
                      DSPLValidationIssue.MISSING_INFO, concept.concept_id,
                      'Concept \'%s\' does not have a definition table' %
                      concept.concept_id))
              return

  def CheckSlices(self):
    """Check for issues related to the slices in this dataset."""
    if not self.dspl_dataset.slices:
      self.AddIssue(
          DSPLValidationIssue(
              DSPLValidationIssue.GENERAL, DSPLValidationIssue.MISSING_INFO,
              None, 'No slices found in dataset'))

    dimension_keys = {}

    for data_slice in self.dspl_dataset.slices:
      if not data_slice.dimension_refs:
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.SLICE, DSPLValidationIssue.MISSING_INFO,
                data_slice.slice_id,
                'Slice \'%s\' has no dimensions' % data_slice.slice_id))
      else:
        # Make sure combination of dimensions in this dataset are unique
        dimension_key = '_'.join(sorted(data_slice.dimension_refs))

        if dimension_key in dimension_keys:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.SLICE,
                  DSPLValidationIssue.INCONSISTENCY,
                  data_slice.slice_id,
                  'Slice \'%s\' has same dimensions as another slice' %
                  data_slice.slice_id))
        else:
          dimension_keys[dimension_key] = True

      if not data_slice.metric_refs:
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.SLICE, DSPLValidationIssue.MISSING_INFO,
                data_slice.slice_id,
                'Slice \'%s\' has no metrics' % data_slice.slice_id))

      time_dimension = ''

      # Check dimensions
      for dimension_id in data_slice.dimension_refs:
        concept = self.dspl_dataset.GetConcept(dimension_id)

        if not concept:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.SLICE, DSPLValidationIssue.BAD_REFERENCE,
                  data_slice.slice_id,
                  'Slice \'%s\' refers to nonexistent concept: \'%s\'' %
                  (data_slice.slice_id, dimension_id)))
        else:
          if 'time:' in concept.concept_reference:
            time_dimension = concept.concept_reference

      if (not time_dimension) and data_slice.dimension_refs:
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.SLICE, DSPLValidationIssue.MISSING_INFO,
                data_slice.slice_id,
                'Slice \'%s\' has no time dimension' % data_slice.slice_id))

      # Check metrics
      for metric_id in data_slice.metric_refs:
        if not self.dspl_dataset.GetConcept(metric_id):
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.SLICE, DSPLValidationIssue.BAD_REFERENCE,
                  data_slice.slice_id,
                  'Slice \'%s\' refers to nonexistent concept: \'%s\'' %
                  (data_slice.slice_id, metric_id)))

      # Check table reference
      if not data_slice.table_ref:
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.SLICE, DSPLValidationIssue.MISSING_INFO,
                data_slice.slice_id,
                'Slice \'%s\' has no table reference' % data_slice.slice_id))
      else:
        table = self.dspl_dataset.GetTable(data_slice.table_ref)

        if not table:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.SLICE, DSPLValidationIssue.BAD_REFERENCE,
                  data_slice.slice_id,
                  'Slice \'%s\' refers to non-existent table: \'%s\'' %
                  (data_slice.slice_id, data_slice.table_ref)))

  def CheckTables(self):
    """Check for issues related to the tables in this dataset."""
    if not self.dspl_dataset.tables:
      self.AddIssue(
          DSPLValidationIssue(
              DSPLValidationIssue.GENERAL, DSPLValidationIssue.MISSING_INFO,
              None, 'No tables found in dataset'))

    for table in self.dspl_dataset.tables:
      table_header_row = table.table_data[0]

      # Skip over columns that are in XML but not CSV
      non_constant_columns = [column for column in table.columns if
                              not column.constant_value]

      # Make sure header size is consistent with column metadata
      if len(non_constant_columns) != len(table_header_row):
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                table.table_id,
                'Table \'%s\' does not have same number of columns as its CSV' %
                table.table_id))
      else:
        # Check that header strings match column IDs
        for table_column in non_constant_columns:
          if table_column.column_id not in table_header_row:
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.TABLE,
                    DSPLValidationIssue.INCONSISTENCY, table.table_id,
                    'Table \'%s\', column \'%s\' cannot be found in the '
                    'header of the corresponding CSV: \'%s\'' %
                    (table.table_id, table_column.column_id,
                     table_header_row)))

          # Check date format existence
          if table_column.data_type == 'date' and not table_column.data_format:
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.TABLE, DSPLValidationIssue.MISSING_INFO,
                    table.table_id,
                    'Table \'%s\', column %s is missing date format' %
                    (table.table_id, table_column.column_id)))

  def _GetConceptInstances(self, concept):
    """Get all instances of a concept from its definition table.

    Args:
      concept: A dspl_model.Concept

    Returns:
      A dictionary containing one entry for each instance value if the concept's
      table is well-defined; otherwise, None.
    """
    concept_instances = {}

    concept_table = self.dspl_dataset.GetTable(concept.table_ref)

    if concept_table is not None:
      column_ids = [column.column_id for column in concept_table.columns]

      # Check that concept ID is a column in its definition table
      if concept.concept_id not in column_ids:
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                concept_table.table_id,
                'Table \'%s\' doesn\'t have column matching concept ID: %s; '
                'aborting check of this table and its data' %
                (concept_table.table_id, concept.concept_id)))
        return None
      else:
        concept_col_index = column_ids.index(concept.concept_id)

      if self.full_data_check:
        for r, row in enumerate(concept_table.table_data):
          if r == 0:
            header_row_length = len(row)
            column_to_csv_index = {}

            # Match table columns to CSV columns
            for column in concept_table.columns:
              if not column.constant_value:
                if column.column_id in row:
                  column_to_csv_index[column] = row.index(column.column_id)
                else:
                  self.AddIssue(
                      DSPLValidationIssue(
                          DSPLValidationIssue.DATA,
                          DSPLValidationIssue.INCONSISTENCY,
                          concept_table.table_id,
                          'CSV for table \'%s\' is missing header element for '
                          'column \'%s\'; aborting check of this table and '
                          'its data' %
                          (concept_table.table_id, column.column_id)))
                  return None

            concept_csv_index = column_to_csv_index[
                concept_table.columns[concept_col_index]]
          else:
            # Check that each row has the same number of columns as the header
            if len(row) != header_row_length:
              self.AddIssue(
                  DSPLValidationIssue(
                      DSPLValidationIssue.DATA, DSPLValidationIssue.INCONSISTENCY,
                      concept_table.table_id,
                      'CSV for table \'%s\' has unexpected number of columns '
                      'in row %d; aborting check of this table and its data' %
                      (concept_table.table_id, r)))
              return None

            # Check that row elements are properly formatted
            for (column, csv_index) in column_to_csv_index.items():
              self._CheckCSVValueFormat(
                  column, r + 1, row[csv_index], concept_table)

            # Check for repeated instances
            if row[concept_csv_index] in concept_instances:
              self.AddIssue(
                  DSPLValidationIssue(
                      DSPLValidationIssue.DATA, DSPLValidationIssue.REPEATED_INFO,
                      concept_table.table_id,
                      'CSV for table \'%s\' has repeated concept ID: %s' %
                      (concept_table.table_id, row[concept_csv_index])))
            else:
              concept_instances[row[concept_csv_index]] = True

        return concept_instances
    return None

  def _CheckDateColumn(self, dimension_concept, slice_table, date_column):
    """Do some basic checking of the date column of a slice table.

    TODO: Make this checking more sophisticated.

    Args:
      dimension_concept: Instance of dspl_model.Concept
      slice_table: A dspl_model.Table for slice containing previous concept
      date_column: A date-typed dspl_model.TableColumn in the latter table
    """
    column_format = date_column.data_format

    if column_format:
      if dimension_concept.concept_reference == 'time:year':
        if 'y' not in column_format:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                  slice_table.table_id,
                  'Table \'%s\', column \'%s\' corresponds to \'time:year\' '
                  'but the format (\'%s\') does not look like a standard Joda '
                  'DateTime year format (e.g., \'yyyy\')' %
                  (slice_table.table_id, date_column.column_id, column_format)))
      elif dimension_concept.concept_reference == 'time:month':
        if ('y' not in column_format) or ('M' not in column_format):
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                  slice_table.table_id,
                  'Table \'%s\', column \'%s\' corresponds to \'time:month\' '
                  'but the format (\'%s\') does not look like a standard Joda '
                  'DateTime month format (e.g., \'MM-yyyy\')' %
                  (slice_table.table_id, date_column.column_id, column_format)))
      elif dimension_concept.concept_reference == 'time:day':
        if (('y' not in column_format) or ('M' not in column_format) or
            ('d' not in column_format)):
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                  slice_table.table_id,
                  'Table \'%s\', column \'%s\' corresponds to \'time:day\' '
                  'but the format (\'%s\') does not look like a correct Joda '
                  'DateTime day format (e.g., \'dd-MM-yyyy\')' %
                  (slice_table.table_id, date_column.column_id, column_format)))

  def _CheckCSVValueFormat(self, column, row, value, table):
    """Check that a CSV value is formatted appropriately.

    Note that this checking is very basic as only integer and float values are
    checked; strings and dates are assumed to be validly formatted.

    TODO: Make this checking more sophisticated.

    Args:
      column: A dspl_model.TableColumn
      row: Integer row in the table CSV
      value: The string value from the corresponding row and column in the CSV
      table: The dspl_model.Table containing the column
    """
    if column.data_type == 'integer':
      if not re.match('^[-]{0,1}[0-9]+$', value):
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.DATA, DSPLValidationIssue.INCONSISTENCY,
                table.table_id,
                'CSV for table \'%s\' has badly formatted integer on line %d: '
                '\'%s\'' %
                (table.table_id, row, value)))
    elif column.data_type == 'float':
      if not re.match('^[-]{0,1}[0-9]*(\.[0-9]+){0,1}$', value):
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.DATA, DSPLValidationIssue.INCONSISTENCY,
                table.table_id,
                'CSV for table \'%s\' has badly formatted float on line %d: '
                '\'%s\'' %
                (table.table_id, row, value)))

  def _CheckSliceData(self, data_slice, concept_data):
    """Check the data associated with a single slice.

    Args:
      data_slice: A dspl_model.Slice
      concept_data: A dictionary of dictionaries containing the data values
                    for each internally defined concept
    """
    slice_table = self.dspl_dataset.GetTable(data_slice.table_ref)

    if slice_table is not None:
      slice_table_columns = [column.column_id for column in slice_table.columns]

      dimension_column_map = {}
      time_dimension_column = None

      # Evaluate the dimensions
      for dimension_id in data_slice.dimension_refs:
        if dimension_id in data_slice.dimension_map:
          slice_table_column_id = data_slice.dimension_map[dimension_id]
        else:
          slice_table_column_id = dimension_id

        # Check that there is a column in the slice table corresponding to this
        # dimension
        if slice_table_column_id not in slice_table_columns:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                  slice_table.table_id,
                  'Table \'%s\' does not have column matching concept \'%s\'; '
                  'aborting check of this table and its data' %
                  (slice_table.table_id, slice_table_column_id)))
          return

        dimension_column = (
            slice_table.columns[
                slice_table_columns.index(slice_table_column_id)])
        dimension_concept = self.dspl_dataset.GetConcept(dimension_id)

        if not dimension_column.constant_value:
          dimension_column_map[dimension_id] = dimension_column

        if dimension_concept is not None:
          # Detect whether this dimension is time-related
          if 'time:' in dimension_concept.concept_reference:
            if dimension_id in dimension_column_map:
              time_dimension_column = dimension_column
              self._CheckDateColumn(
                  dimension_concept, slice_table, time_dimension_column)

          # Compare dimension type to column type
          if (dimension_concept.data_type and
              (dimension_concept.data_type !=
               dimension_column.data_type)):
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.TABLE,
                    DSPLValidationIssue.INCONSISTENCY,
                    slice_table.table_id,
                    'Table \'%s\' column \'%s\' has type (%s) inconsistent '
                    'with that of the matching dimension (%s)' %
                    (slice_table.table_id, slice_table_column_id,
                     dimension_column.data_type,
                     dimension_concept.data_type)))

      metric_column_map = {}

      # Evaluate the metrics
      for metric_id in data_slice.metric_refs:
        if metric_id in data_slice.metric_map:
          slice_table_column_id = data_slice.metric_map[metric_id]
        else:
          slice_table_column_id = metric_id

        # Check that there is a column in the slice table corresponding to this
        # metric
        if slice_table_column_id not in slice_table_columns:
          self.AddIssue(
              DSPLValidationIssue(
                  DSPLValidationIssue.TABLE, DSPLValidationIssue.INCONSISTENCY,
                  slice_table.table_id,
                  'Table \'%s\' does not have column matching concept \'%s\'; '
                  'aborting check of this table and its data' %
                  (slice_table.table_id, slice_table_column_id)))
          return
        else:
          metric_concept = self.dspl_dataset.GetConcept(metric_id)
          metric_column = (
              slice_table.columns[
                  slice_table_columns.index(slice_table_column_id)])

          if not metric_column.constant_value:
            metric_column_map[metric_id] = metric_column

          if metric_concept is not None:
            # Compare metric type to column type
            if (metric_concept.data_type and
                (metric_concept.data_type !=
                 metric_column.data_type)):
              self.AddIssue(
                  DSPLValidationIssue(
                      DSPLValidationIssue.TABLE,
                      DSPLValidationIssue.INCONSISTENCY,
                      slice_table.table_id,
                      'Table \'%s\' column \'%s\' has type (%s) inconsistent '
                      'with that of the matching metric (%s)' %
                      (slice_table.table_id, slice_table_column_id,
                       metric_column.data_type,
                       metric_concept.data_type)))

      if not self.full_data_check:
        return

      observed_dimension_ids = {}
      non_time_observed_dimension_ids = {}

      non_time_prev_dimension_ids = ''
      bad_sorting = False

      # Evaluate each data row
      for r, row in enumerate(slice_table.table_data):
        if r == 0:
          header_row_length = len(row)
          column_to_csv_index = {}

          # Match table columns to CSV columns
          for column in slice_table.columns:
            if not column.constant_value:
              if column.column_id in row:
                column_to_csv_index[column] = row.index(column.column_id)
              else:
                self.AddIssue(
                    DSPLValidationIssue(
                        DSPLValidationIssue.DATA,
                        DSPLValidationIssue.INCONSISTENCY,
                        slice_table.table_id,
                        'CSV for table \'%s\' is missing header element for '
                        'column \'%s\'; aborting check of this table and '
                        'its data' %
                        (slice_table.table_id, column.column_id)))
                return
        else:
          # Check that row has the same number of columns as its header
          if len(row) != header_row_length:
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.DATA, DSPLValidationIssue.INCONSISTENCY,
                    slice_table.table_id,
                    'CSV for table \'%s\' has unexpected number of columns '
                    'in row %d; aborting check of this table and its data' %
                    (slice_table.table_id, r + 1)))
            return

          # Check that row elements are properly formatted
          for (column, csv_index) in column_to_csv_index.items():
            self._CheckCSVValueFormat(
                column, r + 1, row[csv_index], slice_table)

          curr_dimension_ids = ','.join(
              [row[column_to_csv_index[col]]
               for col in dimension_column_map.values()])

          non_time_curr_dimension_ids = ','.join(
              [row[column_to_csv_index[col]]
               for col in dimension_column_map.values()
               if col != time_dimension_column])

          # Check that dimension keys are unique
          if curr_dimension_ids in observed_dimension_ids:
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.DATA,
                    DSPLValidationIssue.REPEATED_INFO,
                    slice_table.table_id,
                    'CSV for table \'%s\' has repeated set of keys: \'%s\'' %
                    (slice_table.table_id, curr_dimension_ids)))
          else:
            observed_dimension_ids[curr_dimension_ids] = True

          # Check non-time dimensions for uniqueness and consistency
          if non_time_curr_dimension_ids != non_time_prev_dimension_ids:
            non_time_prev_dimension_ids = non_time_curr_dimension_ids

            if non_time_curr_dimension_ids in non_time_observed_dimension_ids:
              bad_sorting = True
            else:
              # We've never seen this combination before
              non_time_observed_dimension_ids[non_time_curr_dimension_ids] = (
                  True)

              # Check that dimension values are valid
              for (dimension_id, column) in dimension_column_map.items():
                if dimension_id in concept_data:
                  row_value = row[column_to_csv_index[column]]

                  if (concept_data[dimension_id] and
                      (row_value not in concept_data[dimension_id])):
                    self.AddIssue(
                        DSPLValidationIssue(
                            DSPLValidationIssue.DATA,
                            DSPLValidationIssue.INCONSISTENCY,
                            slice_table.table_id,
                            'CSV for table \'%s\' has unrecognized value for '
                            'concept \'%s\' on line %d: \'%s\'' %
                            (slice_table.table_id, dimension_id, r + 1,
                             row_value)))

      if bad_sorting:
        self.AddIssue(
            DSPLValidationIssue(
                DSPLValidationIssue.DATA,
                DSPLValidationIssue.OTHER,
                slice_table.table_id,
                'CSV for table \'%s\' is not properly sorted' %
                (slice_table.table_id)))

  def CheckData(self):
    """Check table data for sorting and consistency with concept definitions."""
    concept_data = {}

    # Retrieve and check dimension concept data
    for data_slice in self.dspl_dataset.slices:
      for dimension_id in data_slice.dimension_refs:
        concept = self.dspl_dataset.GetConcept(dimension_id)

        if concept is not None:
          if not concept.concept_reference:
            if concept.concept_id not in concept_data:
              concept_instances = self._GetConceptInstances(concept)

              concept_data[concept.concept_id] = concept_instances

    # Check slice data, where possible
    for data_slice in self.dspl_dataset.slices:
      self._CheckSliceData(data_slice, concept_data)

  def RunValidation(self, verbose=True):
    """Run through all of the validation methods and return a summary string.

    Args:
      verbose: Add extra, helpful information into result

    Returns:
      Pretty-printed string summarizing the results of the validation
    """
    self.CheckConcepts()
    self.CheckSlices()
    self.CheckTables()
    self.CheckData()

    self.SortIssues()

    result_lines = []

    prefix_chars = '* '
    underline_chars = '--------------\n'

    # General issues
    general_issues = [issue for issue in self.issues if
                      issue.issue_scope == DSPLValidationIssue.GENERAL]

    if general_issues:
      if verbose:
        result_lines.extend(['\nGeneral Issues\n', underline_chars])

      for issue in general_issues:
        result_lines.extend([prefix_chars, str(issue), '\n'])

    # Concept issues
    concept_issues = [issue for issue in self.issues if
                      issue.issue_scope == DSPLValidationIssue.CONCEPT]

    if concept_issues:
      if verbose:
        result_lines.extend(['\nConcept Issues\n', underline_chars])

      for issue in concept_issues:
        result_lines.extend([prefix_chars, str(issue), '\n'])

    # Slice issues
    slice_issues = [issue for issue in self.issues if
                    issue.issue_scope == DSPLValidationIssue.SLICE]

    if slice_issues:
      if verbose:
        result_lines.extend(['\nSlice Issues\n', underline_chars])

      for issue in slice_issues:
        result_lines.extend([prefix_chars, str(issue), '\n'])

    # Table issues
    table_issues = [issue for issue in self.issues if
                    issue.issue_scope == DSPLValidationIssue.TABLE]

    if table_issues:
      if verbose:
        result_lines.extend(['\nTable Issues\n', underline_chars])

      for issue in table_issues:
        result_lines.extend([prefix_chars, str(issue), '\n'])

    # Data issues
    data_issues = [issue for issue in self.issues if
                   issue.issue_scope == DSPLValidationIssue.DATA]

    if data_issues:
      if verbose:
        result_lines.extend(['\nData Issues\n', underline_chars])

      for issue in data_issues:
        result_lines.extend([prefix_chars, str(issue), '\n'])

    if not result_lines:
      if verbose:
        result_lines = ['No issues found!']

    return ''.join(result_lines)
