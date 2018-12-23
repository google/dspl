#!/usr/bin/python2
#
# Copyright 2018 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Generate a DSPL dataset from a tabular data source via the command-line."""
from __future__ import print_function


__author__ = 'Benjamin Yolken <yolken@google.com>'

import optparse
import sys
import time

from dspllib.data_sources import csv_data_source
from dspllib.data_sources import csv_data_source_sqlite
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
                    choices=['csv', 'csv_sqlite'], default='csv',
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
  if options['data_type'] in ['csv', 'csv_sqlite']:
    try:
      csv_file = open(options['data_source'], 'r')
    except IOError as io_error:
      print('Error opening CSV file\n\n%s' % io_error)
      sys.exit(2)

    if options['data_type'] == 'csv':
      data_source_obj = csv_data_source.CSVDataSource(
          csv_file, options['verbose'])
    else:
      data_source_obj = csv_data_source_sqlite.CSVDataSourceSqlite(
          csv_file, options['verbose'])
  else:
    print('Error: Unknown data type: %s' % (options['data_type']))
    sys.exit(2)

  # Create DSPL dataset from data source
  dataset = data_source_to_dspl.PopulateDataset(
      data_source_obj, options['verbose'])
  data_source_obj.Close()

  if options['verbose']:
    print('Materializing dataset:')
    print(str(dataset))

  # Write DSPL dataset to disk
  dataset.Materialize(options['output_path'])

  if options['verbose']:
    print('Completed in %0.2f seconds' % (time.time() - start_time))


if __name__ == '__main__':
  main(sys.argv[1:])
