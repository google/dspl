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

"""Tests of dspl_model_loader module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import os.path
import shutil
import tempfile
import unittest

import dspl_model
import dspl_model_loader
import dspl_model_test


_SLICE_CSV_DATA = (
"""col1,col2
val1,1
val2,2
val3,3""")


class DSPLModelLoaderTests(unittest.TestCase):
  """Test cases for dspl_model_loader module."""

  def setUp(self):
    self.input_dir = tempfile.mkdtemp()
    self.xml_file_path = os.path.join(self.input_dir, 'dataset.xml')

    xml_file = open(self.xml_file_path, 'w')
    xml_file.write(dspl_model_test.TEST_DSPL_XML)
    xml_file.close()

    slice_csv_file = open(os.path.join(self.input_dir, 'mydata.csv'), 'w')
    slice_csv_file.write(_SLICE_CSV_DATA)
    slice_csv_file.close()

  def tearDown(self):
    shutil.rmtree(self.input_dir)

  def testDSPLImportLoading(self):
    """Test that dataset is imported correctly."""
    dspl_dataset = dspl_model_loader.LoadDSPLFromFiles(self.xml_file_path)

    # Test basic info
    self.assertEqual(dspl_dataset.name, 'My Dataset')
    self.assertEqual(dspl_dataset.description, 'My Dataset Description')
    self.assertEqual(dspl_dataset.url, 'url1')

    self.assertEqual(dspl_dataset.provider_name, 'Googler')
    self.assertEqual(dspl_dataset.provider_url, 'url2')

    # Test imports
    self.assertEqual(len(dspl_dataset.imports), 2)

    self.assertEqual(dspl_dataset.imports[0].namespace_id,
                     'imported_namespace1')
    self.assertEqual(dspl_dataset.imports[0].namespace_url,
                     'http://imported_namespace1_url')
    self.assertEqual(dspl_dataset.imports[1].namespace_id,
                     'imported_namespace2')
    self.assertEqual(dspl_dataset.imports[1].namespace_url,
                     'http://imported_namespace2_url')

    # Test concepts
    self.assertEqual(len(dspl_dataset.concepts), 3)

    self.assertEqual(dspl_dataset.concepts[0].concept_id, 'concept1')
    self.assertEqual(dspl_dataset.concepts[0].concept_extension_reference,
                     'entity:entity')
    self.assertEqual(dspl_dataset.concepts[0].concept_name, 'Concept 1')
    self.assertEqual(dspl_dataset.concepts[0].concept_description,
                     'Concept 1 Description')
    self.assertEqual(dspl_dataset.concepts[0].data_type, 'string')
    self.assertEqual(dspl_dataset.concepts[0].table_ref, 'table2')

    self.assertEqual(dspl_dataset.concepts[1].concept_id, 'concept2')
    self.assertEqual(dspl_dataset.concepts[1].concept_name, 'Concept 2')
    self.assertEqual(dspl_dataset.concepts[1].concept_description,
                     'Concept 2 Description')
    self.assertEqual(dspl_dataset.concepts[1].data_type, 'integer')

    self.assertEqual(dspl_dataset.concepts[2].concept_id, 'geo:country')
    self.assertEqual(dspl_dataset.concepts[2].concept_reference, 'geo:country')

    # Test slices
    self.assertEqual(len(dspl_dataset.slices), 1)

    self.assertEqual(dspl_dataset.slices[0].slice_id, 'data_slice')
    self.assertEqual(dspl_dataset.slices[0].dimension_refs,
                     ['concept1', 'geo:country'])
    self.assertEqual(dspl_dataset.slices[0].metric_refs, ['concept2'])
    self.assertEqual(dspl_dataset.slices[0].table_ref, 'table3')

    # Test tables
    self.assertEqual(len(dspl_dataset.tables), 1)

    self.assertEqual(dspl_dataset.tables[0].table_id, 'table')
    self.assertEqual(dspl_dataset.tables[0].file_name, 'mydata.csv')

    self.assertEqual(len(dspl_dataset.tables[0].columns), 2)
    self.assertEqual(dspl_dataset.tables[0].columns[0].column_id, 'col1')
    self.assertEqual(dspl_dataset.tables[0].columns[0].data_type, 'string')
    self.assertEqual(dspl_dataset.tables[0].columns[1].column_id, 'col2')
    self.assertEqual(dspl_dataset.tables[0].columns[1].data_type, 'integer')

    expected_table_rows = _SLICE_CSV_DATA.splitlines()
    expected_table_data = [r.split(',') for r in expected_table_rows]

    self.assertEqual(dspl_dataset.tables[0].table_data, expected_table_data)


if __name__ == '__main__':
  unittest.main()
