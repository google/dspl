# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd


def AsList(val):
  """Ensures the JSON-LD object is a list."""
  if isinstance(val, list):
    return val
  elif val is None:
    return []
  else:
    return [val]


def GetSchemaProp(obj, key, default=None):
  return obj.get(key, obj.get('schema:' + key, default))


def JsonToKwArgsDict(json_val):
  """Turn a StatisticalDataset object into a kwargs dict for a Jinja2 template.

  Specifically, this collects top-level dataset metadata under a "dataset" key,
  and keeps dimensions, measures, footnotes, and slices as they are.
  """
  ret = {'dataset': {}}
  special_keys = {'dimension', 'measure', 'footnote', 'slice'}
  for key in json_val:
    if key in special_keys:
      ret[key] = GetSchemaProp(json_val, key)
    else:
      ret['dataset'][key] = GetSchemaProp(json_val, key)
  return ret


def MakeIdKeyedDict(vals):
  """Returns a dict mapping objects' IDs to objects in the provided list.

  Given a list of JSON-LD objects, return a dict mapping each element's ID to the
  element.

  Parameters:
  vals (list): list of JSON-LD objects with IDs as dicts

  Returns
  dict:dict whose values are elements of `vals` and whose keys are their IDs.
  """
  ret = {}
  for val in vals:
    id = GetSchemaProp(val, '@id')
    if id:
      ret[id] = val
  return ret


def GetSchemaId(obj):
  return obj.get('@id', GetSchemaProp(obj, 'id'))
