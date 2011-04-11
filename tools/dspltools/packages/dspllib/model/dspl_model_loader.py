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

"""Import a DSPL dataset from disk into the dspl_model framework."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import codecs
import csv
import os.path
import xml.etree.ElementTree

import dspl_model

_DSPL_SCHEMA_PREFIX = '{http://schemas.google.com/dspl/2010}'


def _NSParser(input_file):
  """A special ElementTree parser that gets all the imported namespaces.

  Args:
    input_file: A file-like object containing XML

  Returns:
    A list with two elements: the root of the ElementTree, and a list of
    namespace strings imported by the XML file.
  """
  events = ('start', 'start-ns')

  root = None
  namespace_list = []

  for event, element in xml.etree.ElementTree.iterparse(input_file, events):
    if event == 'start-ns':
      namespace_list.append(element)
    elif event == 'start':
      if root is None:
        root = element

  return [xml.etree.ElementTree.ElementTree(root), namespace_list]


def _GetValue(parent_element):
  """Get the text nested inside an XML element's value element.

  Args:
    parent_element: An ElementTree element

  Returns:
    String inside value tag inside parent or, if no such tag can be found, None
  """
  if parent_element is not None:
    value_element = parent_element.find(_DSPL_SCHEMA_PREFIX + 'value')

    if value_element is not None:
      return value_element.text

  return ''


def _ReadCSVData(csv_data_file):
  """Read the data contained in a CSV file.

  Args:
    csv_data_file: File object containing CSV data

  Returns:
    List of lists, representing rows and row elements of CSV
  """
  csv_reader = csv.reader(open(csv_data_file, 'r'))

  data_rows = []

  for row in csv_reader:
    data_rows.append(row)

  return data_rows


def ElementToConcept(concept_element):
  """Convert an ElementTree concept element into a Concept object.

  Args:
    concept_element: ElementTree element having data from <concept>...</concept>
                     section in an XML file

  Returns:
    dspl_model.Concept object
  """
  dspl_concept = dspl_model.Concept()

  dspl_concept.concept_id = concept_element.get('id')
  dspl_concept.concept_extension_reference = (
      concept_element.get('extends', default=''))

  concept_info_element = concept_element.find(_DSPL_SCHEMA_PREFIX + 'info')

  if concept_info_element is not None:
    dspl_concept.concept_name = _GetValue(
        concept_info_element.find(_DSPL_SCHEMA_PREFIX + 'name'))
    dspl_concept.concept_description = _GetValue(
        concept_info_element.find(_DSPL_SCHEMA_PREFIX + 'description'))

  concept_type_element = concept_element.find(_DSPL_SCHEMA_PREFIX + 'type')

  if concept_type_element is not None:
    dspl_concept.data_type = concept_type_element.get('ref')

  concept_table_element = concept_element.find(
      _DSPL_SCHEMA_PREFIX + 'table')

  if concept_table_element is not None:
    dspl_concept.table_ref = concept_table_element.get('ref')

  return dspl_concept


def ElementToSlice(slice_element, dspl_dataset):
  """Convert an ElementTree slice element into a Slice object.

  Args:
    slice_element: ElementTree element having data from <slice>...</slice>
                   section in an XML file
    dspl_dataset: The dataset that this slice is a member of

  Returns:
    dspl_model.Slice object
  """
  dspl_slice = dspl_model.Slice()

  dspl_slice.slice_id = slice_element.get('id')

  # Parse dimensions
  dimension_elements = slice_element.findall(
      _DSPL_SCHEMA_PREFIX + 'dimension')

  dspl_dimension_refs = []

  for dimension_element in dimension_elements:
    dimension_id = dimension_element.get('concept')
    dspl_concept = dspl_dataset.GetConcept(dimension_id)

    if not dspl_concept and ':' in dimension_id:
      # Dimension refers to an externally-defined concept
      dspl_concept = dspl_model.Concept()
      dspl_concept.concept_id = dimension_id
      dspl_concept.concept_reference = dimension_id

      dspl_dataset.AddConcept(dspl_concept)

    dspl_dimension_refs.append(dimension_id)

  # Parse metrics
  metric_elements = slice_element.findall(
      _DSPL_SCHEMA_PREFIX + 'metric')

  dspl_metric_refs = []

  for metric_element in metric_elements:
    metric_id = metric_element.get('concept')
    dspl_concept = dspl_dataset.GetConcept(metric_id)

    if not dspl_concept and ':' in metric_id:
      # Metric refers to an externally-defined concept
      dspl_concept = dspl_model.Concept()
      dspl_concept.concept_id = metric_id
      dspl_concept.concept_reference = metric_id

      dspl_dataset.AddConcept(dspl_concept)

    dspl_metric_refs.append(metric_id)

  dspl_slice.dimension_refs = dspl_dimension_refs
  dspl_slice.metric_refs = dspl_metric_refs

  slice_table_element = slice_element.find(
      _DSPL_SCHEMA_PREFIX + 'table')

  if slice_table_element is not None:
    dspl_slice.table_ref = slice_table_element.get('ref')

  return dspl_slice


def ElementToTable(table_element, csv_path):
  """Convert an ElementTree table element into a Table object.

  Args:
    table_element: ElementTree element having data from <table>...</table>
                   section in an XML file
    csv_path: Path to directory where CSV file associated with this table can
              be found

  Returns:
    dspl_model.Table object
  """
  dspl_table = dspl_model.Table()
  dspl_table.table_id = table_element.get('id')

  column_elements = table_element.findall(_DSPL_SCHEMA_PREFIX + 'column')

  dspl_columns = []

  for column_element in column_elements:
    dspl_column = dspl_model.TableColumn(
        column_id=column_element.get('id'),
        data_type=column_element.get('type'),
        data_format=column_element.get('format', default=''))

    dspl_columns.append(dspl_column)

  dspl_table.columns = dspl_columns

  data_element = table_element.find(_DSPL_SCHEMA_PREFIX + 'data')

  if data_element is not None:
    file_element = data_element.find(_DSPL_SCHEMA_PREFIX + 'file')

    if file_element is not None:
      dspl_table.file_name = file_element.text

  if dspl_table.file_name:
    csv_file_path = os.path.join(
        csv_path,
        dspl_table.file_name)

    dspl_table.table_data = _ReadCSVData(csv_file_path)

  return dspl_table


def ElementTreeToDataset(element_tree, namespaces, csv_path):
  """Convert an ElementTree tree model into a DataSet object.

  Args:
    element_tree: ElementTree.ElementTree object containing complete data from
                  DSPL XML file
    namespaces: A list of (namespace_id, namespace_url) tuples
    csv_path: Directory where CSV files associated with dataset can be found

  Returns:
    dspl_model.DataSet object
  """
  dspl_dataset = dspl_model.DataSet()

  # Fill in basic info
  dspl_dataset.namespace = element_tree.getroot().get(
      _DSPL_SCHEMA_PREFIX + 'targetNamespace', default='')

  for namespace_id, namespace_url in namespaces:
    if namespace_id:
      dspl_dataset.AddImport(
          dspl_model.Import(namespace_id=namespace_id,
                            namespace_url=namespace_url))

  info_element = element_tree.find(_DSPL_SCHEMA_PREFIX + 'info')

  if info_element is not None:
    dspl_dataset.name = _GetValue(
        info_element.find(_DSPL_SCHEMA_PREFIX + 'name'))
    dspl_dataset.description = (
        _GetValue(info_element.find(_DSPL_SCHEMA_PREFIX + 'description')))
    dspl_dataset.url = (
        _GetValue(info_element.find(_DSPL_SCHEMA_PREFIX + 'url')))

  provider_element = element_tree.find(_DSPL_SCHEMA_PREFIX + 'provider')

  if provider_element is not None:
    dspl_dataset.provider_name = _GetValue(
        provider_element.find(_DSPL_SCHEMA_PREFIX + 'name'))
    dspl_dataset.provider_url = (
        _GetValue(provider_element.find(_DSPL_SCHEMA_PREFIX + 'url')))

  # Get concepts
  concepts_element = element_tree.find(_DSPL_SCHEMA_PREFIX + 'concepts')

  if concepts_element is not None:
    concept_elements = concepts_element.findall(_DSPL_SCHEMA_PREFIX + 'concept')

    for concept_element in concept_elements:
      dspl_dataset.AddConcept(ElementToConcept(concept_element))

  # Get slices
  slices_element = element_tree.find(_DSPL_SCHEMA_PREFIX + 'slices')

  if slices_element is not None:
    slice_elements = slices_element.findall(_DSPL_SCHEMA_PREFIX + 'slice')

    for slice_element in slice_elements:
      dspl_dataset.AddSlice(ElementToSlice(slice_element, dspl_dataset))

  # Get tables
  tables_element = element_tree.find(_DSPL_SCHEMA_PREFIX + 'tables')

  if tables_element is not None:
    table_elements = tables_element.findall(_DSPL_SCHEMA_PREFIX + 'table')

    for table_element in table_elements:
      dspl_dataset.AddTable(ElementToTable(table_element, csv_path))

  return dspl_dataset


def LoadDSPLFromFiles(xml_file_path):
  """Create a fully populated DSPL DataSet given the argument XML path.

  Args:
    xml_file_path: Path to a DSPL XML file

  Returns:
    dspl_model.DataSet object
  """
  xml_file = codecs.open(xml_file_path, encoding='utf-8', mode='r')

  [xml_model, namespaces] = _NSParser(xml_file)
  xml_file.close()

  return ElementTreeToDataset(
      xml_model, namespaces, os.path.split(xml_file_path)[0])
