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

"""Functions for data source to DSPL model conversion."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import itertools

import data_source
from dspllib.model import dspl_model


def _CalculateSlices(column_bundle):
  """Calculate all the possible slices to be produced from a column bundle.

  Args:
    column_bundle: A DataSourceColumnBundle object produced by a data source

  Returns:
    A sequence of DataSourceColumn sequences; each sequence contains the columns
    for one slice.
  """
  all_slices = []

  binary_elements = []
  non_binary_elements = []

  child_parent_dict = {}

  for column in column_bundle.GetColumnIterator():
    if column.rollup:
      binary_elements.append(column)
    else:
      non_binary_elements.append(column)

    if column.parent_ref:
      child_parent_dict[column] = column_bundle.GetColumnByID(column.parent_ref)

  # Expand out slices using powerset operator
  for selection in _Powerset(binary_elements):
    transformed_slice = non_binary_elements + list(selection)

    all_slices.append([s for s in transformed_slice])

  # Prune slices that contain both a concept and its parent
  slices_to_evaluate = []

  for data_slice in all_slices:
    keep_slice = True

    for (key, value) in child_parent_dict.items():
      if key in data_slice and value in data_slice:
        keep_slice = False
        break

    if keep_slice:
      slices_to_evaluate.append(data_slice)

  return slices_to_evaluate


def _Powerset(input_list):
  """Create powerset iterator from the elements in a list.

  Note: Based on example in official Python itertools documentation.

  Example:
    [p for p in Powerset(['a', 'b')] == [(), ('a',), ('b'), ('a', 'b')]

  Args:
    input_list: A sequence of Python objects

  Returns:
    An iterator which loops through all (tuple) elements in the powerset of
    the input_list.
  """
  return (
      itertools.chain.from_iterable(
          itertools.combinations(input_list, r) for r
          in range(len(input_list) + 1)))


def _CreateConceptTable(
    column, instance_data, parent_column=None, verbose=True):
  """Create a DSPL table object that enumerates the instances of a concept.

  If the concept extends 'entity:entity' or 'geo:location', extra columns
  are added to the resulting table for the required inherited properties.
  Otherwise, the table has just a single column.

  By convention, the table id is given as [column_id]_table and the
  corresponding CSV is named [column_id]_table.csv.

  Args:
    column: A DataSourceColumn object corresponding to a dataset dimension
    instance_data: A TableRows object containing a list of concept instances
    parent_column: A DataSourceColumn object corresponding to the parent
                   of this concept
    verbose: Print out status messages to stdout

  Returns:
    A DSPL Table object
  """
  dspl_columns = [dspl_model.TableColumn(column_id=column.column_id,
                                         data_type=column.data_type)]

  if parent_column:
    dspl_columns += [dspl_model.TableColumn(column_id=parent_column.column_id,
                                            data_type=parent_column.data_type)]

  if column.concept_extension == 'entity:entity':
    # Add a 'name' column and populate it with the instance IDs
    dspl_columns += [
        dspl_model.TableColumn(column_id='name', data_type='string')]

    dspl_table_data = instance_data.MergeValues(instance_data).rows
  elif column.concept_extension == 'geo:location':
    # Add 'name', 'latitude', and 'longitude' columns; populate the first with
    # the instance IDs, the others with blank values
    dspl_columns += [
        dspl_model.TableColumn(column_id='name', data_type='string'),
        dspl_model.TableColumn(column_id='latitude', data_type='float'),
        dspl_model.TableColumn(column_id='longitude', data_type='float')]

    dspl_table_data = (instance_data.MergeValues(instance_data)
                       .MergeConstant('').MergeConstant('').rows)
  else:
    dspl_table_data = instance_data.rows

  # Create table, including header row in table data
  concept_table = dspl_model.Table(
      table_id='%s_table' % (column.column_id),
      columns=dspl_columns,
      file_name='%s_table.csv' % (column.column_id),
      table_data=[[c.column_id for c in dspl_columns]] + dspl_table_data,
      verbose=verbose)

  return concept_table


def _CreateSliceTable(slice_columns, table_id, file_name,
                      slice_data, verbose=True):
  """Create a DSPL Table object for a dataset slice.

  Args:
    slice_columns: Sequence of DataSourceColumn objects representing concepts
                   in this slice
    table_id: ID for the table
    file_name: Name of the CSV file containing the table data
    slice_data: A TableRows object containing the data for the slice table
    verbose: Print out status messages to stdout

  Returns:
    A DSPL Table object
  """
  dspl_columns = [
      dspl_model.TableColumn(c.column_id, c.data_type, c.data_format)
      for c in slice_columns]

  # Create table, including header row in table data
  slice_table = dspl_model.Table(
      table_id=table_id,
      columns=dspl_columns,
      file_name=file_name,
      table_data=[[c.column_id for c in dspl_columns]] + slice_data.rows,
      verbose=verbose)

  return slice_table


def PopulateDataset(data_source_obj, verbose):
  """Create a DSPL dataset from a data source.

  Loops through the set of possible slices (provided by the _CalculateSlices
  function), creating the necessary DSPL concept, slice, and table objects as
  needed.

  The following naming convention is used:

    DSPL concept ID                  := DataSource column ID
    DSPL table ID for concept tables := DSPL concept ID + "_table"
    DSPL slice ID                    := "slice_" + n, where n=0,1,2,...
    DSPL table ID for slice tables   := DSPL slice ID + "_table"
    DSPL table file name             := DSPL table ID + ".csv"

  Args:
    data_source_obj: An object that implements the DataSource interface
    verbose: Print out status messages to stdout

  Returns:
    A DSPL DataSet object
  """
  column_bundle = data_source_obj.GetColumnBundle()
  dataset = dspl_model.DataSet(verbose=verbose)

  # Add standard imports
  dataset.AddImport(
      dspl_model.Import(
          namespace_id='entity',
          namespace_url=(
              'http://www.google.com/publicdata/dataset/google/entity')))
  dataset.AddImport(
      dspl_model.Import(
          namespace_id='geo',
          namespace_url=(
              'http://www.google.com/publicdata/dataset/google/geo')))
  dataset.AddImport(
      dspl_model.Import(
          namespace_id='geo_us',
          namespace_url=(
              'http://www.google.com/publicdata/dataset/google/geo/us')))
  dataset.AddImport(
      dspl_model.Import(
          namespace_id='quantity',
          namespace_url=(
              'http://www.google.com/publicdata/dataset/google/quantity')))
  dataset.AddImport(
      dspl_model.Import(
          namespace_id='time',
          namespace_url=(
              'http://www.google.com/publicdata/dataset/google/time')))
  dataset.AddImport(
      dspl_model.Import(
          namespace_id='unit',
          namespace_url=(
              'http://www.google.com/publicdata/dataset/google/unit')))

  # Store concept ID to column ID mappings for imported dimension concepts
  dimension_map = {}

  # Generate concept metadata
  for column in column_bundle.GetColumnIterator():
    if column.slice_role == 'metric':
      metric_concept = dspl_model.Concept(
          concept_id=column.column_id,
          concept_extension_reference=column.concept_extension,
          data_type=column.data_type)
      dataset.AddConcept(metric_concept)
    else:
      # Add dimension concept
      if column.concept_ref:
        # Dimension concept is imported; no need to enumerate instances
        dimension_concept = dspl_model.Concept(
            concept_id=column.column_id,
            concept_reference=column.concept_ref,
            data_type=column.data_type)

        dimension_map[column.concept_ref] = column.column_id
      else:
        # Dimension defined inside the dataset; need to enumerate instances
        if verbose:
          print ('Enumerating instances of \'%s\' concept' %
                 (column.column_id))

        if column.parent_ref:
          parent_column = column_bundle.GetColumnByID(column.parent_ref)
          query_column_ids = [column.column_id, column.parent_ref]
        else:
          parent_column = None
          query_column_ids = [column.column_id]

        concept_table_rows = data_source_obj.GetTableData(
            data_source.QueryParameters(
                query_type=data_source.QueryParameters.CONCEPT_QUERY,
                column_ids=query_column_ids))

        dataset.AddTable(
            _CreateConceptTable(
                column, concept_table_rows, parent_column, verbose))

        dimension_concept = dspl_model.Concept(
            concept_id=column.column_id,
            concept_extension_reference=column.concept_extension,
            data_type=column.data_type,
            table_ref='%s_table' % (column.column_id))

        if column.parent_ref:
          # Add in parent reference property
          dimension_concept.properties.append(
              dspl_model.Property(column.parent_ref, True))

      dataset.AddConcept(dimension_concept)

  # Generate slice metadata
  for i, slice_column_set in enumerate(_CalculateSlices(column_bundle)):
    if verbose:
      print 'Evaluating slice: %s' % ([c.column_id for c in slice_column_set])

    dimension_ids = []
    metric_ids = []

    for column in slice_column_set:
      if column.slice_role == 'dimension':
        dimension_ids.append(column.column_id)
      else:
        metric_ids.append(column.column_id)

    # Execute slice query
    if verbose:
      print 'Getting slice values'

    slice_table_rows = data_source_obj.GetTableData(
        data_source.QueryParameters(
            query_type=data_source.QueryParameters.SLICE_QUERY,
            column_ids=[c.column_id for c in slice_column_set]))

    # Add slice and table metadata to dataset model
    slice_table = _CreateSliceTable(
        slice_column_set,
        'slice_%d_table' % i,
        'slice_%d_table.csv' % i,
        slice_table_rows,
        verbose)

    dataset.AddTable(slice_table)

    new_slice = dspl_model.Slice(
        slice_id='slice_%d' % (i),
        dimension_refs=dimension_ids,
        metric_refs=metric_ids,
        dimension_map=dimension_map,
        table_ref='slice_%d_table' % i)

    dataset.AddSlice(new_slice)

  return dataset
