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


def ProcessFiles(getter):
  for dim in AsList(getter.json.get('dimension', [])):
    if isinstance(dim.get('codeList'), str):
      codeList = []
      with getter.Fetch(dim['codeList']) as f:
        reader = DictReader(f)
        for row in reader:
          if dim.get('equivalentType'):
            row['@type'] = ['DimensionValue', dim['equivalentType']]
          else:
            row['@type'] = 'DimensionValue'
          row['@id'] = dim['@id'] + '='
          row['@id'] += row['codeValue']
          row['dimension'] = dim['@id']
          codeList.append(row)
      dim['codeList'] = codeList
  if isinstance(getter.json.get('footnote'), str):
    footnotes = []
    with getter.Fetch(getter.json['footnote']) as f:
      reader = DictReader(f)
      for row in reader:
        row['@type'] = 'StatisticalAnnotation'
        row['@id'] = getter.json['@id'] + '#footnote='
        row['@id'] += row['codeValue']
        row['dataset'] = getter.json['@id']
        footnotes.append(row)
    getter.json['footnote'] = footnotes
  for slice in AsList(getter.json.get('slice', [])):
    if isinstance(slice.get('data'), str):
      data = []
      with getter.Fetch(slice['data']) as f:
        reader = DictReader(f)
        for row in reader:
          val = {}
          val['@type'] = 'Observation'
          val['slice'] = slice['@id']
          val['dimensionValues'] = []
          val['measureValues'] = []
          for dim in AsList(slice['dimension']):
            fragment = urlparse(dim).fragment
            val['dimensionValues'].append({
                '@type': 'DimensionValue',
                'dimension': dim,
            })
            for dim_def in AsList(getter.json['dimension']):
              if dim_def['@id'] == dim:
                if dim_def['@type'] == 'CategoricalDimension':
                  val['dimensionValues'][-1]['codeValue'] = row[fragment]
                elif dim_def['@type'] == 'TimeDimension':
                  if dim_def.get('equivalentType'):
                    val['dimensionValues'][-1]['value'] = {
                        '@type': dim_def['equivalentType'],
                        '@value': row[fragment]
                    }
                  else:
                    val['dimensionValues'][-1]['value'] = row[fragment]

          for measure in AsList(slice['measure']):
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
      ret[key] = json_val[key]
    else:
      ret['dataset'][key] = json_val[key]
  return ret
