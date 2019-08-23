# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from dspl2.jsonutil import (
    AsList, GetSchemaId, GetSchemaProp, GetSchemaType, GetUrl, MakeIdKeyedDict)
from dspl2.rdfutil import LoadGraph, SelectFromGraph
import json


def _CheckPropertyPresent(warnings, name, obj, prop, category, expected=None):
  val = GetSchemaProp(obj, prop)
  if val is None:
    warnings.append(f'{name} property "{prop}" is {category}')
  elif expected and val != expected:
    warnings.append(f'{name} property "{prop}" has value "{val}" but expected "{expected}"')


def _CheckUrlPresent(warnings, name, obj, prop, category, expected=None):
  val = GetUrl(GetSchemaProp(obj, prop))
  if val is None:
    warnings.append(f'{name} property "{prop}" is {category}')
  elif expected and val != expected:
    warnings.append(f'{name} property "{prop}" has value "{val}" but expected "{expected}"')


def _CheckAnyPropertyPresent(warnings, name, obj, props, category):
  if not any(GetSchemaProp(obj, prop) for prop in props):
    warnings.append(f'{name}: One property of {props} is {category}')


def _CheckIdPresent(warnings, name, obj):
  if GetSchemaId(obj) is None:
    warnings.append(f'{name} has no "@id"')


def _CheckType(warnings, name, obj, typelist=[]):
  type = GetSchemaType(obj)
  if type is None:
    warnings.append(f'{name} has no "@type"')
  elif typelist and type not in typelist:
    warnings.append(f'{name} has unexpected type: "{type}" expected: {typelist}')


def CheckDataset(warnings, dataset):
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'description', 'required')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'name', 'required')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'alternateName', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'creator', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'citation', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'identifier', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'keywords', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'license', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'sameAs', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'spatialCoverage', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'temporalCoverage', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'variableMeasured', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'version', 'recommended')
  _CheckPropertyPresent(warnings, 'Dataset', dataset, 'url', 'recommended')


def CheckDimension(warnings, dim, dsid):
  _CheckIdPresent(warnings, 'Dimension', dim)
  _CheckType(warnings, 'Dimension', dim,
             ['TimeDimension', 'CategoricalDimension'])
  _CheckUrlPresent(warnings, 'Dimension', dim, 'dataset',
                        'required for id ' + GetSchemaId(dim), dsid)
  type = GetSchemaType(dim)
  if type == 'TimeDimension':
    _CheckPropertyPresent(warnings, 'Dimension', dim, 'dateFormat',
                          'required for id ' + GetSchemaId(dim))
  elif type == 'CategoricalDimension':
    _CheckPropertyPresent(warnings, 'Dimension', dim, 'codeList',
                          'required for id ' + GetSchemaId(dim))


def CheckMeasure(warnings, measure, dsid):
  _CheckIdPresent(warnings, 'Measure', measure)
  _CheckType(warnings, 'Measure', measure, ['StatisticalMeasure'])
  _CheckUrlPresent(warnings, 'Measure', measure, 'dataset',
                        'required for id ' + GetSchemaId(measure), dsid)
  _CheckAnyPropertyPresent(warnings, 'Measure', measure,
                           ['unitType', 'unitText'], 'recommended')


def CheckSliceData(warnings, slicedata, slice_id):
  if isinstance(slicedata, str):
    warnings.append(f'Observation: data must be one URL or a list of observations for slice {slice_id}')
  else:
    _CheckPropertyPresent(warnings, 'Observation', slicedata, 'slice', 'required',
                          slice_id)


def CheckSlice(warnings, slice, dsid):
  _CheckIdPresent(warnings, 'Slice', slice)
  slice_id = GetSchemaId(slice)
  _CheckType(warnings, 'Slice', slice, ['DataSlice'])
  _CheckUrlPresent(warnings, 'Slice', slice, 'dataset',
                   'required for id ' + slice_id, dsid)
  _CheckPropertyPresent(warnings, 'Slice', slice, 'dimension', 'required')

  dims = AsList(GetSchemaProp(slice, 'dimension'))
  for dim in dims:
    url = GetUrl(dim)
    if url is None:
      warnings.append(f'Slice property "dimension" values must have URLs for {slice_id}')

  _CheckPropertyPresent(warnings, 'Slice', slice, 'measure', 'required')
  measures = AsList(GetSchemaProp(slice, 'measure'))
  for measure in measures:
    url = GetUrl(measure)
    if url is None:
      warnings.append(f'Slice property "measure" values must have URLs for {slice_id}')

  _CheckPropertyPresent(warnings, 'Slice', slice, 'data', 'required')
  data = GetSchemaProp(slice, 'data')
  if not isinstance(data, str):
    if isinstance(data, dict):
      CheckSliceData(warnings, data, slice_id)
    elif isinstance(data, list):
      for datum in data:
        CheckSliceData(warnings, datum, slice_id)


