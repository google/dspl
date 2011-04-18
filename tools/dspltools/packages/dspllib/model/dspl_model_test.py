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

"""Tests of dspl_model module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import csv
import itertools
import os
import re
import tempfile
import unittest
import xml.etree.ElementTree

import dspl_model


TEST_DSPL_XML = """
<dspl xmlns="http://schemas.google.com/dspl/2010"
    xmlns:imported_namespace1="http://imported_namespace1_url"
    xmlns:imported_namespace2="http://imported_namespace2_url">
  <import namespace="http://imported_namespace1_url"/>
  <import namespace="http://imported_namespace2_url"/>

  <info>
    <name>
      <value xml:lang="en">My Dataset</value>
    </name>
    <description>
      <value xml:lang="en">My Dataset Description</value>
    </description>
    <url>
      <value xml:lang="en">url1</value>
    </url>
  </info>

  <provider>
    <name>
      <value xml:lang="en">Googler</value>
    </name>
    <url>
      <value xml:lang="en">url2</value>
    </url>
  </provider>

  <concepts>
    <concept id="concept1" extends="entity:entity">
      <info>
        <name>
          <value xml:lang="en">Concept 1</value>
        </name>
        <description>
          <value xml:lang="en">Concept 1 Description</value>
        </description>
      </info>
      <type ref="string"/>
      <table ref="table2"/>
    </concept>

    <concept id="concept2">
      <info>
        <name>
          <value xml:lang="en">Concept 2</value>
        </name>
        <description>
          <value xml:lang="en">Concept 2 Description</value>
        </description>
      </info>
      <type ref="integer"/>
    </concept>
  </concepts>

  <slices>
    <slice id="data_slice">
      <dimension concept="concept1"/>
      <dimension concept="geo:country"/>
      <metric concept="concept2"/>
      <table ref="table3">
        <mapDimension concept="geo:country" toColumn="concept3"/>
      </table>
    </slice>
  </slices>

  <tables>
    <table id="table">
      <column id="col1" type="string"/>
      <column id="col2" type="integer">
        <value>1234</value>
      </column>
      <data>
        <file encoding="utf-8" format="csv">mydata.csv</file>
      </data>
    </table>
  </tables>
