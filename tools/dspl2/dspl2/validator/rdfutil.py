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

FLAGS = flags.FLAGS
flags.DEFINE_string('schema',
                    (_Module_path / 'schema' / 'schema.jsonld').as_posix(),
                    'Path to schema.org schema')
flags.DEFINE_string('context',
                    (_Module_path / 'schema' / 'jsonldcontext.json').as_posix(),
                    'Path to schema.org context')

_initialized = False


def Init():
  global _Context, _Schema
  print('Loading schema', file=sys.stderr)
  with open(FLAGS.schema) as schema:
    _Schema.update(json.load(schema))
  print('Loading context', file=sys.stderr)
  with open(FLAGS.context) as context:
    _Context.update(json.load(context))
  del _Context['@context']['id']
  del _Context['@context']['type']
  initialized = True


def NormalizeJsonLd(json_val):
  if not _initialized:
    Init()
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


def main(args):
  with open(args[1]) as f:
    json_val = json.load(f)
  normalized = NormalizeJsonLd(json_val)
  print(json.dumps(normalized, indent=2))


if __name__ == '__main__':
  main(sys.argv)
