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

_DSPL_BILLION_LAUGHS = (
    """<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
 <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
 <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
 <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
 <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
 <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<dspl xmlns="http://schemas.google.com/dspl/2010">
  <info>
    <name>
      <value>&lol9;</value>
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
    self.assertTrue(
        re.search('XML declaration allowed only.*line 1', result, flags=re.DOTALL))

    xml_error_input_file.close()

  def testXMLValidationSchemaError(self):
    """A simple end-to-end test of the non-conforming XML case."""
    schema_error_input_file = StringIO.StringIO(_DSPL_CONTENT_SCHEMA_ERROR)

    result = xml_validation.RunValidation(schema_error_input_file)
    # TODO: this validation failure has lineno 0; look into why lxml is not
    #       returning the right location.
    self.assertTrue(re.search('The attribute \'illegalproperty\' is not allowed',
                              result, flags=re.DOTALL))

    schema_error_input_file.close()

  def testXMLBillionLaughsAttack(self):
    """A simple test to verify that the validation routine is not susceptible
    to the billion laughs attack.
    """
    billion_laughs_input_file = StringIO.StringIO(_DSPL_BILLION_LAUGHS)
    result = xml_validation.RunValidation(billion_laughs_input_file)
    self.assertTrue(re.search('Detected an entity reference loop', result))

    billion_laughs_input_file.close()


if __name__ == '__main__':
  unittest.main()
