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

"""Generate a DSPL dataset from a tabular data source via the command-line."""


__author__ = 'Benjamin Yolken <yolken@google.com>'

import optparse
import sys
import time

from dspllib.data_sources import csv_data_source
from dspllib.data_sources import data_source_to_dspl


def LoadOptionsFromFlags(argv):
  """Parse command-line arguments.

  Args:
    argv: The program argument vector (excluding the script name)

  Returns:
    A dictionary with key-value pairs for each of the options
  """
  usage_string = 'python dsplgen.py [options] [csv file]'

  parser = optparse.OptionParser(usage=usage_string)
  parser.set_defaults(verbose=True)
  parser.add_option('-o', '--output_path', dest='output_path', default='',
                    help=('Path to a output directory '
                          '(default: current directory)'))
  parser.add_option('-q', '--quiet',
                    action='store_false', dest='verbose',
                    help='Quiet mode')
  parser.add_option('-t', '--data_type', dest='data_type', type='choice',
                    choices=['csv'], default='csv',
                    help='Type of data source to use (default: csv)')

  (options, args) = parser.parse_args(args=argv)

  if not len(args) == 1:
    parser.error('A data source (e.g., path to CSV file) is required')

  return {'data_type': options.data_type,
          'data_source': args[0],
          'output_path': options.output_path,
          'verbose': options.verbose}


def main(argv):
  """Parse command-line flags and run data source to DSPL conversion process.

  Args:
    argv: The program argument vector (excluding the script name)
  """
  start_time = time.time()
  options = LoadOptionsFromFlags(argv)

  # Connect to data source
  if options['data_type'] == 'csv':
    data_source_obj = csv_data_source.CSVDataSource(
        open(options['data_source'], 'r'), options['verbose'])
  else:
    print 'Error: Unknown data type: %s' % (options['data_type'])
    sys.exit(2)

  # Create DSPL dataset from data source
  dataset = data_source_to_dspl.PopulateDataset(
      data_source_obj, options['verbose'])
  data_source_obj.Close()

  if options['verbose']:
    print 'Materializing dataset:'
    print str(dataset)

  # Write DSPL dataset to disk
  dataset.Materialize(options['output_path'])

  if options['verbose']:
    print 'Completed in %0.2f seconds' % (time.time() - start_time)


if __name__ == '__main__':
  main(sys.argv[1:])
