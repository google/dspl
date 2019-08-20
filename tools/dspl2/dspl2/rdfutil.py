# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from absl import flags
from pathlib import Path
from pyld import jsonld
import simplejson as json
import sys

_Schema = {}
_Context = {}
_Frame = {
    '@context': [_Context, {'schema': 'http://schema.org/'}],
    '@type': 'StatisticalDataset',
}
_Module_path = Path(__file__).parent
_initialized = False


def _Init(context, schema):
  global _Context, _Schema
  print(f'Loading schema from "{schema}"', file=sys.stderr)
  with open(schema) as schema:
    _Schema.update(json.load(schema))
  print(f'Loading context from "{context}"', file=sys.stderr)
  with open(context) as context:
    _Context.update(json.load(context))
  del _Context['@context']['id']
  del _Context['@context']['type']
  initialized = True


def NormalizeJsonLd(json_val):
  if not _initialized:
    _Init(
       (_Module_path / 'schema' / 'jsonldcontext.json').as_posix(),
       (_Module_path / 'schema' / 'schema.jsonld').as_posix(),
    )
  print('Expanding JSON-LD')
  expanded = jsonld.expand(json_val)
  print('Flattening JSON-LD')
  flattened = jsonld.flatten(expanded)
  print('Framing JSON-LD')
  framed = jsonld.frame(flattened, _Frame)
  framed['@context'] = 'http://schema.org'
  framed.update(framed['@graph'][0])
  del framed['@graph']
  return framed


def main(args, context, schema):
  with open(args[1]) as f:
    json_val = json.load(f)
  normalized = NormalizeJsonLd(json_val)
  json.dump(normalized, sys.stdout, indent=2)


if __name__ == '__main__':
  main(sys.argv)
