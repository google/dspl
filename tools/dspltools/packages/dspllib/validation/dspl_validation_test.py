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

"""Tests of dsplvalidate module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import os
import os.path
import unittest

import dspl_validation
from dspllib.model import dspl_model_loader


class DSPLValidationTests(unittest.TestCase):
  """Test case for dspl_validation module."""

  def setUp(self):
    self.dataset = dspl_model_loader.LoadDSPLFromFiles(
        os.path.join(os.path.split(__file__)[0], 'test_dataset',
                     'dataset.xml'))

  def testValidDSPL(self):
    """A simple end-to-end test of the valid XML case."""
    dspl_validator = dspl_validation.DSPLDatasetValidator(self.dataset)
    dspl_validator.RunValidation()

    all_issues = dspl_validator.GetIssues()
    self.assertEqual(len(all_issues), 0)

  def testMissingConcepts(self):
    self.dataset.concepts = []

    self._SingleIssueTestHelper(
        ['concepts'], dspl_validation.DSPLValidationIssue.GENERAL,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, None)

  def testBadConceptTableRef(self):
    self.dataset.GetConcept('country').table_ref = 'nonexistent_table'

    self._SingleIssueTestHelper(
        ['concepts'], dspl_validation.DSPLValidationIssue.CONCEPT,
        dspl_validation.DSPLValidationIssue.BAD_REFERENCE, 'country')

  def testDimensionMissingTable(self):
    self.dataset.GetConcept('country').table_ref = ''

    self._SingleIssueTestHelper(
        ['concepts'], dspl_validation.DSPLValidationIssue.CONCEPT,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, 'country')

  def testMissingSlices(self):
    self.dataset.slices = []

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.GENERAL,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, None)

  def testMissingDimensions(self):
    self.dataset.GetSlice('countries_slice').dimension_refs = []

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, 'countries_slice')

  def testDuplicateDimensions(self):
    self.dataset.GetSlice('states_slice').dimension_refs[0] = 'country'

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY, 'states_slice')

  def testMissingMetrics(self):
    self.dataset.GetSlice('countries_slice').metric_refs = []

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, 'countries_slice')

  def testBadSliceDimensionRef(self):
    self.dataset.GetSlice('countries_slice').dimension_refs[0] = (
        'nonexistent_concept')

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.BAD_REFERENCE, 'countries_slice')

  def testBadSliceMetricRef(self):
    self.dataset.GetSlice('countries_slice').metric_refs[0] = (
        'nonexistent_concept')

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.BAD_REFERENCE, 'countries_slice')

  def testMissingTimeDimension(self):
    self.dataset.GetSlice('countries_slice').dimension_refs.remove('time:year')

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, 'countries_slice')

  def testMissingSliceTableRef(self):
    self.dataset.GetSlice('countries_slice').table_ref = ''

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, 'countries_slice')

  def testBadSliceTableRef(self):
    self.dataset.GetSlice('countries_slice').table_ref = 'nonexistent_table'

    self._SingleIssueTestHelper(
        ['slices'], dspl_validation.DSPLValidationIssue.SLICE,
        dspl_validation.DSPLValidationIssue.BAD_REFERENCE, 'countries_slice')

  def testMissingTables(self):
    self.dataset.tables = []

    self._SingleIssueTestHelper(
        ['tables'], dspl_validation.DSPLValidationIssue.GENERAL,
        dspl_validation.DSPLValidationIssue.MISSING_INFO, None)

  def testInconsistentNumColumns(self):
    self.dataset.GetTable('countries_table').columns.pop()

    self._SingleIssueTestHelper(
        ['tables'], dspl_validation.DSPLValidationIssue.TABLE,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY, 'countries_table')

  def testInconsistentColumnNames(self):
    self.dataset.GetTable('countries_table').columns[0].column_id = (
        'bad_column_id')

    self._SingleIssueTestHelper(
        ['tables'], dspl_validation.DSPLValidationIssue.TABLE,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY, 'countries_table')

  def testMissingDateFormat(self):
    self.dataset.GetTable('countries_slice_table').columns[1].data_format = ''

    self._SingleIssueTestHelper(
        ['tables'], dspl_validation.DSPLValidationIssue.TABLE,
        dspl_validation.DSPLValidationIssue.MISSING_INFO,
        'countries_slice_table')

  def testBadConceptTableColumnIDs(self):
    self.dataset.GetTable('countries_table').columns[0].column_id = (
        'non_matching_id')

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.TABLE,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY,
        'countries_table')

  def testPoorlyFormedConceptCSV(self):
    self.dataset.GetTable('countries_table').table_data.append(['bad_row'])

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.DATA,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY,
        'countries_table')

  def testRepeatedConceptID(self):
    self.dataset.GetTable('countries_table').table_data.append(
        ['AL', 'Albania', '41.153332', '20.168331'])

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.DATA,
        dspl_validation.DSPLValidationIssue.REPEATED_INFO,
        'countries_table')

  def testBadSliceTableDimensionID(self):
    self.dataset.GetTable('countries_slice_table').columns[0].column_id = (
        'non_matching_id')

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.TABLE,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY,
        'countries_slice_table')

  def testBadSliceTableMetricID(self):
    self.dataset.GetTable('countries_slice_table').columns[2].column_id = (
        'non_matching_id')

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.TABLE,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY,
        'countries_slice_table')

  def testPoorlyFormedSliceCSV(self):
    self.dataset.GetTable('countries_slice_table').table_data.append(
        ['US', '1965', '110188299', '1234'])

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.DATA,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY,
        'countries_slice_table')

  def testRepeatedTableDimensions(self):
    self.dataset.GetTable('countries_slice_table').table_data.append(
        ['US', '1963', '110188299'])

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.DATA,
        dspl_validation.DSPLValidationIssue.REPEATED_INFO,
        'countries_slice_table')

  def testBadSliceConceptReferences(self):
    self.dataset.GetTable('countries_slice_table').table_data.append(
        ['unrecognized_value', '1963', '110188299'])

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.DATA,
        dspl_validation.DSPLValidationIssue.INCONSISTENCY,
        'countries_slice_table')

  def testBadSortOrder(self):
    self.dataset.GetTable('countries_slice_table').table_data.append(
        ['AF', '1975', '110188299'])

    self._SingleIssueTestHelper(
        ['data'], dspl_validation.DSPLValidationIssue.DATA,
        dspl_validation.DSPLValidationIssue.OTHER,
        'countries_slice_table')

  def testResultsString(self):
    self.dataset.GetConcept('country').table_ref = ''
    self.dataset.GetSlice('countries_slice').table_ref = 'nonexistent_table'
    self.dataset.GetTable('countries_slice_table').columns[0].column_id = (
        'nonexistent_column')

    dspl_validator = dspl_validation.DSPLDatasetValidator(self.dataset)

    result = dspl_validator.RunValidation()
    self.assertEqual(len(result.split('\n')), 13)

  def _SingleIssueTestHelper(
      self, check_stages, expected_scope, expected_type,
      expected_base_entity_id):
    """Run the validator and check the (single) issue produced."""
    dspl_validator = dspl_validation.DSPLDatasetValidator(self.dataset)

    if 'concepts' in check_stages:
      dspl_validator.CheckConcepts()

    if 'slices' in check_stages:
      dspl_validator.CheckSlices()

    if 'tables' in check_stages:
      dspl_validator.CheckTables()

    if 'data' in check_stages:
      dspl_validator.CheckData()

    all_issues = dspl_validator.GetIssues()

    self.assertEqual(len(all_issues), 1)

    issue = all_issues[0]

    self.assertEqual(issue.issue_scope, expected_scope)
    self.assertEqual(issue.issue_type, expected_type)
    self.assertEqual(issue.base_entity_id, expected_base_entity_id)

    if issue.base_entity_id:
      self.assertTrue(issue.base_entity_id in issue.message)


if __name__ == '__main__':
  unittest.main()
