#!/usr/bin/python2.4
#
# Copyright 2011, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Tests of dsplgen module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import os
import os.path
import shutil
import tempfile
import unittest

import dsplgen


_TEST_CSV_CONTENT = (
"""date[type=date;format=yyyy-MM-dd],category1,category2[concept=geo:us_state;rollup=true],metric1[extends=quantity:ratio;slice_role=metric],metric2,metric3
1980-01-01,red,california,89,321,71.21
1981-01-01,red,california,99,231,391.2
1982-01-01,blue,maine's,293,32,2.31
1983-01-01,blue,california,293,12,10.3
1984-01-01,red,maine's,932,48,10.78""")


class DSPLGenTests(unittest.TestCase):
  """Test cases for dsplgen module."""

  def setUp(self):
    input_file_params = tempfile.mkstemp()

    self.input_file = os.fdopen(input_file_params[0], 'w')
    self.input_file_path = input_file_params[1]

    self.input_file.write(_TEST_CSV_CONTENT)
    self.input_file.close()

    self.output_dir = tempfile.mkdtemp()

  def tearDown(self):
    os.remove(self.input_file_path)
    shutil.rmtree(self.output_dir)

  def testDSPLGenEndToEnd(self):
    """A simple end-to-end test of the dsplgen application."""
    dsplgen.main(['-o', self.output_dir, '-q', self.input_file_path])

    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'dataset.xml')))
    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'category1_table.csv')))
    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'slice_0_table.csv')))
    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'slice_1_table.csv')))


if __name__ == '__main__':
  unittest.main()
