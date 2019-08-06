#!/usr/bin/env python3
# Copyright 2019 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd
import pandas as pd


# Read the input file.
df = pd.read_csv('http://dd.eionet.europa.eu/vocabulary/eurostat/metroreg/csv')

# Drop irrelevant columns
df = df[['Notation', 'Label']]

# Rename columns
df.columns = ['codeValue', 'name']

# Write output file
df.to_csv('metroreg.csv', index=False)
