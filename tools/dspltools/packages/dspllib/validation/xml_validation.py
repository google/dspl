#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Validate a DSPL XML file."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

from lxml import etree
import os.path
import re


# The number of lines of context to show around XML errors
_CONTEXT_LINES = 3

_SCHEMA_PATH = os.path.join(os.path.split(__file__)[0], 'schemas')
_DSPL_SCHEMA_FILE = 'dspl.xsd'


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
    schema_file = open(os.path.join(_SCHEMA_PATH, _DSPL_SCHEMA_FILE), 'r')
    schema_file_text = schema_file.read()
    schema_file.close()

  # Insert proper paths into XSD schemaLocation tags
  substitution_function = (
      lambda m: 'schemaLocation="%s"' % os.path.join(_SCHEMA_PATH, m.group(1)))

  schema_file_text = re.sub(
      'schemaLocation="([a-zA-Z_0-9.]+)"',
      substitution_function,
      schema_file_text, 2)

  # Parse the schema file into an etree
  schema_file_xml = etree.XML(schema_file_text)

  try:
    schema = etree.XMLSchema(schema_file_xml)
    parser = etree.XMLParser(schema=schema)
    etree.fromstring(xml_file_text, parser)
  except etree.XMLSyntaxError as xml_error:
    # XML parsing error
    error_string = str(xml_error)
    if verbose:
      result = ('Input does not validate against DSPL schema\n\n%s\n%s' %
                (error_string, GetErrorContext(
                    xml_file_text,
                    xml_error.lineno)))
    else:
      result = error_string
  else:
    if verbose:
      result = 'XML file validates successfully!'

  return result
