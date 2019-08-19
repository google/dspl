# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from csv import DictReader
from urllib.parse import urlparse


def AsList(val):
  if isinstance(val, list):
    return val
  return [val]


def GetSchemaProp(obj, key, default=None):
  return obj.get(key, obj.get('schema:' + key, default))


def ProcessFiles(getter):
  for dim in AsList(getter.json.get('dimension', [])):
    if isinstance(dim.get('codeList'), str):
      codeList = []
      with getter.Fetch(GetSchemaProp(dim, 'codeList')) as f:
        reader = DictReader(f)
        for row in reader:
          if dim.get('equivalentType'):
            row['@type'] = ['DimensionValue', GetSchemaProp(dim, 'equivalentType')]
          else:
            row['@type'] = 'DimensionValue'
          row['@id'] = GetSchemaProp(dim, '@id') + '='
          row['@id'] += row['codeValue']
          row['dimension'] = GetSchemaProp(dim, '@id')
          codeList.append(row)
      dim['codeList'] = codeList
  if isinstance(GetSchemaProp(getter.json, 'footnote'), str):
    footnotes = []
    with getter.Fetch(GetSchemaProp(getter.json, 'footnote')) as f:
      reader = DictReader(f)
      for row in reader:
        row['@type'] = 'StatisticalAnnotation'
        row['@id'] = GetSchemaProp(getter.json, '@id') + '#footnote='
        row['@id'] += row['codeValue']
        row['dataset'] = GetSchemaProp(getter.json, '@id')
        footnotes.append(row)
    getter.json['footnote'] = footnotes
  for slice in AsList(GetSchemaProp(getter.json, 'slice', [])):
    if isinstance(GetSchemaProp(slice, 'data'), str):
      data = []
      with getter.Fetch(GetSchemaProp(slice, 'data')) as f:
        reader = DictReader(f)
        for row in reader:
          val = {}
          val['@type'] = 'Observation'
          val['slice'] = GetSchemaProp(slice, '@id')
          val['dimensionValues'] = []
          val['measureValues'] = []
          for dim in AsList(GetSchemaProp(slice, 'dimension')):
            fragment = urlparse(dim).fragment
            val['dimensionValues'].append({
                '@type': 'DimensionValue',
                'dimension': dim,
            })
            for dim_def in AsList(GetSchemaProp(getter.json, 'dimension')):
              if GetSchemaProp(dim_def, '@id') == dim:
                if GetSchemaProp(dim_def, '@type') == 'CategoricalDimension':
                  val['dimensionValues'][-1]['codeValue'] = row[fragment]
                elif GetSchemaProp(dim_def, '@type') == 'TimeDimension':
                  if GetSchemaProp(dim_def, 'equivalentType'):
                    val['dimensionValues'][-1]['value'] = {
                        '@type': GetSchemaProp(dim_def, 'equivalentType'),
                        '@value': row[fragment]
                    }
                  else:
                    val['dimensionValues'][-1]['value'] = row[fragment]

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
      slice['data'] = data
  return getter.json


def JsonToKwArgsDict(json_val):
  """Collects dataset metadata under a "dataset" key"""
  ret = {'dataset': {}}
  special_keys = {'dimension', 'measure', 'footnote', 'slice'}
  for key in json_val:
    if key in special_keys:
      ret[key] = GetSchemaProp(json_val, key)
    else:
      ret['dataset'][key] = GetSchemaProp(json_val, key)
  return ret
