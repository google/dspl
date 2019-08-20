# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from absl import app
from absl import flags
import jinja2
from pathlib import Path
import sys

import dspl2.validator
from dspl2.validator.expander import ExpandStatisticalDataset
from dspl2.validator.filegetter import *
from dspl2.validator.jsonutil import JsonToKwArgsDict
from dspl2.validator.rdfutil import NormalizeJsonLd


FLAGS = flags.FLAGS
flags.DEFINE_boolean('normalize', False,
                     'Normalize the JSON-LD before processing.')


def RenderLocalDspl2(path, normalize):
  template_dir = Path(dspl2.validator.__file__).parent / 'templates'
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(
      template_dir.as_posix()))
  try:
    print("Loading template")
    template = env.get_template('display.html')
    getter = LocalFileGetter(path)
    json_val = ExpandStatisticalDataset(getter)
    if normalize:
      json_val = NormalizeJsonLd(json_val)
    print("Rendering template")
    return template.render(**JsonToKwArgsDict(json_val))
  except Exception as e:
    raise
    template = loader.load(env, 'error.html')
    return template.render(action="processing",
                           url=path,
                           text=str(type(e)) + ": " + str(e))


def main(argv):
  if len(argv) != 3:
    print(f'Usage: {argv[0]} [input.json] [output.html]', file=sys.stderr)
    exit(1)
  with open(argv[2], 'w') as f:
    print(RenderLocalDspl2(argv[1], FLAGS.normalize), file=f)


if __name__ == '__main__':
  app.run(main)
