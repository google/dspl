# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from csv import DictReader
from urllib.parse import urlparse
from dspl2.jsonutil import AsList, GetSchemaId, GetSchemaProp, MakeIdKeyedDict


def _ExpandCodeList(dim, getter):
  """Load a code list from CSV and return a list of JSON-LD objects."""
  codeList = []
  with getter.Fetch(GetSchemaProp(dim, 'codeList')) as f:
    reader = DictReader(f)
    for row in reader:
      if GetSchemaProp(dim, 'equivalentType'):
        row['@type'] = ['DimensionValue', GetSchemaProp(dim, 'equivalentType')]
      else:
        row['@type'] = 'DimensionValue'
      row['@id'] = GetSchemaId(dim) + '='
      row['@id'] += row['codeValue']
      row['dimension'] = GetSchemaId(dim)
      codeList.append(row)
  return codeList


def _ExpandFootnotes(filename, getter):
  """Load footnotes from CSV and return a list of JSON-LD objects."""
  footnotes = []
  with getter.Fetch(filename) as f:
    reader = DictReader(f)
    for row in reader:
      row['@type'] = 'StatisticalAnnotation'
      row['@id'] = GetSchemaId(getter.json) + '#footnote='
      row['@id'] += row['codeValue']
      row['dataset'] = GetSchemaId(getter.json)
      footnotes.append(row)
  return footnotes


def _ExpandSliceData(slice, getter, dim_defs_by_id):
  data = []
  with getter.Fetch(GetSchemaProp(slice, 'data')) as f:
    reader = DictReader(f)
    for row in reader:
      val = {}
      val['@type'] = 'Observation'
      val['slice'] = GetSchemaId(slice)
      val['dimensionValues'] = []
      val['measureValues'] = []
      for dim in AsList(GetSchemaProp(slice, 'dimension')):
        fragment = urlparse(dim).fragment
        dim_val = {
            '@type': 'DimensionValue',
            'dimension': dim,
        }
        dim_def = dim_defs_by_id.get(dim)
        if dim_def:
          if GetSchemaProp(dim_def, '@type') == 'CategoricalDimension':
            dim_val['codeValue'] = row[fragment]
          elif GetSchemaProp(dim_def, '@type') == 'TimeDimension':
            if GetSchemaProp(dim_def, 'equivalentType'):
              dim_val['value'] = {
                  '@type': GetSchemaProp(dim_def, 'equivalentType'),
                  '@value': row[fragment]
              }
            else:
              val['dimensionValues'][-1]['value'] = row[fragment]
        val['dimensionValues'].append(dim_val)

      for measure in AsList(GetSchemaProp(slice, 'measure')):
        fragment = urlparse(measure).fragment
        val['measureValues'].append({
            '@type': 'MeasureValue',
            'measure': measure,
            'value': row[fragment]
        })
        if row.get(fragment + '*'):
          val['measureValues'][-1]['footnote'] = [
              {
                  '@type': 'StatisticalAnnotation',
                  'codeValue': footnote
              }
              for footnote in row[fragment + '*'].split(';')
          ]
      data.append(val)
  return data


def ExpandStatisticalDataset(getter):
  """Expand CSV files referred to in a StatisticalDataset."""

  for dim in AsList(GetSchemaProp(getter.json, 'dimension')):
    if isinstance(dim.get('codeList'), str):
      dim['codeList'] = _ExpandCodeList(dim, getter)
  if isinstance(GetSchemaProp(getter.json, 'footnote'), str):
    getter.json['footnote'] = _ExpandFootnotes(
        GetSchemaProp(getter.json, 'footnote'), getter)
  for slice in AsList(GetSchemaProp(getter.json, 'slice')):
    dim_defs_by_id = MakeIdKeyedDict(
        AsList(GetSchemaProp(getter.json, 'dimension')))
    if isinstance(GetSchemaProp(slice, 'data'), str):
      slice['data'] = _ExpandSliceData(slice, getter, dim_defs_by_id)
  return getter.json