</dspl>"""


class DSPLModelTests(unittest.TestCase):
  """General test cases for dspl_model module."""

  def setUp(self):
    self.dspl_dataset = dspl_model.DataSet(verbose=False)

  def testGettersAndSetters(self):
    """Test behavior of concept, slice, and table setters and getters."""
    self.dspl_dataset.AddImport(
        dspl_model.Import(namespace_id='import1', namespace_url='import1_url'))
    self.dspl_dataset.AddConcept(
        dspl_model.Concept(concept_id='concept1'))
    self.dspl_dataset.AddConcept(
        dspl_model.Concept(concept_id='concept2'))
    self.dspl_dataset.AddSlice(
        dspl_model.Slice(slice_id='slice1'))
    self.dspl_dataset.AddTable(
        dspl_model.Table(table_id='table1'))

    self.assertEqual(self.dspl_dataset.GetImport('import1').namespace_url,
                     'import1_url')
    self.assertEqual(self.dspl_dataset.GetConcept('concept2').concept_id,
                     'concept2')
    self.assertEqual(self.dspl_dataset.GetSlice('slice1').slice_id,
                     'slice1')
    self.assertEqual(self.dspl_dataset.GetTable('table1').table_id,
                     'table1')
    self.assertEqual(self.dspl_dataset.GetConcept('concept3'), None)
    self.assertEqual(self.dspl_dataset.GetSlice('slice3'), None)
    self.assertEqual(self.dspl_dataset.GetTable('table3'), None)

  def testDatasetXMLCreation(self):
    """Create dataset using models, then compare output to expected XML."""
    self.dspl_dataset.name = 'My Dataset'
    self.dspl_dataset.description = 'My Dataset Description'
    self.dspl_dataset.url = 'url1'

    self.dspl_dataset.provider_name = 'Googler'
    self.dspl_dataset.provider_url = 'url2'

    self.dspl_dataset.AddImport(
        dspl_model.Import(
            namespace_id='imported_namespace1',
            namespace_url='http://imported_namespace1_url'))

    self.dspl_dataset.AddImport(
        dspl_model.Import(
            namespace_id='imported_namespace2',
            namespace_url='http://imported_namespace2_url'))

    self.dspl_dataset.AddConcept(
        dspl_model.Concept(
            concept_id='concept1',
            concept_name='Concept 1',
            concept_description='Concept 1 Description',
            table_ref='table2',
            concept_extension_reference='entity:entity',
            data_type='string'))

    self.dspl_dataset.AddConcept(
        dspl_model.Concept(
            concept_id='concept2',
            concept_name='Concept 2',
            concept_description='Concept 2 Description',
            data_type='integer'))

    self.dspl_dataset.AddConcept(
        dspl_model.Concept(
            concept_id='concept3',
            concept_name='Concept 3',
            concept_description='Concept 3 Description',
            concept_reference='geo:country',
            data_type='string'))

    self.dspl_dataset.AddSlice(
        dspl_model.Slice(
            slice_id='data_slice',
            dimension_refs=['concept1', 'concept3'],
            metric_refs=['concept2'],
            table_ref='table3'))

    self.dspl_dataset.AddTable(
        dspl_model.Table(
            table_id='table',
            columns=[dspl_model.TableColumn('col1', 'string', '', ''),
                     dspl_model.TableColumn('col2', 'integer', '', '1234')],
            file_name='mydata.csv',
            verbose=False))

    xml_output = self.dspl_dataset.ToXMLElement()

    for element_tuple in itertools.izip_longest(
        xml_output.getiterator(),
        xml.etree.ElementTree.fromstring(TEST_DSPL_XML).getiterator()):
      constructed_element = element_tuple[0]
      expected_element = element_tuple[1]

      # Compare tag names
      constructed_tag_name = constructed_element.tag

      # Remove namespace prefixes from expected tag
      expected_tag_name = re.search(
          '^(?:\{.*\})?(.*)$', expected_element.tag).group(1)

      self.assertEqual(constructed_tag_name, expected_tag_name)

      # Compare tag attributes, ignoring these for dspl and value tags
      if (constructed_element.tag != 'dspl' and
          constructed_element.tag != 'value'):
        self.assertEqual(sorted(constructed_element.items()),
                         sorted(expected_element.items()))

      # Compare tag text
      constructed_text = constructed_element.text
      expected_text = expected_element.text

      # Handle differences in how test and expected results handle text
      if expected_text:
        expected_text = expected_text.strip()

      if expected_text == '':
        expected_text = None

      self.assertEqual(constructed_text,
                       expected_text)


class DSPLTableTests(unittest.TestCase):
  """Test cases for table writing functionality of dspl_model module."""

  def setUp(self):
    csv_file_params = tempfile.mkstemp()

    os.close(csv_file_params[0])
    self.csv_file_path = csv_file_params[1]

  def tearDown(self):
    os.remove(self.csv_file_path)

  def testTableData(self):
    """Test that Table objects materialize their data to CSV correctly."""
    table_data = [['col1', 'col2', 'col3'],
                  ['1/1/2010', 'blue', 'california'],
                  ['1/2/2010', 'red', 'maine']]

    dspl_table = dspl_model.Table(
        table_id='table',
        file_name=self.csv_file_path,
        table_data=table_data,
        verbose=False)

    dspl_table.MaterializeData('')

    output_csv_file = open(self.csv_file_path, 'r')
    output_csv_reader = csv.reader(output_csv_file)

    self.assertEqual(
        output_csv_reader.next(), ['col1', 'col2', 'col3'])
    self.assertEqual(
        output_csv_reader.next(), ['1/1/2010', 'blue', 'california'])
    self.assertEqual(
        output_csv_reader.next(), ['1/2/2010', 'red', 'maine'])

    output_csv_file.close()


if __name__ == '__main__':
  unittest.main()
