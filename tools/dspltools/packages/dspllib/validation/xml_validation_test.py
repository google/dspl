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

"""Tests of xml_validation module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import re
import StringIO
import unittest

import xml_validation


_DSPL_CONTENT_VALID = (
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


_DSPL_CONTENT_XML_ERROR = (
"""   <?xml version="1.0" encoding="UTF-8"?>
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


_DSPL_CONTENT_SCHEMA_ERROR = (
"""<?xml version="1.0" encoding="UTF-8"?>
<dspl xmlns="http://schemas.google.com/dspl/2010"
    xmlns:time="http://www.google.com/publicdata/dataset/google/time">
  <import namespace="http://www.google.com/publicdata/dataset/google/time"/>
  <info>
    <name illegalproperty="illegalvalue">
      <value>Dataset Name</value>
    </name>
  </info>
  <provider>
    <name>
      <value>Provider Name</value>
    </name>
  </provider>
</dspl>""")


class XMLValidationTests(unittest.TestCase):
  """Test case for xml_validation module."""

  def setUp(self):
    pass

  def testXMLValidationGoodXML(self):
    """A simple end-to-end test of the valid XML case."""
    valid_input_file = StringIO.StringIO(_DSPL_CONTENT_VALID)

    result = xml_validation.RunValidation(valid_input_file)
    self.assertTrue(re.search('validates successfully', result))

    valid_input_file.close()

  def testXMLValidationXMLError(self):
    """A simple end-to-end test of the bad XML case."""
    xml_error_input_file = StringIO.StringIO(_DSPL_CONTENT_XML_ERROR)

    result = xml_validation.RunValidation(xml_error_input_file)
    self.assertTrue(re.search('not valid XML.*line 1', result, flags=re.DOTALL))

    xml_error_input_file.close()

  def testXMLValidationSchemaError(self):
    """A simple end-to-end test of the non-conforming XML case."""
    schema_error_input_file = StringIO.StringIO(_DSPL_CONTENT_SCHEMA_ERROR)

    result = xml_validation.RunValidation(schema_error_input_file)
    self.assertTrue(re.search('does not validate against DSPL schema.*line 6',
                              result, flags=re.DOTALL))

    schema_error_input_file.close()


if __name__ == '__main__':
  unittest.main()
