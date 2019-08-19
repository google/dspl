# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import extruct
from io import StringIO
from pathlib import Path
import requests
import simplejson as json
from urllib.parse import urljoin, urlparse

from dspl2.validator.rdfutil import NormalizeJsonLd


def _ProcessDspl2File(filename, file, *, type=''):
  if filename.endswith('.html') or type.startswith('text/html'):
    data = extruct.extract(file.read(), uniform='True')
    return NormalizeJsonLd({
        '@context': 'http://schema.org',
        '@graph': [
            subdata_elem
            for subdata in data.values()
            for subdata_elem in subdata
            if subdata
        ]
    })
  if filename.endswith('.json') or filename.endswith('.jsonld') or type.startswith('application/ld+json'):
    return json.load(file)


class UploadedFileGetter(object):
  def __init__(self, files):
    json_files = set()
    self.json = None
    self.file_map = {}
    for f in files:
      self.file_map[f.filename] = f
      data = _ProcessDspl2File(f.filename, f.stream)
      if data:
        json_files.add(f.filename)
        self.base = f.filename
        self.json = data
    if not self.json:
      raise RuntimeError("DSPL 2 file not present in {}".format(
          [file.filename for file in self.file_map.values()]))
    if len(json_files) > 1:
      raise RuntimeError("Multiple DSPL 2 files present: {}".format(json_files))

  def Fetch(self, filename):
    f = self.file_map.get(filename)
    if not f:
      raise IOError(None, 'File not found', filename)
    f.stream.seek(0)
    return StringIO(f.read().decode('utf-8'))


class InternetFileGetter(object):
  def __init__(self, url):
    self.base = url
    r = requests.get(self.base)
    r.raise_for_status()
    self.json = _ProcessDspl2File(url, StringIO(r.text), type=r.headers['content-type'])

  def Fetch(self, filename):
    r = requests.get(urljoin(self.base, filename))
    r.raise_for_status()
    return StringIO(r.text)


class LocalFileGetter(object):
  def __init__(self, path):
    self.base = path
    with Path(path).open() as f:
      self.json = _ProcessDspl2File(path, f)

  def Fetch(self, filename):
    path = Path(self.base).parent.joinpath(Path(filename)).resolve()
    return path.open()


class HybridFileGetter(object):
  @staticmethod
  def _load_file(base, rel=None):
    uri = urlparse(base)
    if rel:
      uri = urljoin(base, rel)
    if not uri.scheme or uri.scheme == 'file':
      return Path(uri.path).open()
    elif uri.scheme == 'http' or uri.scheme == 'https':
      r = requests.get(uri)
      r.raise_for_status()
      return StringIO(r.text)

  def __init__(self, json_uri):
    self.base = json_uri
    self.json = _ProcessDspl2File(
        json_uri,
        json.load(HybridFileGetter._load_file(json_uri)))

  def Fetch(self, uri):
    return HybridFileGetter._load_file(self.base, uri)