def CheckStatisticalDataset(warnings, dataset):
  _CheckType(warnings, 'StatisticalDataset', dataset, ['StatisticalDataset'])
  _CheckIdPresent(warnings, 'StatisticalDataset', dataset)
  _CheckPropertyPresent(warnings, 'StatisticalDataset', dataset, 'dimension',
                        'required')
  for dim in AsList(GetSchemaProp(dataset, 'dimension')):
    CheckDimension(warnings, dim, GetSchemaId(dataset))
  _CheckPropertyPresent(warnings, 'StatisticalDataset', dataset, 'measure',
                        'required')
  for measure in AsList(GetSchemaProp(dataset, 'measure')):
    CheckMeasure(warnings, measure, GetSchemaId(dataset))
  _CheckPropertyPresent(warnings, 'StatisticalDataset', dataset, 'slice',
                        'required')
  for slice in AsList(GetSchemaProp(dataset, 'slice')):
    CheckSlice(warnings, slice, GetSchemaId(dataset))


def CheckRdfConstraints(warnings, graph):
  # Check dataset ID
  results = SelectFromGraph(
      graph,
      ('?ds', 'a', 'schema:StatisticalDataset'),
  )
  if not results or not results[0]['ds']:
    warnings.append("RDF: StatisticalDataset ID not found")

  # Check all slice dimensions are present
  results = SelectFromGraph(
      graph,
      ('?ds', 'a', 'schema:StatisticalDataset'),
      ('?ds', 'schema:dimension', '?dim'),
  )
  dims = set(result['dim'] for result in results)
  if not dims:
    warnings.append('RDF: No dataset dimensions found')
  results = SelectFromGraph(
      graph,
      ('?slice', 'a', 'schema:DataSlice'),
      ('?slice', 'schema:dimension', '?dim'),
  )
  slice_dims = set(result['dim'] for result in results)
  excess_dims = slice_dims - dims
  if excess_dims:
    warnings.append(f'RDF: undefined dimensions found in slice: {excess_dims}; expected={dims}')

  # Check all slice measures are present
  results = SelectFromGraph(
      graph,
      ('?ds', 'a', 'schema:StatisticalDataset'),
      ('?ds', 'schema:measure', '?measure'),
  )
  measures = set(result['measure'] for result in results)
  if not measures:
    warnings.append('RDF: No dataset measures found')
  results = SelectFromGraph(
      graph,
      ('?slice', 'a', 'schema:DataSlice'),
      ('?slice', 'schema:measure', '?measure'),
  )
  slice_measures = set(result['measure'] for result in results)
  excess_measures = slice_measures - measures
  if excess_measures:
    warnings.append(f'RDF: undefined measures found in slice: {excess_measures}; expected={measures}')

  # Check all measurevalue footnotes are present
  results = SelectFromGraph(
      graph,
      ('?ds', 'a', 'schema:StatisticalDataset'),
      ('?ds', 'schema:footnote', '?footnote'),
      ('?footnote', 'schema:codeValue', '?codeValue'),
  )
  footnotes = set(result['codeValue'] for result in results)
  if not footnotes:
    warnings.append('RDF: No dataset footnotes found')
  results = SelectFromGraph(
      graph,
      ('?val', 'a', 'schema:MeasureValue'),
      ('?val', 'schema:footnote', '?footnote'),
      ('?footnote', 'schema:codeValue', '?codeValue'),
  )
  slice_footnotes = set(result['codeValue'] for result in results)
  excess_footnotes = slice_footnotes - footnotes
  if excess_footnotes:
    warnings.append(f'RDF: undefined footnotes found in slice: {excess_footnotes}; expected={footnotes}')


def ValidateDspl2(dataset, getter):
  warnings = []
  CheckDataset(warnings, dataset)
  CheckStatisticalDataset(warnings, dataset)
  CheckRdfConstraints(warnings, getter.graph)
  return warnings
