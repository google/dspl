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

"""Validate a DSPL XML file."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import os.path
import re
import xml.parsers.expat
import xml.etree.ElementTree

from genxmlif import GenXmlIfError
from minixsv import pyxsval

# The number of lines of context to show around XML errors
_CONTEXT_LINES = 3

_DEFAULT_SCHEMA_PATH = os.path.join(
    os.path.split(__file__)[0], 'schemas', 'dspl.xsd')


def GetErrorContext(xml_string, error_line_number):
  """Generate a string that shows the context of an XML error.

  Args:
    xml_string: String containing the contents of an XML file
    error_line_number: 1-indexed line number on which error has been detected

  Returns:
    A pretty-printed string containing the lines around the error
  """
  min_error_start_line = (error_line_number - 1) - _CONTEXT_LINES
  max_error_end_line = (error_line_number - 1) + _CONTEXT_LINES

  error_context_lines = []

  for l, line in enumerate(xml_string.splitlines()):
    if l >= min_error_start_line:
      line_string = '%5d' % (l + 1)

      # Highlight the error line with asterisks
      if (l + 1) == error_line_number:
        line_string = line_string.replace(' ', '*')

      error_context_lines.append('%s: %s' % (line_string, line.rstrip()))

      if l >= max_error_end_line:
        break

  return '\n'.join(error_context_lines)


def GetErrorLineNumber(error_string):
  """Parse out the line number from a minixsv error message.

  Args:
    error_string: String returned by minixsv exception

  Returns:
    Integer line number on which error was detected
  """
  line_match = re.search(': line ([0-9]+)', error_string)

  return int(line_match.group(1))


def RunValidation(xml_file, schema_file=None, verbose=True):
  """Run the validation process and return a message with the result.

  Args:
    xml_file: An XML input file
    schema_file: A DSPL schema file; if not given, the default 'dspl.xsd' is
                 used.
    verbose: Include helpful, extra information about validation

  Returns:
    String containing result of validation process
  """
  result = ''

  xml_file_text = xml_file.read()

  if schema_file:
    schema_file_text = schema_file.read()
  else:
    schema_file = open(_DEFAULT_SCHEMA_PATH, 'r')
    schema_file_text = schema_file.read()
    schema_file.close()

  # Figure out which type of parsing exception this version of ElementTree
  # throws; code adapted from example in ElementTree documentation
  try:
    parse_error = xml.etree.ElementTree.ParseError
  except AttributeError:
    try:
      xml.etree.ElementTree.XML('<foo>')
    except:
      from sys import exc_type as parse_error

  try:
    pyxsval.parseAndValidateXmlInputString(
        xml_file_text, xsdText=schema_file_text,
        xmlIfClass=pyxsval.XMLIF_ELEMENTTREE,
        warningProc=pyxsval.PRINT_WARNINGS)

  except (GenXmlIfError, parse_error) as xml_error:
    # XML parsing error
    error_string = str(xml_error)

    if verbose:
      result = ('Input is not valid XML\n\n%s\n%s' %
                (error_string, GetErrorContext(
                    xml_file_text,
                    GetErrorLineNumber(error_string))))
    else:
      result = error_string
  except pyxsval.XsvalError as schema_error:
    # Schema validation error
    error_string = str(schema_error)

    if verbose:
      result = ('Input does not validate against DSPL schema\n\n%s\n%s' %
                (error_string, GetErrorContext(
                    xml_file_text,
                    GetErrorLineNumber(error_string))))
    else:
      result = error_string
  else:
    if verbose:
      result = 'XML file validates successfully!'

  return result
