# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from dspl2.jsonutil import (
    AsList, GetSchemaId, GetSchemaProp, GetSchemaType, GetUrl, MakeIdKeyedDict)


def _CheckPropertyPresent(name, obj, prop, category, expected=None):
  val = GetSchemaProp(obj, prop)
  if not val:
    print(f'{name} property "{prop}" is {category}')
  elif expected and val != expected:
    print(f'{name} property "{prop}" has value "{val}" but expected "{expected}"')


def _CheckAnyPropertyPresent(name, obj, props, category):
  if not any(GetSchemaProp(obj, prop) for prop in props):
    print(f'{name}: One property of {props} is {category}')


def _CheckIdPresent(name, obj):
  if not GetSchemaId(obj):
    print(f'{name} has no "@id"')


def _CheckType(name, obj, typelist=[]):
  type = GetSchemaType(obj)
  if not type:
    print(f'{name} has no "@type"')
  elif typelist and type not in typelist:
    print(f'{name} has unexpected type: "{type}" expected: {typelist}')


def CheckDataset(dataset):
  _CheckPropertyPresent('Dataset', dataset, 'description', 'required')
  _CheckPropertyPresent('Dataset', dataset, 'name', 'required')
  _CheckPropertyPresent('Dataset', dataset, 'alternateName', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'creator', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'citation', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'identifier', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'keywords', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'license', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'sameAs', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'spatialCoverage', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'temporalCoverage', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'variableMeasured', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'version', 'recommended')
  _CheckPropertyPresent('Dataset', dataset, 'url', 'recommended')


def CheckDimension(dim, dsid):
  _CheckIdPresent('Dimension', dim)
  _CheckType('Dimension', dim, ['TimeDimension', 'CategoricalDimension'])
  _CheckPropertyPresent('Dimension', dim, 'dataset',
                        'required for id ' + GetSchemaId(dim), dsid)
  type = GetSchemaType(dim)
  if type == 'TimeDimension':
    _CheckPropertyPresent('Dimension', dim, 'dateFormat',
                          'required for id ' + GetSchemaId(dim))
  elif type == 'CategoricalDimension':
    _CheckPropertyPresent('Dimension', dim, 'codeList',
                          'required for id ' + GetSchemaId(dim))


def CheckMeasure(measure, dsid):
  _CheckIdPresent('Measure', measure)
  _CheckType('Measure', measure, ['StatisticalMeasure'])
  _CheckPropertyPresent('Measure', measure, 'dataset',
                        'required for id ' + GetSchemaId(measure), dsid)
  _CheckAnyPropertyPresent('Measure', measure, ['unitType', 'unitText'],
                           'recommended')


def CheckSliceData(slicedata, slice_id):
  if isinstance(slicedata, str):
    print(f'Observation: data must be one URL or a list of observations for slice {slice_id}')
  else:
    _CheckPropertyPresent('Observation', slicedata, 'slice', 'required',
                          slice_id)


def CheckSlice(slice, dsid):
  _CheckIdPresent('Slice', slice)
  _CheckType('Slice', slice, ['DataSlice'])
  _CheckPropertyPresent('Slice', slice, 'dataset',
                        'required for id ' + GetSchemaId(slice), dsid)
  _CheckPropertyPresent('Slice', slice, 'dimension', 'required')

  dims = GetSchemaProp(slice, 'dimension')
  if not isinstance(dims, list):
    print(f'Slice property "dimension" value is required to be a list for {GetSchemaId(slice)}')
  for dim in dims:
    url = GetUrl(dim)
    if not url:
      print(f'Slice property "dimension" values must have URLs for {GetSchemaId(slice)}')

  _CheckPropertyPresent('Slice', slice, 'measure', 'required')
  measures = GetSchemaProp(slice, 'measure')
  if not isinstance(measures, list):
    print(f'Slice property "measure" value is required to be a list for {GetSchemaId(slice)}')
  for measure in measures:
    url = GetUrl(measure)
    if not url:
      print(f'Slice property "measure" values must have URLs for {GetSchemaId(slice)}')

  _CheckPropertyPresent('Slice', slice, 'data', 'required')
  data = GetSchemaProp(slice, 'data')
  if not isinstance(data, str):
    if isinstance(data, dict):
      CheckSliceData(data, GetSchemaId(slice))
    elif isinstance(data, list):
      for datum in data:
        CheckSliceData(datum, GetSchemaId(slice))


def CheckStatisticalDataset(dataset):
  _CheckType('StatisticalDataset', dataset, ['StatisticalDataset'])
  _CheckIdPresent('StatisticalDataset', dataset)
  _CheckPropertyPresent('StatisticalDataset', dataset, 'dimension', 'required')
  for dim in AsList(GetSchemaProp(dataset, 'dimension')):
    CheckDimension(dim, GetSchemaId(dataset))
  _CheckPropertyPresent('StatisticalDataset', dataset, 'measure', 'required')
  for measure in AsList(GetSchemaProp(dataset, 'measure')):
    CheckMeasure(measure, GetSchemaId(dataset))
  _CheckPropertyPresent('StatisticalDataset', dataset, 'slice', 'required')
  for slice in AsList(GetSchemaProp(dataset, 'slice')):
    CheckSlice(slice, GetSchemaId(dataset))


def ValidateDspl2(dataset):
  CheckDataset(dataset)
  CheckStatisticalDataset(dataset)
