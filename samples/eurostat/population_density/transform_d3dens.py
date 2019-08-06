#!/usr/bin/env python3
# Copyright 2019 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd
import pandas as pd


# Read the file and set the index column to the metro region.
df = pd.read_csv(
    'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/met_d3dens.tsv.gz',
    delimiter='\t',
    index_col='metroreg\\time')

# Stack the column headers into a single column's values, and make the metro
# region a column again.
df = df.stack().reset_index()

# Rename the columns
df.columns = ['metroreg', 'year', 'density']

# Strip surrounding whitespace from each value
for col in df.columns:
  df[col] = df[col].str.strip()

# Indicate that the year is an integer
df['year'] = df['year'].astype(int)

# Add a string-valued footnote column with default empty string.
df['density*'] = ''

# Split up any values with footnotes between the value and footnote columns
for idx, density in df.loc[df['density'].str.contains(' '),
                           'density'].iteritems():
  density, footnote = density.split(' ')
  df.loc[idx, 'density'] = density
  df.loc[idx, 'density*'] = ';'.join(list(footnote))

# Remove the placeholder value of ':'
df.loc[df['density'] == ':', 'density'] = None

# Remove rows with no density
df = df[pd.notnull(df['density'])]

# And write the results to a CSV file.
df.to_csv('met_d3dens.csv', index=False)
