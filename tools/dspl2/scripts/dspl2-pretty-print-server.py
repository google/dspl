#!/bin/env python3
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from flask import Flask, request, render_template
import json
from pathlib import Path
import requests

import dspl2
from dspl2 import (
    Dspl2JsonLdExpander, Dspl2RdfExpander, InternetFileGetter,
    JsonToKwArgsDict, LoadGraph, FrameGraph, UploadedFileGetter)


def _Display(template, json_val):
  return render_template(template, **JsonToKwArgsDict(json_val))


template_dir = Path(dspl2.__file__).parent / 'templates'
app = Flask('dspl2-viewer', template_folder=template_dir.as_posix())

@app.route('/')
def Root():
  return render_template('choose.html')


@app.route('/render', methods=['GET', 'POST'])
def _HandleUploads():
  try:
    rdf = request.args.get('rdf') == 'on'
    url = request.args.get('url')
    if request.method == 'POST':
      files = request.files.getlist('files[]')
      getter = UploadedFileGetter(files)
    else:
      if not url:
        return render_template('error.html',
                               message="No URL provided")
      getter = InternetFileGetter(url)
    if rdf:
      graph = Dspl2RdfExpander(getter).Expand()
      json_val = FrameGraph(graph)
    else:
      json_val = Dspl2JsonLdExpander(getter).Expand()
    return _Display('display.html', json_val)
  except json.JSONDecodeError as e:
    return render_template('error.html',
                           action="decoding",
                           url=e.doc or url,
                           text=str(e))
  except IOError as e:
    return render_template('error.html',
                           action="loading",
                           url=e.filename,
                           text=str(e))
  except RuntimeError as e:
    return render_template('error.html',
                           text=str(e))
  except requests.exceptions.HTTPError as e:
    return render_template('error.html',
                           url=url,
                           action="retrieving",
                           status=e.response.status_code,
                           text=e.response.text)
  except requests.exceptions.RequestException as e:
    return render_template('error.html',
                           url=url,
                           action="retrieving",
                           text=str(e))
  except Exception as e:
    return render_template('error.html',
                           action="processing",
                           url=url,
                           text=str(type(e)) + str(e))


if __name__ == '__main__':
    app.run()
