#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

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
