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


class DSPLValidationIssue(object):
  """Object that records a single potential import issue in a dataset."""

  # Issue scopes
  GENERAL = 0
  CONCEPT = 1
  SLICE = 2
  TABLE = 3
  CSV = 4

  # Issue types
  MISSING_INFO = 100
  BAD_REFERENCE = 101
  INCONSISTENCY = 102
  OTHER = 103

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

  def __init__(self, dspl_dataset):
    """Create a new DSPLDatasetValidator object.

    Args:
      dspl_dataset: An instance of dspllib.model.dspl_model.DataSet
    """
    self.dspl_dataset = dspl_dataset
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
        for t, table_column in enumerate(non_constant_columns):
          if table_column.column_id != table_header_row[t]:
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.TABLE,
                    DSPLValidationIssue.INCONSISTENCY, table.table_id,
                    'Table \'%s\', column \'%s\' does not match the '
                    'corresponding column in its CSV: \'%s\'' %
                    (table.table_id, table_column.column_id,
                     table_header_row[t])))

          # Check date formats
          if table_column.data_type == 'date' and not table_column.data_format:
            self.AddIssue(
                DSPLValidationIssue(
                    DSPLValidationIssue.TABLE, DSPLValidationIssue.MISSING_INFO,
                    table.table_id,
                    'Table \'%s\', column %s is missing date format' %
                    (table.table_id, table_column.column_id)))

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

    if not result_lines:
      if verbose:
        result_lines = ['No issues found!']

    return ''.join(result_lines)
