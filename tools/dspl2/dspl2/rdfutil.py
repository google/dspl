# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import json
from pathlib import Path
from pyld import jsonld
from rdflib import Graph, Namespace
from rdflib.serializer import Serializer
import sys

from dspl2.jsonutil import AsList


SCHEMA = Namespace('http://schema.org/')


_Schema = {}
_Context = {}
_DataFileFrame = {
    '@context': [_Context, {'schema': 'http://schema.org/'}],
    '@type': 'StatisticalDataset',
    'slice': {
        'dimension': {
            '@embed': '@never'
        },
        'measure': {
            '@embed': '@never'
        },
    }
}
_FullFrame = {
    '@context': [_Context, {'schema': 'http://schema.org/'}],
    '@type': 'StatisticalDataset',
    'slice': {
        'dimension': {
            '@embed': '@never'
        },
        'measure': {
            '@embed': '@never'
        },
        'data': {
            'dimensionValues': {
                'dimension': {
                    '@embed': '@never'
                }
            },
            'measureValues': {
                'measure': {
                    '@embed': '@never'
                },
                'footnote': {
                    '@embed': '@never'
                }
            }
        }
    }
}
_Initialized = False
_Module_path = Path(__file__).parent
_RdfPrefixes = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'schema': 'http://schema.org/',
}


def _Init(context, schema):
  global _Context, _Schema, _Initialized
  if not _Initialized:
    with schema.open() as schema:
      _Schema.update(json.load(schema))
    with context.open() as context:
      _Context.update(json.load(context))
    del _Context['@context']['id']
    del _Context['@context']['type']
    _Initialized = True


def _LoadJsonLd(json_val, public_id):
  _Init(_Module_path / 'schema' / 'jsonldcontext.json',
        _Module_path / 'schema' / 'schema.jsonld')
  json_val['@context'] = _Context
  graph = Graph().parse(
      data=json.dumps(json_val).encode('utf-8'),
      format='json-ld',
      publicID=public_id
  )
  return graph


def LoadGraph(input, public_id):
  if isinstance(input, dict):
    data = input
  elif isinstance(input, str):
    data = json.loads(input)
  else:
    data = json.load(input)

  return _LoadJsonLd(data, public_id)


def FrameGraph(graph, frame=_FullFrame):
  serialized = graph.serialize(format='json-ld', indent=2)
  json_val = json.loads(serialized)
  json_val = {
      '@context': _Context,
      '@graph': AsList(json_val)
  }
  framed = jsonld.frame(json_val, frame)
  framed['@context'] = 'http://schema.org'
  for items in framed['@graph']:
    framed.update(items)
  del framed['@graph']
  return framed


def _N3(obj, namespace_manager):
  if isinstance(obj, str):
    return obj
  return obj.n3(namespace_manager=namespace_manager)


def MakeSparqlSelectQuery(*constraints,
                          ns_manager=None,
                          rdf_prefixes=_RdfPrefixes):
  ret = ''
  for prefix, url in rdf_prefixes.items():
    ret += f'PREFIX {prefix}: <{url}>\n'
  ret += 'SELECT * WHERE {\n'
  for constraint in constraints:
    sub, pred, obj = (_N3(field, ns_manager)
                      for field in constraint)
    ret += f'    {sub} {pred} {obj} .\n'
  ret += '}'
  return ret


def SelectFromGraph(graph, *constraints):
  result = graph.query(
      MakeSparqlSelectQuery(
          *constraints,
          ns_manager=graph.namespace_manager))
  return list({str(k): str(v)
               for k, v in binding.items()}
              for binding in result.bindings)


def main(args, context, schema):
  with open(args[1]) as f:
    normalized = FrameGraph(LoadGraph(f, args[1]))
    json.dump(normalized, sys.stdout, indent=2)


if __name__ == '__main__':
  main(sys.argv)
