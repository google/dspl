# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from absl import app
from absl import flags
import dspl2
import jinja2
from pathlib import Path
import sys


FLAGS = flags.FLAGS
flags.DEFINE_boolean('rdf', False, 'Process the JSON-LD as RDF.')


def _RenderLocalDspl2(path, rdf):
  template_dir = Path(dspl2.__file__).parent / 'templates'
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(
      template_dir.as_posix()))
  try:
    print("Loading template")
    template = env.get_template('display.html')
    print("Loading DSPL2")
    getter = dspl2.LocalFileGetter(path)
    print("Expanding DSPL2")
    if rdf:
      graph = dspl2.Dspl2RdfExpander(getter).Expand()
      print("Framing DSPL2")
      json_val = dspl2.FrameGraph(graph)
    else:
      json_val = dspl2.Dspl2JsonLdExpander(getter).Expand()
    print("Rendering template")
    return template.render(**dspl2.JsonToKwArgsDict(json_val))
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
    print(_RenderLocalDspl2(argv[1], FLAGS.rdf), file=f)


if __name__ == '__main__':
  app.run(main)
