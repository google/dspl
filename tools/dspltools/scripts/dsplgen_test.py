#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Tests of dsplgen module."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import os
import os.path
import re
import shutil
import StringIO
import sys
import tempfile
import unittest

import dsplcheck
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
    self.input_dir = tempfile.mkdtemp()

    input_file = open(os.path.join(self.input_dir, 'input.csv'), 'w')
    input_file.write(_TEST_CSV_CONTENT)
    input_file.close()

    self.output_dir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.input_dir)
    shutil.rmtree(self.output_dir)

  def testDSPLGenEndToEnd(self):
    """A simple end-to-end test of the dsplgen application."""
    dsplgen.main(['-o', self.output_dir, '-q',
                  os.path.join(self.input_dir, 'input.csv')])

    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'dataset.xml')))
    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'category1_table.csv')))
    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'slice_0_table.csv')))
    self.assertTrue(
        os.path.isfile(os.path.join(self.output_dir, 'slice_1_table.csv')))

    # Test that output validates against dsplcheck
    saved_stdout = sys.stdout

    redirected_output = StringIO.StringIO()
    sys.stdout = redirected_output

    dsplcheck.main([os.path.join(self.output_dir, 'dataset.xml')])

    self.assertTrue(
        re.search(
            'validates successfully.*Parsing completed.*'
            'No issues found.*Completed',
            redirected_output.getvalue(), re.DOTALL))

    redirected_output.close()

    sys.stdout = saved_stdout

  def testCSVNotFound(self):
    """Test case in which CSV can't be opened."""
    dsplgen.main(['-o', self.output_dir, '-q',
                  os.path.join(self.input_dir, 'input.csv')])

    saved_stdout = sys.stdout
    redirected_output = StringIO.StringIO()
    sys.stdout = redirected_output

    self.assertRaises(SystemExit,
                      dsplgen.main, ['-q', 'non_existent_input_file.csv'])
    self.assertTrue('Error opening CSV file' in redirected_output.getvalue())

    redirected_output.close()
    sys.stdout = saved_stdout


if __name__ == '__main__':
  unittest.main()
