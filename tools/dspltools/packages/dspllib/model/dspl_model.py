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

"""Implementation of the DSPL data model in Python.

Note that not all DSPL features are currently supported (e.g., topics,
concept properties, etc.).
"""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import csv
import os
import xml.dom.minidom
import xml.etree.ElementTree


_VALUE_LANGUAGE = 'en'


class DSPLModelError(Exception):
  """Base class for exceptions in the dspl_model module."""
  pass


def _ValueOrPlaceHolder(value_string, description):
  """Embeds a string inside an XML <value>...</value> element.

  If the string is empty or None, an alternate string is used instead.

  Args:
    value_string: String to embed
    description: String to be used if the value string is empty or None.

  Returns:
    An ElementTree Element object.
  """
  value_element = xml.etree.ElementTree.Element('value')
  value_element.set('xml:lang', _VALUE_LANGUAGE)

  if value_string:
    value_element.text = value_string
  else:
    value_element.text = '** INSERT %s **' % description

  return value_element


class DataSet(object):
  """Top-level representation of a DSPL dataset."""

  def __init__(self, namespace='', name='', description='', url='',
               provider_name='', provider_url='', imports=(), topics=(),
               concepts=(), slices=(), tables=(), verbose=True):
    """Create a new DataSet object.

    Args:
      namespace: Namespace for the dataset
      name: Name of the dataset
      description: Dataset description
      url: Dataset URL
      provider_name: Name of dataset provider
      provider_url: Provider URL
      imports: Sequence of Import objects
      topics: Sequence of Topic objects
      concepts: Sequence of Concept objects
      slices: Sequence of Slice objects
      tables: Sequence of Table objects
      verbose: Print out status messages to stdout
    """
    self.namespace = namespace
    self.name = name
    self.description = description
    self.url = url
    self.provider_name = provider_name
    self.provider_url = provider_url

    self.imports = list(imports)
    self.topics = list(topics)
    self.concepts = list(concepts)
    self.slices = list(slices)
    self.tables = list(tables)

    self.verbose = verbose

  def AddImport(self, import_obj):
    """Add an import to this dataset."""
    self.imports.append(import_obj)

  def GetImport(self, namespace_id):
    """Get the import matching the argument namespace id."""
    for import_obj in self.imports:
      if import_obj.namespace_id == namespace_id:
        return import_obj

    return None

  def AddTopic(self, topic_obj):
    """Add a top-level topic to this dataset."""
    self.topics.append(topic_obj)

  def _TopicSearchHelper(self, topic_list, topic_id):
    """Recursively search a list for the topic with the argument id."""
    for topic_obj in topic_list:
      if topic_obj.topic_id == topic_id:
        return topic_obj
      elif topic_obj.children:
        children_result = self._TopicSearchHelper(topic_obj.children, topic_id)

        if children_result:
          return children_result

    return None

  def GetTopic(self, topic_id):
    """Get the topic matching the argument topic id."""
    return self._TopicSearchHelper(self.topics, topic_id)

  def AddConcept(self, concept):
    """Add a concept to this dataset."""
    self.concepts.append(concept)

  def GetConcept(self, concept_id):
    """Find the concept matching the argument ID."""
    for concept in self.concepts:
      if concept.concept_id == concept_id:
        return concept

    return None

  def AddSlice(self, data_slice):
    """Add a slice to this dataset."""
    self.slices.append(data_slice)

  def GetSlice(self, slice_id):
    """Find slice matching the argument ID."""
    for data_slice in self.slices:
      if data_slice.slice_id == slice_id:
        return data_slice

    return None

  def AddTable(self, table):
    """Add a table to this dataset."""
    self.tables.append(table)

  def GetTable(self, table_id):
    """Find the table matching the argument ID."""
    for table in self.tables:
      if table.table_id == table_id:
        return table

    return None

  def Materialize(self, output_path):
    """Write the dataset XML and CSV files to the argument output path."""
    output_file_name = os.path.join(output_path, 'dataset.xml')

    if self.verbose:
      print 'Writing file: %s' % output_file_name

    # Write XML file
    xml_file = open(output_file_name, 'w')
    xml_file.write(str(self))
    xml_file.close()

    # Write CSV files
    for table in self.tables:
      table.MaterializeData(output_path)

  def ToXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Recursively calls the ToXMLElement method for all of its concept, slice,
    and table children.

    TODO(yolken): Cache results for better performance.

    Returns:
      An ElementTree Element.
    """
    root_element = xml.etree.ElementTree.Element('dspl')

    if self.namespace:
      root_element.set('targetNamespace', self.namespace)

    # Add namespace and imports
    root_element.set('xmlns',
                     'http://schemas.google.com/dspl/2010')

    for import_obj in self.imports:
      root_element.set('xmlns:%s' % import_obj.namespace_id,
                       import_obj.namespace_url)
      root_element.append(import_obj.ToXMLElement())

    # Basic dataset information
    dataset_info = xml.etree.ElementTree.Element('info')

    dataset_name = xml.etree.ElementTree.Element('name')
    dataset_name.append(_ValueOrPlaceHolder(self.name, 'DATASET NAME'))
    dataset_info.append(dataset_name)

    dataset_description = xml.etree.ElementTree.Element('description')
    dataset_description.append(
        _ValueOrPlaceHolder(self.description, 'DATASET DESCRIPTION'))
    dataset_info.append(dataset_description)

    dataset_url = xml.etree.ElementTree.Element('url')
    dataset_url.append(
        _ValueOrPlaceHolder(self.url, 'DATASET URL'))
    dataset_info.append(dataset_url)

    root_element.append(dataset_info)

    # Provider information
    provider_info = xml.etree.ElementTree.Element('provider')

    provider_name = xml.etree.ElementTree.Element('name')
    provider_name.append(
        _ValueOrPlaceHolder(self.provider_name, 'PROVIDER NAME'))
    provider_info.append(provider_name)

    provider_url = xml.etree.ElementTree.Element('url')
    provider_url.append(
        _ValueOrPlaceHolder(self.provider_url, 'PROVIDER URL'))
    provider_info.append(provider_url)

    root_element.append(provider_info)

    # Add topic info
    if self.topics:
      topic_elements = xml.etree.ElementTree.Element('topics')

      for topic in self.topics:
        topic_elements.append(topic.ToXMLElement())

      root_element.append(topic_elements)

    # Add concept info
    concept_elements = xml.etree.ElementTree.Element('concepts')

    for concept in self.concepts:
      if not concept.concept_reference:
        concept_elements.append(concept.ToXMLElement())

    root_element.append(concept_elements)

    # Add slices
    slice_elements = xml.etree.ElementTree.Element('slices')

    for data_slice in self.slices:
      slice_elements.append(data_slice.ToXMLElement(self))

    root_element.append(slice_elements)

    # Add table info
    table_elements = xml.etree.ElementTree.Element('tables')

    for table in self.tables:
      table_elements.append(table.ToXMLElement())

    root_element.append(table_elements)

    return root_element

  def __str__(self):
    """Make a 'pretty' version of the dataset XML, with two-space indents.

    TODO(yolken): Cache results for better performance.

    Returns:
      A string of the dataset XML
    """
    result = xml.dom.minidom.parseString(
        xml.etree.ElementTree.tostring(
            self.ToXMLElement(), encoding='utf-8')).toprettyxml(indent='  ')

    return result


class Import(object):
  """Representation of a DSPL dataset import."""

  def __init__(self, namespace_id='', namespace_url=''):
    """Create a new Import object.

    Args:
      namespace_id: Identifier for the dataset
      namespace_url: URL for the imported dataset
    """
    self.namespace_id = namespace_id
    self.namespace_url = namespace_url

  def ToXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    import_element = xml.etree.ElementTree.Element('import')
    import_element.set('namespace', self.namespace_url)

    return import_element


class Topic(object):
  """Representation of a DSPL topic."""

  def __init__(self, topic_id='', topic_name='', children=()):
    """Create a new Topic object.

    Args:
      topic_id: Identifier for this topic
      topic_name: Name of this topic
      children: Sequence of topics that are the children of this one
    """
    self.topic_id = topic_id
    self.topic_name = topic_name
    self.children = children

  def ToXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    topic_element = xml.etree.ElementTree.Element('topic')
    topic_element.set('id', self.topic_id)

    topic_info = xml.etree.ElementTree.Element('info')
    topic_name = xml.etree.ElementTree.Element('name')

    topic_name.append(
        _ValueOrPlaceHolder(
            self.topic_name,
            'NAME for topic: %s' % self.topic_id))
    topic_info.append(topic_name)
    topic_element.append(topic_info)

    for child_topic in self.children:
      topic_element.append(child_topic.ToXMLElement())

    return topic_element


class Concept(object):
  """Representation of a DSPL concept."""

  def __init__(self, concept_id='', concept_name='', concept_description='',
               data_type='', table_ref='', concept_reference='',
               concept_extension_reference='', topic_references=(),
               attributes=(), properties=()):
    """Create a new Concept object.

    Args:
      concept_id: ID string for the concept
      concept_name: Name of the concept
      concept_description: Description of the concept
      data_type: One of {'boolean', 'date', 'float', 'integer', 'string'}
      table_ref: ID string for the concept's table
      concept_reference: ID string for the (external) concept that this object
                         represents; including a value here means that the
                         metadata will not be materialized to XML
      concept_extension_reference: ID string for the concept this one extends
      topic_references: List of string topic IDs for this concept
      attributes: A list of Attribute instances associated with this concept
      properties: A list of Property instances associated with this concept
    """
    self.concept_id = concept_id
    self.concept_name = concept_name
    self.concept_description = concept_description
    self.data_type = data_type
    self.table_ref = table_ref
    self.concept_reference = concept_reference
    self.concept_extension_reference = concept_extension_reference
    self.topic_references = list(topic_references)
    self.attributes = list(attributes)
    self.properties = list(properties)

  def ToXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    concept_element = xml.etree.ElementTree.Element('concept')
    concept_element.set('id', self.concept_id)

    if self.concept_extension_reference:
      concept_element.set('extends', self.concept_extension_reference)

    concept_info = xml.etree.ElementTree.Element('info')

    concept_name = xml.etree.ElementTree.Element('name')
    concept_name.append(
        _ValueOrPlaceHolder(
            self.concept_name,
            'NAME for concept: %s' % self.concept_id))
    concept_info.append(concept_name)

    concept_description = xml.etree.ElementTree.Element('description')
    concept_description.append(
        _ValueOrPlaceHolder(
            self.concept_description,
            'DESCRIPTION for concept: %s' % self.concept_id))
    concept_info.append(concept_description)

    concept_element.append(concept_info)

    for topic_reference in self.topic_references:
      topic_element = xml.etree.ElementTree.Element('topic')
      topic_element.set('ref', topic_reference)

      concept_element.append(topic_element)

    concept_type = xml.etree.ElementTree.Element('type')
    concept_type.set('ref', self.data_type)
    concept_element.append(concept_type)

    for concept_attribute in self.attributes:
      concept_element.append(concept_attribute.toXMLElement())

    for concept_property in self.properties:
      concept_element.append(concept_property.toXMLElement())

    if self.table_ref:
      concept_table = xml.etree.ElementTree.Element('table')
      concept_table.set('ref', self.table_ref)
      concept_element.append(concept_table)

    return concept_element


class Attribute(object):
  """Representation of a simple DSPL concept attribute.

  For now, this representation is limited to attributes with just a concept
  reference and value.
  """

  def __init__(self, concept_ref='', value=''):
    """Create a new Attribute instance.

    Args:
      concept_ref: String reference to concept
      value: String value for this attribute
    """
    self.concept_ref = concept_ref
    self.value = value

  def toXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    attribute_element = xml.etree.ElementTree.Element('attribute')
    attribute_element.set('concept', self.concept_ref)

    if self.value:
      value_element = xml.etree.ElementTree.Element('value')
      value_element.text = self.value

      attribute_element.append(value_element)

    return attribute_element


class Property(object):
  """Representation of a simple DSPL concept property.

  For now, this representation is limited to properties with just a concept
  reference and (optional) isParent attribute.
  """

  def __init__(self, concept_ref='', is_parent=False):
    """Create a new Property instance.

    Args:
      concept_ref: String reference to concept
      is_parent: Boolean representing whether the previous is this concept's
                 parent
    """
    self.concept_ref = concept_ref
    self.is_parent = is_parent

  def toXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    property_element = xml.etree.ElementTree.Element('property')
    property_element.set('concept', self.concept_ref)

    if self.is_parent:
      property_element.set('isParent', 'true')

    return property_element


class Slice(object):
  """Representation of a DSPL slice."""

  def __init__(self, slice_id='', dimension_refs=(), metric_refs=(),
               dimension_map=(), metric_map=(), table_ref=''):
    """Create a new Slice object.

    Args:
      slice_id: ID string for this slice
      dimension_refs: Sequence of concept ids (immutable after initialization)
      metric_refs: Sequence of concept ids (immutable after initialization)
      dimension_map: Map of dimension IDs to column IDs (if not the same)
      metric_map: Map of metric IDs to column IDs (if not the same)
      table_ref: String ID of this slice's table
    """
    self.slice_id = slice_id
    self.dimension_refs = tuple(dimension_refs)
    self.metric_refs = tuple(metric_refs)
    self.dimension_map = dict(dimension_map)
    self.metric_map = dict(metric_map)
    self.table_ref = table_ref

  def ToXMLElement(self, dataset):
    """Convert object to its ElementTree XML representation.

    Args:
      dataset: DataSet object that this slice belongs to.

    Returns:
      An ElementTree Element.
    """
    slice_element = xml.etree.ElementTree.Element('slice')
    slice_element.set('id', self.slice_id)

    dimension_mapping_elements = []
    metric_mapping_elements = []

    for dimension_ref in self.dimension_refs:
      dimension = dataset.GetConcept(dimension_ref)

      new_dimension = xml.etree.ElementTree.Element('dimension')
      new_dimension.set('concept', dimension.concept_id)
      slice_element.append(new_dimension)

      # Handle dimension->column mappings
      if dimension.concept_id in self.dimension_map:
        dimension_mapping_element = (
            xml.etree.ElementTree.Element('mapDimension'))
        dimension_mapping_element.set('concept', dimension.concept_id)
        dimension_mapping_element.set('toColumn',
                                      self.dimension_map[dimension.concept_id])
        dimension_mapping_elements.append(dimension_mapping_element)

    for metric_ref in self.metric_refs:
      metric = dataset.GetConcept(metric_ref)

      new_metric = xml.etree.ElementTree.Element('metric')
      new_metric.set('concept', metric.concept_id)
      slice_element.append(new_metric)

      # Handle metric->column metrics
      if metric.concept_id in self.metric_map:
        metric_mapping_element = (
            xml.etree.ElementTree.Element('mapMetric'))
        metric_mapping_element.set('concept', metric.concept_id)
        metric_mapping_element.set('toColumn',
                                   self.metric_map[metric.concept_id])
        metric_mapping_elements.append(metric_mapping_element)

    if self.table_ref:
      slice_table = xml.etree.ElementTree.Element('table')
      slice_table.set('ref', self.table_ref)

      for mapping_element in (
          dimension_mapping_elements + metric_mapping_elements):
        slice_table.append(mapping_element)

      slice_element.append(slice_table)

    return slice_element


class TableColumn(object):
  """A column in a DSPL table."""

  def __init__(self, column_id='', data_type='', data_format='',
               constant_value=''):
    """Create a new TableColumn object.

    Args:
      column_id: String ID for the column
      data_type: One of {'boolean', 'date', 'float', 'integer', 'string'}
      data_format: Formatting string for this column
      constant_value: A constant value for this column
    """
    self.column_id = column_id
    self.data_type = data_type
    self.data_format = data_format
    self.constant_value = constant_value

  def ToXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    column_element = xml.etree.ElementTree.Element('column')
    column_element.set('id', self.column_id)
    column_element.set('type', self.data_type)

    if self.data_format:
      column_element.set('format', self.data_format)

    if self.constant_value:
      column_value_element = xml.etree.ElementTree.Element('value')
      column_value_element.text = self.constant_value
      column_element.append(column_value_element)

    return column_element


class Table(object):
  """Representation of a DSPL table."""

  def __init__(self, table_id='', columns=(),
               file_name='', table_data=(), verbose=True):
    """Create a new Table object.

    Args:
      table_id: String ID for the table
      columns: Sequence of TableColumn objects
      file_name: Name of the file associated with this table
      table_data: Sequence of sequences, one for each row in the table
      verbose: Print out status messages to stdout
    """
    self.table_id = table_id
    self.columns = list(columns)
    self.file_name = file_name
    self.table_data = list(table_data)
    self.verbose = verbose

  def MaterializeData(self, output_path):
    """Write table data to CSV, using argument path."""
    output_file_name = os.path.join(output_path, self.file_name)

    if self.verbose:
      print 'Writing file: %s' % output_file_name

    csv_output_file = open(output_file_name, 'wb')
    csv_writer = csv.writer(csv_output_file)

    for row in self.table_data:
      csv_writer.writerow(row)

    csv_output_file.close()

  def ToXMLElement(self):
    """Convert object to its ElementTree XML representation.

    Returns:
      An ElementTree Element.
    """
    table_element = xml.etree.ElementTree.Element('table')
    table_element.set('id', self.table_id)

    for column in self.columns:
      table_element.append(column.ToXMLElement())

    table_data = xml.etree.ElementTree.Element('data')
    table_data_file = xml.etree.ElementTree.Element('file')
    table_data_file.set('encoding', 'utf-8')
    table_data_file.set('format', 'csv')
    table_data_file.text = self.file_name

    table_data.append(table_data_file)

    table_element.append(table_data)

    return table_element
