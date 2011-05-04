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

"""Tests of dsplcheck module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import os
import re
import StringIO
import sys
import tempfile
import unittest

import dsplcheck


_DSPL_CONTENT = (
"""<?xml version="1.0" encoding="UTF-8"?>
<dspl xmlns="http://schemas.google.com/dspl/2010"
    xmlns:time="http://www.google.com/publicdata/dataset/google/time">
  <import namespace="http://www.google.com/publicdata/dataset/google/time"/>
  <info>
    <name>
      <value>Dataset Name</value>
    </name>
  </info>
  <provider>
    <name>
      <value>Provider Name</value>
    </name>
  </provider>
</dspl>""")


_DSPL_CONTENT_BAD_CSV_PATH = (
"""<?xml version="1.0" encoding="UTF-8"?>
<dspl xmlns="http://schemas.google.com/dspl/2010"
    xmlns:time="http://www.google.com/publicdata/dataset/google/time">
  <import namespace="http://www.google.com/publicdata/dataset/google/time"/>
  <info>
    <name>
      <value>Dataset Name</value>
    </name>
  </info>
  <provider>
    <name>
      <value>Provider Name</value>
    </name>
  </provider>
  <tables>
    <table id="my_table">
      <column id="col1" type="string"/>
      <column id="col2" type="string"/>
      <data>
        <file format="csv" encoding="utf-8">non_existent_file.csv</file>
      </data>
    </table>
  </tables>
</dspl>""")


class DSPLCheckTests(unittest.TestCase):
  """Test case for dsplcheck module."""

  def setUp(self):
    valid_dspl_file_params = tempfile.mkstemp()

    self.valid_dspl_file = os.fdopen(valid_dspl_file_params[0], 'w')
    self.valid_dspl_file_path = valid_dspl_file_params[1]
    self.valid_dspl_file.write(_DSPL_CONTENT)
    self.valid_dspl_file.close()

    bad_csv_dspl_file_params = tempfile.mkstemp()

    self.bad_csv_dspl_file = os.fdopen(bad_csv_dspl_file_params[0], 'w')
    self.bad_csv_dspl_file_path = bad_csv_dspl_file_params[1]
    self.bad_csv_dspl_file.write(_DSPL_CONTENT_BAD_CSV_PATH)
    self.bad_csv_dspl_file.close()

  def tearDown(self):
    os.remove(self.valid_dspl_file_path)
    os.remove(self.bad_csv_dspl_file_path)

  def testValidDataset(self):
    """Test basic case of dataset that validates and parses correctly."""
    self._StdoutTestHelper(
        dsplcheck.main, [self.valid_dspl_file_path],
        'validates successfully.*Parsing completed.*Done')

  def testBadXMLFilePath(self):
    """Test case where bad XML file path is passed in."""
    self._StdoutTestHelper(
        dsplcheck.main, ['nonexistent_input_file.xml'],
        'Error opening XML file', expect_exit=True)

  def testBadCSVFilePath(self):
    """Test case where DSPL file has bad CSV reference."""
    self._StdoutTestHelper(
        dsplcheck.main, [self.bad_csv_dspl_file_path],
        'Error while trying to parse', expect_exit=True)

  def _StdoutTestHelper(self, function, args,
                        expected_output, expect_exit=False):
    """Check the stdout output of a function against its expected value.

    Args:
      function: A function to execute
      args: The arguments to pass to the function
      expected_output: A regular expression expected to match the stdout output
      expect_exit: Boolean indicating whether the function execution should
                   trigger a system exit
    """
    saved_stdout = sys.stdout

    redirected_output = StringIO.StringIO()
    sys.stdout = redirected_output

    if expect_exit:
      self.assertRaises(SystemExit, function, args)
    else:
      function(args)

    self.assertTrue(
        re.search(expected_output, redirected_output.getvalue(), re.DOTALL))

    redirected_output.close()
    sys.stdout = saved_stdout


if __name__ == '__main__':
  unittest.main()
